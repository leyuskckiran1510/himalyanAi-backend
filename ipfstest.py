import ipfsApi

api = ipfsApi.Client(host="localhost", port=5001)
print(api.add_str("dawdawdawdawdawdawd"))
