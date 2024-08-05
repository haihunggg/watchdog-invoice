import json
from pprint import pprint

try:
    with open("connectstring_config.json") as fo:
        ans = json.load(fo)
    pprint(ans)
except Exception as e:
    print("empty")
