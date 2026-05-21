import json
import re

def find_uuids(obj):
    uuids = []
    if isinstance(obj, str):
        if len(obj) == 36 and re.match(r"^[0-9a-f\-]{36}$", obj):
            uuids.append(obj)
    elif isinstance(obj, list):
        for item in obj:
            uuids.extend(find_uuids(item))
    elif isinstance(obj, dict):
        for val in obj.values():
            uuids.extend(find_uuids(val))
    return uuids

with open("notebooks_raw.json", "r") as f:
    data = json.load(f)

all_uuids = set(find_uuids(data))
print(f"Found {len(all_uuids)} unique UUIDs:")
for uid in sorted(all_uuids):
    print(uid)
