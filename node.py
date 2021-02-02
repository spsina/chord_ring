import asyncio

import websockets
import jsonpickle
from access_info import AccessInfo
import random
from threading import Thread
import json
import time


class Node:
    _MAX = 32  # max numbers of nodes in the ring

    def __init__(self, ai, chord_access_info):
        self.finger_table = []  # finger table
        self.nxt = ai  # next node access info (address, port, id)
        self.prv = ai  # previous node access info (address, port, id)
        self.cai = chord_access_info  # a chord node that this node will be joind to
        self.ai = ai  # self access info

    def set_nxt(self, nxt):
        self.nxt = nxt

    def set_prv(self, prv):
        self.prv = prv

    def get_nxt(self):
        return self.nxt

    def get_prv(self):
        return self.prv

    def get_range(self):
        """
        :return: a range of keys, that might be saved on this node
        """

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
            _end = self._MAX

        return range(_start, _end)

    @staticmethod
    async def remote_locate(_chord, key):
        """
        :param _chord: a node in the ring
        :param key: key to ask the location of, from the given _chord
        :return: a _chord AI(accessInfo) where the given key is saved
        """
        async with websockets.connect(_chord.get_uri()) as ws:

            # we intend to call the locate function on the given _chord
            _data = {
                'func_name': 'locate',
                'kwargs': {'key': key},
                'args': ()
            }

            await ws.send(json.dumps(_data))
            _result = await ws.recv()

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
        _chord = None

        for ft in self.finger_table:
            if ft.id > _chord_id:
                _chord = ft

        if not _chord:
            raise Exception("yja ridim")

        return await self.remote_locate(_chord, key)

    async def if_not_my_range_nxt_range(self, q):
        if q in self.get_range():
            key_q = self.ai
        else:
            async with websockets.connect(self.nxt.get_uri()) as ws:
                _data = {
                    'func_name': 'if_not_my_range_nxt_range',
                    'args': (),
                    'kwargs': {'q': q}
                }

                await ws.send(json.dumps(_data))
                _result = await ws.recv()

                if _result is not None:
                    result = jsonpickle.decode(_result)
                else:
                    result = None

                key_q = result

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
            q = self.ai.id + 2 ** i % self._MAX

            key_q = await self.if_not_my_range_nxt_range(q)
            self.finger_table.append(key_q)

    def get_finger_table(self):
        return self.finger_table

    async def run(self, websocket, path):
        """
        func_data = json.loads(func_str)

        function = func_data.get('func_name')
        args = func_data.get('args')
        kwargs = func_data.get('kwargs')

        """

        while True:
            func_str = await websocket.recv()
            func_data = json.loads(func_str)

            func_name = func_data.get('func_name')
            func = eval("self.%s" % func_name)
            args = func_data.get('args')
            kwargs = func_data.get('kwargs')

            try:
                # the given function is an async, we need to await it
                _return = await func(*args, **kwargs)
            except TypeError:
                _return = func(*args, **kwargs)

            print("[NODE %d] executed %s with args %s and kwargs %s" % (
                self.ai.id, func_name, json.dumps(args), json.dumps(kwargs)))

            await websocket.send(jsonpickle.encode(_return))
            return jsonpickle.encode(_return)

    @staticmethod
    async def test_run_function(_ai):
        """
        tests the functionality of run function a given ai node
        :param _ai: remove chord ai
        :return: None
        """
        # sync function test
        print("[TEST] -----------> Testing Sync Function Call")
        async with websockets.connect(_ai.get_uri()) as ws:
            _data = {
                'func_name': 'hello',
                'args': (),
                'kwargs': {"name": "sina"}
            }

            print("[TEST] Sending Data")
            await ws.send(json.dumps(_data))
            print("[TEST] Waiting for Data")
            _result = await ws.recv()
            result = jsonpickle.decode(_result)

            print("[TEST] result: ", result)
            assert result == "Hello sina"
        print("[TEST] ############ Testing Sync Function Call --- end")

        # async function test
        print("[TEST] -----------> Testing Async Function Call")
        async with websockets.connect(_ai.get_uri()) as ws:
            _data = {
                'func_name': 'a_hello',
                'args': (),
                'kwargs': {"name": "sina"}
            }

            print("[TEST] Sending Data")
            await ws.send(json.dumps(_data))
            print("[TEST] Waiting for Data")
            _result = await ws.recv()
            result = jsonpickle.decode(_result)

            print("[TEST] result: ", result)
            assert result == "Async Hello sina"
        print("[TEST] ############ Testing Async Function Call")

    @staticmethod
    async def test_finger_table(_ai):
        """
        test finger table creation
        :param _ai: remove chord ai
        :return: None
        """
        # sync function test
        print("[TEST] -----------> Update Finger Table")
        async with websockets.connect(_ai.get_uri()) as ws:
            _data = {
                'func_name': 'update_finger_table',
                'args': (),
                'kwargs': {}
            }

            print("[TEST] Sending Data")
            await ws.send(json.dumps(_data))
            print("[TEST] Waiting for Data")
            _result = await ws.recv()
            result = jsonpickle.decode(_result)

            print("[TEST] result: ", result)
            assert result == None
        print("[TEST] ############ Update Finger Table")

        print("[TEST] -----------> Get Finger Table")
        async with websockets.connect(_ai.get_uri()) as ws:
            _data = {
                'func_name': 'get_finger_table',
                'args': (),
                'kwargs': {}
            }

            print("[TEST] Sending Data")
            await ws.send(json.dumps(_data))
            print("[TEST] Waiting for Data")
            _result = await ws.recv()
            result = jsonpickle.decode(_result)

            print("[TEST] result: ", result)
        print("[TEST] ############ Get Finger Table")

    def test(self):
        # this process may be run from a thread
        # get a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        print("[TEST] ==================>")
        # run function test
        asyncio.get_event_loop().run_until_complete(self.test_run_function(self.ai))
        asyncio.get_event_loop().run_until_complete(self.test_finger_table(self.ai))
        print("[TEST] ===================")

    @staticmethod
    def hello(name):
        """Used for testing sync function calls"""
        return "Hello %s" % name

    @staticmethod
    async def a_hello(name):
        """Used for testing async function calls"""
        return "Async Hello %s" % name

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

        # this process may be run from a thread
        # get a new event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

        start_server = websockets.serve(self.run, self.ai.address, self.ai.port)
        asyncio.get_event_loop().run_until_complete(start_server)

        print("[NODE : %d] running node on %s:%d" % (self.ai.id, self.ai.address, self.ai.port))
        print("[NODE : %d] running self test")

        _test = Thread(target=self.test)
        _test.start()

        print("[NODE %d] waiting for commands" % self.ai.id)

        asyncio.get_event_loop().run_forever()


def node_manager(_ai):
    _node = Node(_ai, None)
    _node.start()


if __name__ == "__main__":
    _ai = AccessInfo("localhost", 9090, random.randint(1, 32))
    _t = Thread(target=node_manager, args=(_ai,))
    _t.start()
    _t.join()
