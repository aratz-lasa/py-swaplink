from typing import List

from swaplink.abc import (
    ISwaplink,
    INode,
    ISwaplinkProtocol,
    NodeAddr,
    NeighborsCallback,
)
from swaplink.node import Node


class Swaplink(ISwaplink):
    _relative_load: int
    _node: "INode"
    _in_links: List[INode]
    _out_links: List[INode]
    _protocol: ISwaplinkProtocol

    def __init__(self, host: str = "0.0.0.0", port: int = 5678):
        self._in_links = []
        self._out_links = []
        # todo
        self._node = Node(host, port)
        self._relative_load = None
        self._callback: NeighborsCallback
        self._callback = None

    async def join(self, num_links: int, bootstrap: NodeAddr = None) -> None:
        self._relative_load = num_links
        # todo: join network through bootstrap node

    async def list_neighbours(
        self, callback_on_change: NeighborsCallback
    ) -> List["INode"]:
        self._callback = callback_on_change
        return self._out_links  # todo: return also in-links?
        pass

    async def select(self) -> INode:
        # todo:
        #   - select randomly a neighbor
        #   - run OnlyInLinks random walk
        pass
