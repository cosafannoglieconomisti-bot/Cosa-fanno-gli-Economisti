import subprocess
import os
import time

env = os.environ.copy()
# Force stdio transport
env["NOTEBOOKLM_MCP_TRANSPORT"] = "stdio"

print("Starting server and capturing output to /tmp/nlm_raw_output.bin...")
with open("/tmp/nlm_raw_output.bin", "wb") as f:
    proc = subprocess.Popen(
        ["/Library/Frameworks/Python.framework/Versions/3.13/bin/notebooklm-mcp"],
        stdout=f,
        stderr=subprocess.PIPE,
        env=env,
        text=False
    )
    
    # Wait a bit
    time.sleep(3)
    proc.terminate()
    stdout_data, stderr_data = proc.communicate()

print(f"Server exited. Stderr length: {len(stderr_data)}")
print(f"Stderr sample: {stderr_data[:200]!r}")

if os.path.exists("/tmp/nlm_raw_output.bin"):
    size = os.path.getsize("/tmp/nlm_raw_output.bin")
    print(f"Raw output size: {size} bytes")
    if size > 0:
        with open("/tmp/nlm_raw_output.bin", "rb") as f:
            content = f.read(100)
            print(f"Raw output start: {content!r}")
