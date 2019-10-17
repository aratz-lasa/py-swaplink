from typing import List

from swaplink.abc import ISwaplink, INode, NodeAddr
from swaplink.node import Node


class Swaplink(ISwaplink):
    _relative_load: int
    _node: "INode"

    def __init__(self, relative_load: int = 10, bootstrap: NodeAddr = None):
        self._relative_load = max(1, relative_load)
        # todo
        self._node = Node()

    async def get_neighbour_nodes(self) -> List[INode]:
        pass  # todo

    async def get_random_node(self) -> INode:
        pass  # todo
