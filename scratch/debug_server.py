import subprocess
import time
import os

env = os.environ.copy()
env["PYTHONPATH"] = "/Users/marcolemoglie_1_2/Desktop/canale/.venv/lib/python3.11/site-packages"

# Start the server
with open("scratch/server_stdout.bin", "wb") as f_out, open("scratch/server_stderr.bin", "wb") as f_err:
    process = subprocess.Popen(
        ["/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/python3", "-m", "notebooklm_mcp.cli", "--config", "notebooklm-config.json", "server"],
        stdout=f_out,
        stderr=f_err,
        env=env,
        stdin=subprocess.PIPE
    )
    
    print("Waiting 10s for server to start...")
    time.sleep(10)
    
    # Send a list_tools request
    request = b'{"jsonrpc": "2.0", "method": "tools/list", "id": 1}\n'
    print("Sending request...")
    process.stdin.write(request)
    process.stdin.flush()
    
    print("Waiting 10s for response...")
    time.sleep(10)
    process.terminate()

print("Server test complete. Check scratch/server_stdout.bin and scratch/server_stderr.bin")
