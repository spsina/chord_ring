import json
import jsonpickle

class AccessInfo:

    def __init__(self, address, port, id):
        self.address = address
        self.port = port
        self.id = id