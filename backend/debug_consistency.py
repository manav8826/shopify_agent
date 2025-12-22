import asyncio
import httpx
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

async def run_consistency_check():
    base_url = "http://127.0.0.1:8000/api"
    store_url = "https://clevrr-test.myshopify.com/"
    query = "How many orders did we get in the last 7 days?"
    
    print(f"--- Starting Consistency Check (HTTP) ---")
    
    responses = []
    
    async with httpx.AsyncClient(timeout=120.0) as client:
        with open("backend/consistency_report.txt", "w", encoding="utf-8") as f:
            f.write(f"--- Starting Consistency Check (HTTP) ---\n")
            f.flush()
            print(f"--- Starting Consistency Check (HTTP) ---")
            
            # Use the EXACT query from user screenshot
            query = "How many total orders do we have" # User's exact prompt
            
            for i in range(3):
                msg = f"\n[Iteration {i+1}] Creating Session..."
                f.write(msg + "\n"); f.flush(); print(msg)
                
                try:
                    # Create Session
                    resp = await client.post(f"{base_url}/sessions", json={"store_url": store_url})
                    if resp.status_code != 200:
                         err = f"❌ Failed to create session: {resp.text}"
                         f.write(err + "\n"); f.flush(); print(err)
                         continue
                    
                    session_id = resp.json()["session_id"]
                    f.write(f"Session ID: {session_id}\n"); f.flush()
                    
                    msg = f"[Iteration {i+1}] Sending Message..."
                    f.write(msg + "\n"); f.flush(); print(msg)
                    
                    chat_resp = await client.post(f"{base_url}/chat", json={
                        "session_id": session_id,
                        "message": query
                    })
                    
                    if chat_resp.status_code != 200:
                        err = f"❌ Chat failed: {chat_resp.text}"
                        f.write(err + "\n"); f.flush(); print(err)
                        continue
                        
                    message = chat_resp.json()["message"]
                    thought_process = chat_resp.json().get("thought_process", "No thoughts")
                    
                    f.write(f"[Iteration {i+1}] Response Length: {len(message)}\n")
                    f.write(f"Preview: {message[:100]}...\n")
                    f.write(f"Full Response: {message}\n")
                    f.write(f"Thought Process Snippet: {thought_process[:500]}...\n") 
                    f.flush()
                    
                    responses.append(message)
                except Exception as e:
                    err = f"❌ Exception: {str(e)}"
                    f.write(err + "\n"); f.flush(); print(err)
                
                # Compare
                if i > 0 and len(responses) > i:
                    if responses[i] == responses[i-1]:
                        msg = f"✅ Match with previous."
                        f.write(msg + "\n"); f.flush(); print(msg)
                    else:
                        msg = f"❌ MISMATCH with previous!"
                        f.write(msg + "\n"); f.flush(); print(msg)
                        
            f.write("\n--- Summary ---\n")
            unique_responses = set(responses)
            if len(unique_responses) == 1 and len(responses) == 3:
                f.write("✅ PASSED: All 3 responses were identical.\n")
                print("✅ PASSED")
            else:
                f.write(f"❌ FAILED: Found {len(unique_responses)} unique responses.\n")
                print("❌ FAILED")
                
    print("Consistency check complete. See backend/consistency_report.txt")

if __name__ == "__main__":
    asyncio.run(run_consistency_check())
