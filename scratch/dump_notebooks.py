from Execution.pp_notebooklm.client import NotebookLMClient
import json

client = NotebookLMClient()
result = client._call_rpc(client.RPC_LIST_NOTEBOOKS, [None, 1, None, [2]])
with open("notebooks_raw.json", "w") as f:
    json.dump(result, f, indent=2)

print("Dumped notebooks to notebooks_raw.json")
