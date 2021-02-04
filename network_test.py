import asyncio
from access_info import AccessInfo
from node import Node
from threading import Thread
import time
from colorama import Fore, Back, Style

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
_run = asyncio.get_event_loop().run_until_complete


def node_runner(node):
    """
    This function is used to run in a thread, so it's keeps a node alive
    """

    node.start()


def spawn_node(node):
    """
    given a node, start a thread that starts the node
    waits 0.7 seconds to ensure that the node is up and runnig
    """

    t1 = Thread(target=node_runner, args=(node,))
    t1.start()
    # threads.append(t1)
    time.sleep(1)


def assert_nxt_and_prv(na, nxt_id, prv_id):
    """
    check prv and nxt node of a given node with the true nxt_id and prv_id 
    that is provided to this function
    """

    _nxt = _run(na.execute('get_nxt'))
    _prv = _run(na.execute('get_prv'))
    assert _nxt.id == nxt_id
    assert _prv.id == prv_id


def assert_finger_table(na, ft):
    """
    check finger table of the given node (with connection info "na")
    with the provided ft

    ft: a list containing the id values of the nodes that should be in the finger table
    """

    _ft = _run(na.execute('get_finger_table'))

    # each record in the finger table is structured as follows:
    # an AccessInfo object, which provides connection info to it's corresponding node

    # generate a list containing only node id's from the retrieved ft
    _ft_ids = [__ft.id for __ft in _ft]

    # sort the lists, so position of record can match
    _ft_ids.sort()
    ft.sort()

    assert _ft_ids == ft


def assert_location(key_to_locate, node_to_ask, node_id):
    """
    assert the correctness of the key location
    key_to_ask: the key we are trying to find location for
    node_to_ask: this is the node that we ask for the key
    node_id: the actual node id
    """

    _node_location = _run(node_to_ask.execute('locate', key=key_to_locate))
    assert _node_location.id == node_id


def get_node_prv_nxt(node):
    return node.id, _run(node.execute('get_prv')).id, _run(node.execute('get_nxt')).id


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

    # assert the correctness of ring positions
    assert_nxt_and_prv(n1a, 4, 20)
    assert_nxt_and_prv(n2a, 13, 1)
    assert_nxt_and_prv(n3a, 20, 4)
    assert_nxt_and_prv(n4a, 1, 13)

    # get prv and next node (used for report print)
    n1_prv_nxt = get_node_prv_nxt(n1a)
    n2_prv_nxt = get_node_prv_nxt(n2a)
    n3_prv_nxt = get_node_prv_nxt(n3a)
    n4_prv_nxt = get_node_prv_nxt(n4a)

    # assert finger table correctness
    assert_finger_table(n1a, [4, 4, 13, 13, 20])
    assert_finger_table(n2a, [13, 13, 13, 13, 20])
    assert_finger_table(n3a, [20, 20, 20, 1, 1])
    assert_finger_table(n4a, [1, 1, 1, 1, 4])

    # get finger table (used for report print)
    n1_ft = n1a.id, str([_ft.id for _ft in _run(n1a.execute('get_finger_table'))])
    n2_ft = n2a.id, str([_ft.id for _ft in _run(n1a.execute('get_finger_table'))])
    n3_ft = n3a.id, str([_ft.id for _ft in _run(n1a.execute('get_finger_table'))])
    n4_ft = n4a.id, str([_ft.id for _ft in _run(n1a.execute('get_finger_table'))])

    assert_location(3, n1a, 4)
    assert_location(13, n4a, 13)
    assert_location(26, n2a, 1)
    assert_location(39, n3a, 13)

    print(Fore.YELLOW, "[NETWORK TEST] RING PREV AND NEXT NODE REPORT: ", Fore.BLUE)
    print(" [NETWORK TEST] node id %2d:\tprev_node_id: %2d\tnext_node_id:%2d" % n1_prv_nxt)
    print(" [NETWORK TEST] node id %2d:\tprev_node_id: %2d\tnext_node_id:%2d" % n2_prv_nxt)
    print(" [NETWORK TEST] node id %2d:\tprev_node_id: %2d\tnext_node_id:%2d" % n3_prv_nxt)
    print(" [NETWORK TEST] node id %2d:\tprev_node_id: %2d\tnext_node_id:%2d" % n4_prv_nxt)

    print(Fore.YELLOW, "[NETWORK TEST] RING FINGER TABLE REPORT: ", Fore.BLUE)
    print(" [NETWORK TEST] node id %2d:\t%s" % n1_ft)
    print(" [NETWORK TEST] node id %2d:\t%s" % n2_ft)
    print(" [NETWORK TEST] node id %2d:\t%s" % n3_ft)
    print(" [NETWORK TEST] node id %2d:\t%s" % n4_ft)

    print(Fore.GREEN, "[NETWORK TEST] ALL TESTS PASSED")
