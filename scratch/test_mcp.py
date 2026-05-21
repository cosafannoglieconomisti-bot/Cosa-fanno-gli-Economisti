import subprocess
import json
import time

def test_mcp():
    cmd = [
        "/Users/marcolemoglie_1_2/Desktop/canale/.venv/bin/notebooklm-mcp",
        "server",
        "--config", "notebooklm-config.json"
    ]
    
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=0
    )
    
    # Send initialize request
    init_request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "test-client", "version": "1.0"}
        }
    }
    
    print("Sending initialize request...")
    process.stdin.write(json.dumps(init_request) + "\n")
    process.stdin.flush()
    
    # Read stdout
    print("Reading stdout...")
    stdout_lines = []
    try:
        # Read for a bit
        for _ in range(5):
            line = process.stdout.readline()
            if line:
                print(f"STDOUT: {line.strip()}")
                stdout_lines.append(line)
            else:
                break
    except Exception as e:
        print(f"Error reading stdout: {e}")
    
    # Read stderr
    print("Reading stderr...")
    stderr_output = process.stderr.read(1000)
    print(f"STDERR: {stderr_output}")
    
    process.terminate()

if __name__ == "__main__":
    test_mcp()
