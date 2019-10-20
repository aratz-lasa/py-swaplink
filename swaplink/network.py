import asyncio
import time
from asyncio.protocols import BaseProtocol
from asyncio.transports import BaseTransport
from collections import deque
from typing import List

from swaplink import defaults
from swaplink.abc import (
    ISwaplink,
    Node,
    LinkStore,
    NodeAddr,
    NeighborsCallback,
    LinkType,
    ISwaplinkProtocol,
)
from swaplink.errors import RPCError
from swaplink.protocol import SwaplinkProtocol
from swaplink.utils import random_choice_safe


class Swaplink(ISwaplink):
    _protocol: ISwaplinkProtocol
    _transport: BaseTransport
    _tasks: List[asyncio.Task]
    _links_queue: deque

    def __init__(
        self, host: str = defaults.DEFAULT_HOST, port: int = defaults.DEFAULT_PORT
    ):
        self._node = Node(host, port)
        self._link_store = LinkStore()
        self._num_links = None

        self._protocol = None
        self._transport = None
        self._tasks = []
        self._links_queue = deque()

    async def join(
        self, num_links: int, bootstrap_nodes: List[NodeAddr] = None
    ) -> None:
        loop = asyncio.get_event_loop()
        self._transport, protocol = await loop.create_datagram_endpoint(
            lambda: SwaplinkProtocol(
                self._node, self._link_store, self._links_queue, self._num_links
            ),
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
        try:
            random_node = random_choice_safe(self._link_store.get_in_links_copy())
            if not random_node:
                random_node = self._links_queue.pop()
            return await self._protocol.call_random_walk(
                random_node, 0, defaults.DEFAULT_WALK_LENGTH, LinkType.IN
            )
        except (RPCError, IndexError):
            pass
        return None  # todo: raise error?

    async def _init_links(self, bootstrap_nodes):
        for _ in range(self._num_links):
            random_bootstrap_addr = random_choice_safe(bootstrap_nodes)
            random_bootstrap = Node(*random_bootstrap_addr)
            try:
                neighbor = await self._protocol.call_random_walk(
                    random_bootstrap, 0, defaults.DEFAULT_WALK_LENGTH, LinkType.IN
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
            self._clear_in_links()
            await self._add_in_links()
            await asyncio.sleep(defaults.HBEAT_CHECK_FREQUENCY)

    async def _update_out_links(self) -> None:
        while True:
            await self._clear_out_links()
            await self._add_out_links()
            await asyncio.sleep(defaults.HBEAT_SEND_FREQUENCY)

    async def _clear_out_links(self) -> None:
        for node in self._link_store.get_out_links_copy():
            try:
                await self._protocol.call_im_your_in_node(node)
            except RPCError:
                self._link_store.remove_out_link(node)

    def _clear_in_links(self) -> None:
        for node in self._link_store.get_in_links_copy():
            hbeat = self._link_store.get_in_link_hbeat(node)
            if time.monotonic() - hbeat >= defaults.HBEAT_CHECK_FREQUENCY:
                self._link_store.remove_in_link(node)

    async def _add_out_links(self):
        for _ in range(self._num_links - len(self._link_store.get_out_links_copy())):
            try:
                random_node = random_choice_safe(self._link_store.get_in_links_copy())
                if not random_node:
                    random_node = self._links_queue.pop()
                node = await self._protocol.call_random_walk(
                    random_node, 0, defaults.DEFAULT_WALK_LENGTH, LinkType.IN
                )
                await self._protocol.call_im_your_in_node(node)
                self._link_store.add_out_link(node)
            except (RPCError, IndexError):
                pass

    async def _add_in_links(self):
        for _ in range(self._num_links - len(self._link_store.get_in_links_copy())):
            try:
                random_node = random_choice_safe(self._link_store.get_out_links_copy())
                if not random_node:
                    random_node = self._links_queue.pop()
                node = await self._protocol.call_random_walk(
                    random_node, 0, defaults.DEFAULT_WALK_LENGTH, LinkType.OUT
                )
                await self._protocol.call_give_me_in_node(node)
            except (RPCError, IndexError):
                pass
