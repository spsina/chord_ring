import asyncio
from access_info import AccessInfo
from node import Node
from threading import Thread
import time


def node_runner(node):
    node.start()


def spawn_node(node):
    t1 = Thread(target=node_runner, args=(node, ))
    t1.start()
    threads.append(t1)
    time.sleep(0.7)

if __name__ == "__main__":
    threads = []

    n1a = AccessInfo('localhost', 1212, 1)
    n2a = AccessInfo('localhost', 4545, None)
    n3a = AccessInfo('localhost', 6565, None)

    n1 = Node(n1a, None)
    spawn_node(n1)
    
    n2 = Node(n2a, n1a)
    spawn_node(n2)

    n3 = Node(n3a, n1a)
    spawn_node(n3)

    

    for t in threads:
        t.join()





