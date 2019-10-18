from typing import List

from swaplink.abc import (
    ISwaplink,
    Node,
    ISwaplinkProtocol,
    LinkStore,
    NodeAddr,
    NeighborsCallback,
    LinkType,
)
from swaplink.defaults import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_WALK_LENGTH
from swaplink.protocol import SwaplinkProtocol
from swaplink.utils import get_random_int_min_zero


class Swaplink(ISwaplink):
    _protocol: ISwaplinkProtocol

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self._link_store = LinkStore()
        self._node = Node(host, port)
        self._protocol = SwaplinkProtocol(self._node, self._link_store)
        self._relative_load = None
        self._callback: NeighborsCallback
        self._callback = None

    async def join(
        self, num_links: int, bootstrap_nodes: List[NodeAddr] = None
    ) -> None:
        self._relative_load = num_links
        for _ in range(num_links):
            random_bootstrap_addr = bootstrap_nodes[
                get_random_int_min_zero(bootstrap_nodes)
            ]
            random_bootstrap = Node(*random_bootstrap_addr)
            new_out_link_found = False
            while not new_out_link_found:
                try:
                    neighbor = await self._protocol.call_random_walk(
                        random_bootstrap, 0, DEFAULT_WALK_LENGTH, LinkType.IN
                    )
                    await self._protocol.call_im_your_in_node(neighbor)
                    self._link_store.out_links.append(neighbor)
                    bootstrap_nodes.append(neighbor)
                    new_out_link_found = True
                except Exception:
                    pass

    async def list_neighbours(
        self, callback_on_change: NeighborsCallback
    ) -> List[Node]:
        self._callback = callback_on_change
        return self._link_store.out_links  # todo: return also in-links?

    async def select(self) -> Node:
        start_node = self._link_store.in_links[
            get_random_int_min_zero(len(self._link_store.in_links))
        ]
        return await self._protocol.call_random_walk(
            start_node, 0, DEFAULT_WALK_LENGTH, LinkType.IN
        )
