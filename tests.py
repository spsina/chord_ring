import asyncio
from access_info import AccessInfo
from threading import Thread
from node import Node
import random

async def test_run_function(_ai):
    """
    tests the functionality of run function a given ai node
    :param _ai: remove chord ai
    :return: None
    """
    # sync function test
    print("[TEST] -----------> Testing Sync Function Call")
    
    result = await _ai.execute("hello", name="sina")
    assert result == "Hello sina"

    print("[TEST] ############ Testing Sync Function Call --- end")

    # async function test
    print("[TEST] -----------> Testing Async Function Call")
    
    result = await _ai.execute('a_hello', name="sina")
    assert result == "Async Hello sina"

    print("[TEST] ############ Testing Async Function Call")


async def test_finger_table(_ai):
    """
    test finger table creation
    :param _ai: remove chord ai
    :return: None
    """
    # sync function test
    print("[TEST] -----------> Update Finger Table")
    result = await _ai.execute('update_finger_table')
    assert result == None
    print("[TEST] ############ Update Finger Table")

    print("[TEST] -----------> Get Finger Table")
    result = await _ai.execute('get_finger_table')
    assert result == [_ai for i in range(5)]
    print("[TEST] ############ Get Finger Table")


async def test_locate_for_insert(_ai):
    """
    test locate for insert
    :param _ai: remove chord ai
    :return: None
    """
    # sync function test
    print("[TEST] -----------> Locate For Insert")
    result = await _ai.execute('locate_for_insert')
    print("[TEST] ############ Locate For Insert")


async def test_cai_node(_ai):
    """
    test finger table creation
    :param _ai: remove chord ai
    :return: None
    """

    def cai_node():
        cai = AccessInfo("localhost", 2020, random.randint(1, 32))
        _node = Node(cai, _ai)
        _node.start()

    _t = Thread(target=cai_node)
    _t.start()
    _t.join()


def test(_ai):

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    asyncio.get_event_loop().run_until_complete(test_run_function(_ai))
    asyncio.get_event_loop().run_until_complete(test_finger_table(_ai))
    asyncio.get_event_loop().run_until_complete(test_locate_for_insert(_ai))
    asyncio.get_event_loop().run_until_complete(test_cai_node(_ai))
