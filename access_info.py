import json
import jsonpickle

class AccessInfo:

    def __init__(self, address, port, id):
        self.address = address
        self.port = port
        self.id = id

    def __repr__(self) -> str:
        return json.dumps({
            'address': self.address,
            'port': self.port,
            'id': self.id
        })


t = AccessInfo("localhost", 3242, 3)
d = jsonpickle.encode(t)
print(d)
print(type(d))
print(jsonpickle.decode(d))