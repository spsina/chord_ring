import asyncio
import websockets
import jsonpickle
from access_info import AccessInfo
import random
from threading import Thread
import time


class Node:
    _MAX = 32  # max numbers of nodes in the ring

    def __init__(self, ai, chord_access_info):
        self.finger_table = []  # finger table
        self.nxt = ai  # next node access info (address, port, id)
        self.prv = ai  # previous node access info (address, port, id)
        self.cai = chord_access_info  # a chord node that this node will be joind to
        self.ai = ai  # self access info

    async def set_nxt(self, nxt):
        self.nxt = nxt

    async def set_prv(self, prv):
        self.prv = prv

    async def get_nxt(self):
        return self.nxt

    async def get_prv(self):
        return self.prv

    async def get_range(self):
        """
        :return: a range of keys, that might be saved on this node
        """

        # range is (prvId, currentId]
        # or (prvId, _MAX] if currentID < prvId
        if self.ai.id > self.prv.id:
            _start = self.prv.id + 1
            _end = self.ai.id + 1
        elif self.ai.id < self.prv.id:
            _start = self.prv.id + 1
            _end = self._MAX + 1
        else:
            _start = 1
            _end = self._MAX

        return range(_start, _end)

    @staticmethod
    async def remote_locate(_chord, key):
        """
        :param _chord: a node in the ring
        :param key: key to ask the location of, from the given _chord
        :return: a _chord AI(accessInfo) where the given key is saved
        """
        return await _chord.execute("locate", key=key)

    async def locate(self, key):
        
        """
        Find what node the given key is located in
        """

        # normalize key
        key = key % self._MAX

        if key == 0:
            key = 1

        # check if key is on the current node
        if key in await self.get_range():
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
        _chord = None

        # no range found for the given key in finger table
        # so find and  use the chord with the larges supported key
        for ft in self.finger_table:
            if ft.id > _chord_id:
                _chord = ft

        if not _chord:
            raise Exception("Logic Error In Chord Find")

        return await self.remote_locate(_chord, key)

    async def locate_for_insert(self):
        """
        Generate a new id for new node
        find the node that is the proper predesessor of the newly generated id
        """
                
        # do {
        new_node_id = random.randint(1, 32)
        q = await self.locate(new_node_id)
        # }

        while new_node_id == q.id:
            new_node_id = random.randint(1, 32)
            q = await self.locate(new_node_id)
        
        
        return q, new_node_id
    
    async def if_not_my_range_nxt_range(self, q):
        
        # normalize q
        q = q % self._MAX

        if q == 0:
            q = 1

        if q in await self.get_range():
            return self.ai
        else:
            return await self.nxt.execute('if_not_my_range_nxt_range', q=q)
        
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
            q = self.ai.id + 2 ** i

            key_q = await self.if_not_my_range_nxt_range(q)
            self.finger_table.append(key_q)

    async def get_finger_table(self):
        return self.finger_table

    async def run(self, websocket, path):
        """
        func_data = json.loads(func_str)

        function = func_data.get('func_name')
        args = func_data.get('args')
        kwargs = func_data.get('kwargs')

        """
        
        func_str = await websocket.recv()
        func_data = jsonpickle.decode(func_str)

        func_name = func_data.get('func_name')
        func = eval("self.%s" % func_name)
        args = func_data.get('args')
        kwargs = func_data.get('kwargs')

        _return = await func(*args, **kwargs)

        print("[NODE %d] executed %s with args %s and kwargs %s" % (
            self.ai.id, func_name, str(args), str(kwargs)))

        await websocket.send(jsonpickle.encode(_return))
        return jsonpickle.encode(_return)
    
    @staticmethod
    async def hello(name):
        """Used for testing sync function calls"""
        return "Hello %s" % name

    @staticmethod
    async def a_hello(name):
        """Used for testing async function calls"""
        a = random.randint(1,32)
        return "Async Hello %s" % name


    def start(self):
        """
        if chord access info is set, it means this node
        is trying to connect to a ring
        otherwise, this node is the genesis node in a ring
        """
        # this process may be run from a thread
        # get a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        _run = asyncio.get_event_loop().run_until_complete
        
        if self.cai:
            # # connect to the ring
            q, new_id = _run(self.cai.execute("locate_for_insert"))

            # # update the id
            self.ai.id = new_id

            # place the new node in the middle of q and q.nxt
            _q_nxt = _run(q.execute("get_nxt"))
            self.nxt = _q_nxt
            _run(_q_nxt.execute('set_prv', prv=self.ai))
            _run(q.execute('set_nxt', nxt=self.ai))
            
        else:
            self.ai.id = random.randint(1,32)

        start_server = websockets.serve(self.run, self.ai.address, self.ai.port)
        asyncio.get_event_loop().run_until_complete(start_server)

        print("[NODE : %d] running node on %s:%d" % (self.ai.id, self.ai.address, self.ai.port))
        print("[NODE %d] waiting for commands" % self.ai.id)

        asyncio.get_event_loop().run_forever()
