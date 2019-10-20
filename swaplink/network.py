import asyncio
import time
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
from swaplink.defaults import (
    DEFAULT_HOST,
    DEFAULT_PORT,
    DEFAULT_WALK_LENGTH,
    HBEAT_CHECK_FREQUENCY,
    HBEAT_SEND_FREQUENCY,
)
from swaplink.errors import RPCError
from swaplink.protocol import SwaplinkProtocol
from swaplink.utils import random_choice_safe


class Swaplink(ISwaplink):
    _protocol: ISwaplinkProtocol
    _transport: BaseTransport
    _tasks: List[asyncio.Task]

    def __init__(self, host: str = DEFAULT_HOST, port: int = DEFAULT_PORT):
        self._node = Node(host, port)
        self._link_store = LinkStore()
        self._num_links = None

        self._protocol = None
        self._transport = None
        self._tasks = []

    async def join(
        self, num_links: int, bootstrap_nodes: List[NodeAddr] = None
    ) -> None:
        loop = asyncio.get_event_loop()
        self._transport, protocol = await loop.create_datagram_endpoint(
            lambda: SwaplinkProtocol(self._node, self._link_store, self._num_links),
            local_addr=self._node,
        )
        self._protocol = self._base_protocol_cast(protocol)
        self._num_links = num_links
        if bootstrap_nodes:  # else: first node in the network
            await self._init_links(bootstrap_nodes)

        self._run_tasks()

    async def leave(self) -> None:
        if self._transport is not None:
            self._transport.close()
        for task in self._tasks:
            task.cancel()
            await task

    def list_neighbours(self, callback_on_change: NeighborsCallback) -> List[Node]:
        self._link_store.set_callback(callback_on_change)
        return self._link_store.get_out_links_copy()  # todo: return also in-links?

    async def select(self) -> Node:
        start_node = random_choice_safe(self._link_store.get_in_links_copy())
        return await self._protocol.call_random_walk(
            start_node, 0, DEFAULT_WALK_LENGTH, LinkType.IN
        )

    async def _init_links(self, bootstrap_nodes):
        for _ in range(self._num_links):
            random_bootstrap_addr = random_choice_safe(bootstrap_nodes)
            random_bootstrap = Node(*random_bootstrap_addr)
            try:
                neighbor = await self._protocol.call_random_walk(
                    random_bootstrap, 0, DEFAULT_WALK_LENGTH, LinkType.IN
                )
                await self._protocol.call_give_me_in_node(neighbor)
                await self._protocol.call_im_your_in_node(neighbor)
                self._link_store.add_out_link(neighbor)
                bootstrap_nodes.append(neighbor)
                bootstrap_nodes = list(set(bootstrap_nodes))
            except RPCError:
                pass

    def _base_protocol_cast(self, protocol: BaseProtocol) -> ISwaplinkProtocol:
        """
        method needed because MyPy does not detect protocol is ISwpalinkProtocol too
        :param protocol: SwapLinkProtocol (BaseProtocol and ISwaplinkProtocol subtype)
        :return: MyPy correct protocol
        """
        if isinstance(protocol, ISwaplinkProtocol):
            return protocol
        raise TypeError()

    def _run_tasks(self) -> None:
        self._tasks.append(asyncio.create_task(self._update_in_links()))
        self._tasks.append(asyncio.create_task(self._update_out_links()))

    async def _update_in_links(self) -> None:
        while True:
            await asyncio.sleep(HBEAT_CHECK_FREQUENCY)
            self._remove_old_links()
            await self._add_in_links()

    async def _update_out_links(self) -> None:
        while True:
            await asyncio.sleep(HBEAT_SEND_FREQUENCY)
            await self._send_hbeats()
            await self._add_out_links()

    async def _send_hbeats(self) -> None:
        while True:
            await asyncio.sleep(HBEAT_SEND_FREQUENCY)
            for node in self._link_store.get_out_links_copy():
                try:
                    await self._protocol.call_im_your_in_node(node)
                except RPCError:
                    self._link_store.remove_out_link(node)

    def _remove_old_links(self) -> None:
        for node in self._link_store.get_in_links_copy():
            hbeat = self._link_store.get_in_link_hbeat(node)
            if time.monotonic() - hbeat >= HBEAT_CHECK_FREQUENCY:
                self._link_store.remove_in_link(node)

    async def _add_out_links(self):
        for _ in range(self._num_links - len(self._link_store.get_out_links_copy())):
            random_node = random_choice_safe(self._link_store.get_in_links_copy())
            node = await self._protocol.call_random_walk(
                random_node, 0, DEFAULT_WALK_LENGTH, LinkType.IN
            )
            await self._protocol.call_im_your_in_node(node)
            self._link_store.add_out_link(node)

    async def _add_in_links(self):
        for _ in range(self._num_links - len(self._link_store.get_in_links_copy())):
            random_node = random_choice_safe(self._link_store.get_out_links_copy())
            node = await self._protocol.call_random_walk(
                random_node, 0, DEFAULT_WALK_LENGTH, LinkType.OUT
            )
            await self._protocol.call_give_me_in_node(node)
