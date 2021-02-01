import asyncio
import websockets
import json
from access_info import AccessInfo
import random
from threading import Thread

class Node:

    def __init__(self, ai, chord_access_info):
        self.finger_table = []
        self.nxt = None
        self.prv = None
        self.cai = chord_access_info
        self.ai = ai

    
    async def run(self, websocket, path):
        """
        func_data = json.loads(func_str)

        function = func_data.get('func_name')
        args = func_data.get('args')
        kwargs = func_data.get('kwargs')

        """

        func_str = await websocket.recv()

        func_data = json.loads(func_str)
        func_name = func_data.get('func_name')
        func = eval("self.%s" % func_name)
        args = func_data.get('args')
        kwargs = func_data.get('kwargs')

        print(args, kwargs)

        _return = func(*args, **kwargs)

        print("[NODE %d] exceuted %s with args %s and kwargs %s" % (self.ai.id, func_name, json.dumps(args), json.dumps(kwargs)))

        await websocket.send(json.dumps(_return))
        
        return json.dumps(_return)

    def hello(self, name):
        return "Hello %s" % name

    def start(self):
        """
        if chord access info is set, it means this node
        is trying to connect to a ring

        otherwise, this node is the genesis node in a ring
        """

        if self.cai:
            pass
        else:
            pass
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        start_server = websockets.serve(self.run, self.ai.address, self.ai.port)
        asyncio.get_event_loop().run_until_complete(start_server)

        print("[NODE : %d] running node on %s:%d" % (self.ai.id, self.ai.address, self.ai.port))
        print("[NODE %d] waiting for commands" % self.ai.id)

        asyncio.get_event_loop().run_forever()

def node_manager(_ai):
    _node = Node(_ai, None)
    _node.start()


async def test(_ai):
    
    async with websockets.connect("ws://%s:%d" % (_ai.address, _ai.port)) as websocket:
        
        _data = {
            'func_name': 'hello',
            'args': (),
            'kwargs': {'name': 'sina'}
        }

        await websocket.send(json.dumps(_data))
        _result = await websocket.recv()
        
        if _result is not None:
            result = json.loads(_result)
        else:
            result = None

        print(result)

if __name__ == "__main__":
    _ai = AccessInfo("localhost", 9090, random.randint(1,32))

    _t = Thread(target=node_manager, args=(_ai, ))
    _t.start()
    import time
    time.sleep(1)
    asyncio.get_event_loop().run_until_complete(test(_ai))
    
    _t.join()