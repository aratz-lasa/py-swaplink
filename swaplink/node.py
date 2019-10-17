from swaplink.abc import INode, NodeAddr


class Node(INode):
    _host: str
    _port: int

    def __init__(self, host: str, port: int):
        self._host = host
        self._port = port

    def get_addr(self) -> NodeAddr:
        return (self._host, self._port)
