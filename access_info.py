import json
import jsonpickle

class AccessInfo:

    def __init__(self, address, port, id):
        self.address = address
        self.port = port
        self.id = id

    def get_uri(self):
        return "ws://%s:%d" % (self.address, self.port)

    def __repr__(self) -> str:
        return json.dumps({
            'address': self.address,
            'port': self.port,
            'id': self.id
        })
