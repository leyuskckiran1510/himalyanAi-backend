import ipfsapi

api = ipfsapi.Client(host="localhost", port=5001)
print(api.add_str("dawdawdawdawdawdawd"))
