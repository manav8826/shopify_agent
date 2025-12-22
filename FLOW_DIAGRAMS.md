# System Architecture & Workflows 📊

This specific document details the internal flows of the ShopifyAI Agent, highlighting the "Ghost Data" optimization pattern.

## 1. The "Ghost Data" Analysis Pipeline (Sequence)
This diagram illustrates the critical optimization where large datasets are injected directly into the Python REPL's memory, bypassing the LLM's token limit.

```mermaid
sequenceDiagram
    autonumber
    actor User
    participant API as FastAPI Backend
    participant Agent as ReAct Agent
    participant LLM as Groq/Gemini Model
    participant ST as Shopify Tool
    participant REPL as Python REPL
    participant S_API as Shopify Admin API

    User->>API: "Calculate summary of last 7 days orders"
    API->>Agent: Start Session
    
    loop Reasoning Loop
        Agent->>LLM: Prompt + History + Tools
        LLM-->>Agent: Action: get_shopify_data(last_7_days)
        
        Agent->>ST: Execute Tool
        ST->>S_API: GET /orders?created_at_min=...
        S_API-->>ST: Return 250+ Orders JSON
        
        Note over ST, REPL: CRITICAL OPTIMIZATION<br/>"Ghost Data" Injection
        ST->>REPL: Inject `shopify_data` variable directly
        ST-->>Agent: Return Summary ("Fetched 250 records. Data hidden.")
        
        Agent->>LLM: Observation: Fetched 250 records...
        
        Note left of LLM: LLM does NOT see the JSON.<br/>It writes code assuming variable exists.
        
        LLM-->>Agent: Action: python_repl_ast(code="df = pd.DataFrame(shopify_data)...")
        
        Agent->>REPL: Execute Code
        REPL->>REPL: Access `shopify_data` from memory
        REPL-->>Agent: Return Analysis Result (e.g., "$12,450.50")
        
        Agent->>LLM: Observation: "$12,450.50"
        LLM-->>Agent: Final Answer: "The total revenue is $12,450.50"
    end
    
    Agent-->>API: Response
    API-->>User: Display Response
```

## 2. Component Architecture (System)
How the modules interact within the Monorepo.

```mermaid
graph TD
    subgraph Frontend
        UI[React UI]
        Ch[Chat Component]
    end

    subgraph Backend
        API[FastAPI Router]
        DB[(SQLite Session DB)]
        
        subgraph "Agent Service"
            Mgr[Agent Manager]
            Mem[Memory/History]
            
            subgraph "Tools"
                T1[Shopify Tool]
                T2[Python REPL]
            end
            
            Inj[Variable Injector]
        end
    end
    
    subgraph External
        L[LLM (Groq/Gemini)]
        S[Shopify Store]
    end

    UI --> API
    API --> Mgr
    Mgr <--> DB
    Mgr <--> L
    Mgr --> T1
    Mgr --> T2
    
    T1 <--> S
    T1 --> Inj
    Inj -.->|Injects Data Context| T2
```
