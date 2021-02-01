import asyncio
import json
import websockets
from access_info import AccessInfo
import random

_ai = AccessInfo("localhost", 9090, 30)

async def hello():
    uri = "ws://%s:%d" % (_ai.address, _ai.port)
    async with websockets.connect(uri) as websocket:
        _data = {
            'func_name': 'hello',
            'args': (),
            'kwargs': {'name': 'Ali From Other Proccess'}
        }

        await websocket.send(json.dumps(_data))
        _result = await websocket.recv()
        
        if _result is not None:
            result = json.loads(_result)
        else:
            result = None

        print(result)

asyncio.get_event_loop().run_until_complete(hello())