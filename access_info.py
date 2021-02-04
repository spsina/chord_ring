import json
import jsonpickle
import websockets


class AccessInfo:

    def __init__(self, address, port, id):
        self.address = address
        self.port = port
        self.id = id

    def get_uri(self):
        return "ws://%s:%d" % (self.address, self.port)

    async def execute(self, func_name, *args, **kwargs):
        async with websockets.connect(self.get_uri()) as ws:
            _data = {
                'func_name': func_name,
                'args': args,
                'kwargs': kwargs
            }

            await ws.send(jsonpickle.encode(_data))
            _result = await ws.recv()
            result = jsonpickle.decode(_result)

            return result

    def __repr__(self) -> str:
        return json.dumps({
            'address': self.address,
            'port': self.port,
            'id': self.id
        })

    def __eq__(self, other):
        return self.id == other.id
