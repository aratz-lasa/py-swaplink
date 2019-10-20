import asyncio
from asyncio.protocols import BaseProtocol
from asyncio.transports import BaseTransport
from typing import List

from swaplink.abc import (
    ISwaplink,
    Node,
    LinkStore,
    NodeAddr,
    NeighborsCallback,
    LinkType,
    ISwaplinkProtocol,
)
from swaplink.defaults import DEFAULT_HOST, DEFAULT_PORT, DEFAULT_WALK_LENGTH
from swaplink.errors import RPCError
from swaplink.protocol import SwaplinkProtocol
from swaplink.utils import get_random_int_min_zero


class Swaplink(ISwaplink):
    _protocol: ISwaplinkProtocol
    _transport: BaseTransport

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self._node = Node(host, port)
        self._link_store = LinkStore()
        self._num_links = None

        self._protocol = None
        self._transport = None

    async def join(
        self, num_links: int, bootstrap_nodes: List[NodeAddr] = None
    ) -> None:
        loop = asyncio.get_event_loop()
        self._transport, protocol = await loop.create_datagram_endpoint(
            lambda: SwaplinkProtocol(self._node, self._link_store),
            local_addr=self._node,
        )
        self._protocol = self._base_protocol_cast(protocol)
        self._num_links = num_links
        if bootstrap_nodes:  # else: first node in the network
            await self._init_links(bootstrap_nodes)

    def _base_protocol_cast(self, protocol: BaseProtocol) -> ISwaplinkProtocol:
        """
        method needed because MyPy does not detect protocol is ISwpalinkProtocol too
        :param protocol: SwapLinkProtocol (BaseProtocol and ISwaplinkProtocol subtype)
        :return: MyPy correct protocol
        """
        if isinstance(protocol, ISwaplinkProtocol):
            return protocol
        raise TypeError()

    async def _init_links(self, bootstrap_nodes):
        for _ in range(self._num_links):
            random_bootstrap_addr = bootstrap_nodes[
                get_random_int_min_zero(len(bootstrap_nodes))
            ]
            random_bootstrap = Node(*random_bootstrap_addr)
            try:
                neighbor = await self._protocol.call_random_walk(
                    random_bootstrap, 0, DEFAULT_WALK_LENGTH, LinkType.IN
                )
                await self._protocol.call_give_me_in_node(neighbor)
                await self._protocol.call_im_your_in_node(neighbor)
                self._link_store.out_links.add(neighbor)
                bootstrap_nodes.append(neighbor)
            except RPCError:
                pass

    async def leave(self) -> None:
        if self._transport is not None:
            self._transport.close()

    async def list_neighbours(
        self, callback_on_change: NeighborsCallback
    ) -> List[Node]:
        self._link_store.set_callback(callback_on_change)
        return list(self._link_store.out_links)  # todo: return also in-links?

    async def select(self) -> Node:
        start_node = list(self._link_store.in_links)[
            get_random_int_min_zero(len(self._link_store.in_links))
        ]
        return await self._protocol.call_random_walk(
            start_node, 0, DEFAULT_WALK_LENGTH, LinkType.IN
        )
