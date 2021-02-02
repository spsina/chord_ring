import asyncio
from time import sleep
import websockets
import jsonpickle
from access_info import AccessInfo
import random
from threading import Thread
import math
import json


class Node:

    _MAX = 32   # max numbers of nodes in the ring

    def __init__(self, ai, chord_access_info):
        self.finger_table = []
        self.nxt = ai
        self.prv = ai
        self.cai = chord_access_info
        self.ai = ai

    ### setters and getters start
    def set_nxt(self, nxt):
        self.nxt = nxt

    def set_prv(self, prv):
        self.prv = prv

    def get_nxt(self):
        return self.nxt

    def get_prv(self):
        return self.prv
    ### setters and getteres end
    
    def get_range(self):
        if self.prv:
            
            # range is (prvId, currentId]
            # or (prvId, _MAX] if currentID < prvId
            if self.ai.id > self.prv.id:
                _start = self.prv.id + 1
                _end = self.ai.id + 1
            elif self.ai.id < self.prv.id:
                _start = self.prv + 1
                _end = self._MAX + 1
            else:
                _start = 1
                _end = 33

            return range(_start, _end)
        
        # if no prv, only one node is in the ring
        # so all ranges are acceptable
        return range(1, 33)
            

    async def remote_locate(self, _chord, key):
        async with websockets.connect("ws://%s:%d" % (_chord.address,
         _chord.port)) as websocket:

            _data = {
                'func_name': 'locate',
                'args': (),
                'kwargs': {'key': key}
            }

            await websocket.send(json.dumps(_data))
            _result = await websocket.recv()

            if _result is not None:
                result = jsonpickle.decode(_result)
            else:
                result = None

            return result

    async def locate(self, key):
        """
        Find what node the given key is located in
        """

        # check if key is on the current node
        if key in self.get_range():
            return self.ai

        """
        self.finger_table
            ft.address
            ft.port
            ft.id
        """

        for i in range(len(self.finger_table) - 1):
            if self.finger_table[i].id <= key <= self.finger_table[i + 1].id:
                return await self.remote_locate(self.finger_table[i], key)
        
        _chord_id = - 1
        _chord= None

        for ft in self.finger_table:
            if ft.id > _chord_id:
                _chord = ft

        if not _chord:
            raise Exception("yja ridim")
            
        return await self.remote_locate(_chord, key)
        
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

        _return = func(*args, **kwargs)

        print("[NODE %d] exceuted %s with args %s and kwargs %s" % (self.ai.id, func_name, json.dumps(args), json.dumps(kwargs)))

        await websocket.send(json.dumps(_return))
        
        return json.dumps(_return)

    def hello(self, name):
        return "Hello %s" % name

    async def if_not_my_range_nxt_range(self, q):
        if q in self.get_range():
            key_q = self.ai
        else:
            nxt = self.nxt
            async with websockets.connect("ws://%s:%d" % (nxt.address, nxt.port)) as websocket:
                _data = {
                    'func_name': 'if_not_my_range_nxt_range',
                    'args': (),
                    'kwargs': {'q': q}
                }

                await websocket.send(json.dumps(_data))
                _result = await websocket.recv()

                if _result is not None:
                    result = json.loads(_result)
                else:
                    result = None

                key_q = result
        print("[NODE %d] " % self.ai.id, key_q.address, key_q.port, key_q.id)
        return key_q

    async def update_finger_table(self):
        """
        FT:

        q           key
        -----------------
        id + 1      key1
        id + 2      key2
        id + 4      key3
        id + 8      key4
        id + 16     key5
        """

        self.finger_table = []

        for i in range(5):
            q = self.ai.id + 2**(i)

            key_q = await self.if_not_my_range_nxt_range(q)
            self.finger_table.append(key_q)

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
        
        asyncio.get_event_loop().run_until_complete(self.update_finger_table())
        
        start_server = websockets.serve(self.run, self.ai.address, self.ai.port)
        asyncio.get_event_loop().run_until_complete(start_server)

        print("[NODE : %d] running node on %s:%d" % (self.ai.id, self.ai.address, self.ai.port))
        print("[NODE %d] waiting for commands" % self.ai.id)

        asyncio.get_event_loop().run_forever()

    def print_finger_table(self):
        return "[NODE %d] Finget Table: " % self.ai.id, self.finger_table

def node_manager(_ai):
    _node = Node(_ai, None)
    _node.start()


async def test(_ai):
    
    async with websockets.connect("ws://%s:%d" % (_ai.address, _ai.port)) as websocket:
        
        _data = {
            'func_name': 'print_finger_table',
            'args': (),
            'kwargs': {}
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