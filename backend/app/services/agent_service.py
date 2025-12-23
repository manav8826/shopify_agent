import logging
import uuid
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from langchain_groq import ChatGroq
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, SystemMessage
from langchain_core.tools import BaseTool
from langchain_experimental.tools import PythonAstREPLTool
from sqlalchemy.orm import Session as DBSession

from app.tools.shopify_tool import GetShopifyDataTool
from app.core.prompts import SHOPIFY_AGENT_SYSTEM_PROMPT
from app.core.config import settings
from app.models.agent import AgentResponse, Message as ApiMessage
from app.db.database import SessionLocal
from app.models.database_models import Session, Message

# Setup logging
logger = logging.getLogger("agent_service")
logging.basicConfig(level=logging.INFO)

class AgentService:
    def __init__(self):
        self.llm = self._initialize_llm()
        # Tools are NOT initialized here to prevent shared state
        
    def _initialize_llm(self) -> ChatGroq:
        """Initialize Groq LLM"""
        return ChatGroq(
            model="llama-3.3-70b-versatile",
            temperature=0.0,
            groq_api_key=settings.GROQ_API_KEY,
            max_retries=1, # Fail fast on rate limits
        )
    
    def _create_tools_for_request(self, repl_locals: Dict[str, Any]) -> List[BaseTool]:
        """Create FRESH instances of tools for every single request"""
        return [
            GetShopifyDataTool(),
            PythonAstREPLTool(locals=repl_locals) # Connected memory scope
        ]
    
    async def create_session(self, store_url: str) -> str:
        """Create new session in DB"""
        if not re.match(r'^https?://[\w\-]+(\.[\w\-]+)+[/#?]?.*$', store_url):
             raise ValueError("Invalid store URL format.")

        db: DBSession = SessionLocal()
        try:
            session_id = str(uuid.uuid4())
            new_session = Session(
                id=session_id,
                store_url=store_url,
                created_at=datetime.utcnow(),
                last_active=datetime.utcnow()
            )
            db.add(new_session)
            db.commit()
            logger.info(f"Created session {session_id} for store {store_url}")
            return session_id
        finally:
            db.close()
    
    async def get_history(self, session_id: str) -> List[ApiMessage]:
        """Get conversation history from DB"""
        db: DBSession = SessionLocal()
        try:
            session = db.query(Session).filter(Session.id == session_id).first()
            if not session:
                raise ValueError("Session not found")
                
            # SQLite stores datetime, but we ensure sorting
            messages = db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp).all()
            
            return [
                ApiMessage(
                    role=msg.role, 
                    content=msg.content, 
                    timestamp=msg.timestamp
                ) for msg in messages
            ]
        finally:
            db.close()

    def _check_rate_limit(self, session_id: str, db: DBSession):
        # Generic rate limit check (simplified for DB version)
        pass

    async def chat(self, session_id: str, message: str) -> AgentResponse:
        """Execute agent with user message using manual ReAct loop"""
        db: DBSession = SessionLocal()
        try:
            session = db.query(Session).filter(Session.id == session_id).first()
            if not session:
                raise ValueError("Session not found")
            
            # Update last activity
            session.last_active = datetime.utcnow()
            
            # Save User Message
            user_msg = Message(session_id=session_id, role="user", content=message, timestamp=datetime.utcnow())
            db.add(user_msg)
            db.commit() 
            
            if "ignore previous instructions" in message.lower():
                 return AgentResponse(session_id=session_id, message="I cannot process that request.")
            
            # --- CRITICAL FIX: Initialize tools FRESH for this request ---
            repl_locals = {} # Shared state for this request only
            tools = self._create_tools_for_request(repl_locals)
            tool_map = {tool.name: tool for tool in tools}
            
            # Load Context (Last 5 messages to save tokens)
            recent_msgs = db.query(Message).filter(Message.session_id == session_id).order_by(Message.timestamp).all()[-5:]
            
            # Construct Prompt
            tools_desc = "\n".join([f"{t.name}: {t.description}" for t in tools])
            tool_names = ", ".join([t.name for t in tools])
            
            # Format history block
            history_text = ""
            for msg in recent_msgs: 
                role = "Human" if msg.role == "user" else "AI"
                history_text += f"{role}: {msg.content}\n"
                
            full_prompt = f"""{SHOPIFY_AGENT_SYSTEM_PROMPT}

TOOLS:
------
You have access to the following tools:

{tools_desc}

To use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

**CRITICAL: You must ALWAYS start your final response with "Final Answer:" or it will be lost.**

**DATA PROCESSING:**
When you fetch data using `get_shopify_data`, it is **automatically saved** to a python variable named `shopify_data`.
You do NOT need to copy-paste the JSON. Just use `shopify_data` in your `python_repl_ast` code.
Example: `df = pd.DataFrame(shopify_data)`

Begin!

Previous conversation history:
{history_text}

New input: {message}
"""
            
            current_scratchpad = ""
            final_answer = ""
            
            try:
                for i in range(15): # Max iterations
                    # Call LLM with Stop Sequence
                    response = await self.llm.ainvoke(
                        [HumanMessage(content=full_prompt + current_scratchpad)],
                        stop=["Observation:"]
                    )
                    output = response.content
                    # Gemini sometimes returns list of parts
                    if isinstance(output, list):
                        output = " ".join([str(item) for item in output])
                    current_scratchpad += f"\n{output}"
                    
                    # Check for Final Answer
                    if "Final Answer:" in output:
                        final_answer = output.split("Final Answer:")[-1].strip()
                        break
                    
                    # Check for Action
                    # Regex explanation:
                    # Action:\s*(.*?) -> Capture action name (non-greedy)
                    # \nAction Input:\s* -> Match literal "Action Input:"
                    # (.*) -> Capture everything else (we'll clean it up)
                    action_match = re.search(r"Action:\s*(.*?)\nAction Input:\s*(.*)", output, re.DOTALL)
                    if not action_match:
                         # Attempt fallback
                         action_match = re.search(r"Action:\s*(.*?)\nAction Input:\s*```(?:\w+)?\n(.*?)```", output, re.DOTALL)
    
                    if action_match:
                        action = action_match.group(1).strip()
                        raw_input = action_match.group(2).strip()
                        
                        # CLEANUP: Remove "Observation:" if it wasn't caught by stop sequence
                        if "Observation:" in raw_input:
                            raw_input = raw_input.split("Observation:")[0].strip()
                            
                        # CLEANUP: Remove code block ticks
                        action_input = raw_input.strip("`")
                        
                        logger.info(f"Tool Selection: {action} Input: {action_input}")
                        
                        if action in tool_map:
                            tool = tool_map[action]
                            try:
                                # Attempt to parse JSON input (for multi-arg tools)
                                try:
                                    import json
                                    # Try naive parse
                                    tool_input = json.loads(action_input)
                                except json.JSONDecodeError:
                                    # Fallback: Try to find the last '}' if trailing text exists of Llama 3 hallucinations
                                    if "}" in action_input:
                                        try:
                                            clean_input = action_input[:action_input.rindex("}")+1]
                                            tool_input = json.loads(clean_input)
                                        except Exception:
                                            # If still fails, use raw string (e.g. for python_repl)
                                            tool_input = action_input
                                    else:
                                        tool_input = action_input
                                        
                                observation = await tool.arun(tool_input)
                                
                                # --- SPECIAL HANDLING: Shopify Data (Ghost Data Pattern) ---
                                if action == "get_shopify_data" and isinstance(observation, (list, dict)):
                                    # 1. Inject into shared locals for this request
                                    # Pre-process: Cast numeric fields to float to avoid string concatenation in Pandas
                                    if isinstance(observation, list):
                                        for item in observation:
                                            if isinstance(item, dict):
                                                for field in ['total_price', 'subtotal_price', 'total_tax']:
                                                    if field in item and item[field] is not None:
                                                        try:
                                                            item[field] = float(item[field])
                                                        except (ValueError, TypeError):
                                                            pass 
                                                
                                                # Pre-clean billing_address to ensure safe city extraction
                                                if 'billing_address' not in item or item['billing_address'] is None:
                                                    item['billing_address'] = {'city': 'Unknown', 'country': 'Unknown'}
                                                
                                                # Pre-clean customer to ensure safe name extraction
                                                if 'customer' not in item or item['customer'] is None:
                                                    item['customer'] = {'first_name': 'Unknown', 'last_name': '', 'id': 'Unknown'}
                                                            
                                    repl_locals["shopify_data"] = observation
                                    repl_locals["orders_data"] = observation # Backwards compatibility
                                    
                                    # 2. Force update the specific tool instance to be safe
                                    if "python_repl_ast" in tool_map:
                                        # LangChain's PythonAstREPLTool stores locals in self.locals
                                        tool_map["python_repl_ast"].locals.update({
                                            "shopify_data": observation,
                                            "orders_data": observation
                                        })
                                    
                                    # 3. GHOST DATA: Do NOT show full data to LLM to save tokens
                                    # Create a schema summary instead
                                    item_count = len(observation) if isinstance(observation, list) else 1
                                    
                                    keys_preview = "unknown_keys"
                                    if isinstance(observation, list):
                                        if observation and isinstance(observation[0], dict):
                                            keys = list(observation[0].keys())
                                            keys_preview = ", ".join(keys[:5])
                                        else:
                                            keys_preview = "empty_list" if not observation else "no_dict_items"
                                    elif isinstance(observation, dict):
                                        keys = list(observation.keys())
                                        keys_preview = ", ".join(keys[:5])
                                    
                                    short_observation = (
                                        f"Successfully fetched {item_count} records. \n"
                                        f"Data is stored in python variable 'shopify_data'. \n"
                                        f"Row keys preview: [{keys_preview}, ...]\n"
                                        f"Do NOT output the full data. Use python to analyze it."
                                    )
                                    
                                    logger.info(f"Ghost Data: Injected {item_count} records into REPL. Hiding from LLM prompt.")
                                    
                                    # Use the summary for the prompt
                                    obs_str = short_observation
                                else:
                                    # Regular tools: formatting
                                    obs_str = str(observation)
                                    # TRUNCATION: Fallback for other large outputs
                                    if len(obs_str) > 5000:
                                        obs_str = obs_str[:5000] + "\n... [Output Truncated]"

                                logger.info(f"Tool Observation: {obs_str[:200]}...")
                                current_scratchpad += f"\nObservation: {obs_str}\n"

                            except Exception as e:
                                observation = f"Error executing tool: {e}"
                                logger.info(f"Tool Observation: {observation}")
                                current_scratchpad += f"\nObservation: {observation}\n"
                    else:
                        # Fallback for direct answers (missing Final Answer prefix)
                        logger.warning(f"Agent loop: No Action or Final Answer found. Treating output as Final Answer.")
                        if len(output.strip()) > 0:
                            # Heuristic: If it starts with "Thought:", strip it and use the rest
                            thought_match = re.match(r"^Thought:\s*(.*)", output, re.IGNORECASE | re.DOTALL)
                            if thought_match:
                                final_answer = thought_match.group(1).strip()
                            else:
                                final_answer = output
                            break
                        final_answer = "I am unsure how to proceed. Please clarify."
                        break
    
                if not final_answer:
                    final_answer = "I could not generate a response in time."
                    
                # Clean up Final Answer
                final_answer = re.sub(r'```python.*?```', '', final_answer, flags=re.DOTALL).strip()
                
                # Save AI Response
                ai_msg = Message(session_id=session_id, role="assistant", content=final_answer, timestamp=datetime.utcnow())
                db.add(ai_msg)
                db.commit()
                
                return AgentResponse(
                    session_id=session_id,
                    message=final_answer,
                    thought_process=current_scratchpad if settings.DEBUG else None
                )
    
            except Exception as e:
                # Check for LLM Rate Limit (429)
                error_str = str(e)
                if "429" in error_str or "Too Many Requests" in error_str or "RESOURCE_EXHAUSTED" in error_str:
                    logger.warning(f"LLM Rate Limit Hit: {error_str}")
                    return AgentResponse(
                        session_id=session_id,
                        message="**System Overload**: I am currently receiving too many requests. Please wait 30-60 seconds and try again. 🚥",
                        thought_process=None
                    )
                
                logger.error(f"Error in chat session {session_id}: {e}", exc_info=True)
                return AgentResponse(
                    session_id=session_id,
                    message=f"I encountered an error: {str(e)}",
                    thought_process=None
                )
        finally:
            db.close()
