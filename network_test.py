import asyncio
from access_info import AccessInfo
from node import Node
from threading import Thread
import time

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
_run = asyncio.get_event_loop().run_until_complete

def node_runner(node):
    """
    This function is used to run in a thraed, so it's keeps a node alive
    """
    
    node.start()


def spawn_node(node):
    """
    given a node, start a thread that starts the node
    waits 0.7 seconds to ensure that the node is up and runnig
    """

    t1 = Thread(target=node_runner, args=(node, ))
    t1.start()
    threads.append(t1)
    time.sleep(0.7)


def assert_nxt_and_prv(na, nxt_id, prv_id):
    """
    check prv and nxt node of a given node with the true nxt_id and prv_id 
    that is provided to this function
    """

    _nxt = _run(na.execute('get_nxt'))
    _prv = _run(na.execute('get_prv'))
    assert _nxt.id == nxt_id
    assert _prv.id == prv_id

if __name__ == "__main__":
    threads = []

    # create chord ring with 4 chords
    n1a = AccessInfo('localhost', 1212, 1)
    n2a = AccessInfo('localhost', 4545, 4)
    n3a = AccessInfo('localhost', 6565, 13)
    n4a = AccessInfo('localhost', 7878, 20)

    # spawn the chord into the ring
    n1 = Node(n1a, None)
    spawn_node(n1)
    
    n2 = Node(n2a, n1a)
    spawn_node(n2)

    n3 = Node(n3a, n1a)
    spawn_node(n3)

    n4 = Node(n4a, n1a)
    spawn_node(n4)


    # assert the correctness of the ring
    # - chord positions in the ring
    # - finger table of each node
    # - storage location(node) of a given key
    
    # assert the currectness of ring positions
    assert_nxt_and_prv(n1a, 4, 20)
    assert_nxt_and_prv(n2a, 13, 1)
    assert_nxt_and_prv(n3a, 20, 4)
    assert_nxt_and_prv(n4a, 1, 13)


    for t in threads:
        t.join()





