from access_info import AccessInfo
from node import Node
from threading import Thread
import asyncio

loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
_run = asyncio.get_event_loop().run_until_complete


def node_starter(node):
    node.start()


def spaw_node():
    address = input("address(localhost): ")
    if not address:
        address = "localhost"
    port = int(input("port: "))
    chord = None
    connect_to_ring = input("Connect to existing ring? (Y/N): ")

    while connect_to_ring not in "YyNn":
        connect_to_ring = input("Connect to existing ring? (Y/N): ")

    connect_to_ring = True if connect_to_ring in "Yy" else False

    if connect_to_ring:
        chord_address = input("chord adderss(localhost): ")
        if not chord_address:
            chord_address = "localhost"
        chord_port = int(input("chord port: "))
        chord_id = int(input("chord id: "))
        chord = AccessInfo(chord_address, chord_port, chord_id)

    _ai = AccessInfo(address, port, None)
    _node = Node(ai=_ai, chord_access_info=chord)

    _t = Thread(target=node_starter, args=(_node,))
    _t.start()

    threads.append(_t)


def add_node():
    address = input("address(localhost): ")
    if not address:
        address = "localhost"
    port = int(input("port: "))
    id = int(input("id: "))

    _ai = AccessInfo(address=address, port=port, id=id)
    nodes[_ai.id] = _ai


def list_nodes():
    for i in nodes.keys():
        print("%d - %s:%d" % (nodes[i].id, nodes[i].address, nodes[i].port))


def get_not_null_input(message):
    _i = input(message)
    while not _i:
        _i = input(message)

    return _i


def ex():
    node_id = int(get_not_null_input("Node Id: "))

    if node_id not in nodes.keys():
        print("ERROR - node with id %d does not exist" % node_id)
        return

    _node = nodes[node_id]

    func_name = get_not_null_input("Func name: ")
    kwargs = {}

    while True:
        kwargs_str = input("kwargs: ")
        if not kwargs_str:
            break
        try:
            _kwargs = kwargs_str.split()

            for __kwargs in _kwargs:
                key_value = __kwargs.split("=")
                if len(key_value) != 2:
                    raise Exception("Invalid kwargs")
                kwargs[key_value[0]] = key_value[1]
            break
        except Exception as e:
            print(str(e))

    try:
        result = _run(_node.execute(func_name, **kwargs))
        print("---> ", result)

    except Exception as e:
        print(str(e))


if __name__ == "__main__":
    commands = {
        'spawn node': spaw_node,
        'add node': add_node,
        'list nodes': list_nodes,
        'ex': ex,
        'q': None
    }

    threads = []
    nodes = {}

    while True:
        command = input("<terminal> ")

        if command == "q":
            break

        if not command:
            continue

        func = commands.get(command, None)

        if not func:
            print("ERROR - Invalid Command")
            continue

        func()
