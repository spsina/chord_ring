from access_info import AccessInfo
import random
from threading import Thread
from node import Node
import time


def node_manager(_ai):
    _node = Node(_ai, None)
    _node.start()


if __name__ == "__main__":
    _ai = AccessInfo("localhost", 9090, random.randint(1, 32))
    _t = Thread(target=node_manager, args=(_ai,))
    _t.start()
    time.sleep(0.5)
    import tests

    tests.test(_ai)

    _t.join()
