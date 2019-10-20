from collections import deque
from typing import Any, Tuple

from rpcudp.protocol import RPCProtocol

from swaplink import defaults
from swaplink.abc import ISwaplinkProtocol, LinkType, Node, NodeAddr, ILinkStore
from swaplink.errors import RPCError
from swaplink.utils import random_choice_safe


class SwaplinkProtocol(RPCProtocol, ISwaplinkProtocol):
    _origin_node: Node
    _link_store: ILinkStore
    _links_queue: deque
    _num_links: int

    def __init__(
        self,
        origin_node: Node,
        link_store: ILinkStore,
        links_queue: deque,
        num_links: int,
    ):
        RPCProtocol.__init__(self, defaults.RPC_TIMEOUT)
        self._origin_node = origin_node
        self._link_store = link_store
        self._links_queue = links_queue
        self._num_links = num_links

    # Calls
    async def call_random_walk(
        self,
        node_to_ask: Node,
        index: int,
        limit: int,
        link_type: LinkType,
        walk_initiator: Node = None,
    ) -> Node:
        if not walk_initiator:
            walk_initiator = self._origin_node
        result = await self.random_walk(
            node_to_ask, walk_initiator, index, limit, link_type
        )
        random_node = self._handle_call_response(result, node_to_ask)
        return Node(*random_node)

    async def call_give_me_in_node(self, node_to_ask: Node) -> None:
        result = await self.give_me_in_node(node_to_ask)
        self._handle_call_response(result, node_to_ask)

    async def call_change_your_out_node(
        self, node_to_ask: Node, new_in_node: Node
    ) -> None:
        result = await self.change_your_out_node(node_to_ask, new_in_node)
        self._handle_call_response(result, node_to_ask)

    async def call_im_your_in_node(self, node_to_ask: Node) -> None:
        result = await self.im_your_in_node(node_to_ask)
        self._handle_call_response(result, node_to_ask)

    # RPCs
    async def rpc_random_walk(
        self,
        sender: Node,
        walk_initiator: Node,
        index: int,
        limit: int,
        link_type: LinkType,
    ) -> NodeAddr:
        random_node: Node
        self._add_sender_to_queue(sender)
        if index >= limit:
            return self._origin_node
        if link_type == LinkType.IN:
            random_node = random_choice_safe(
                self._link_store.get_in_links_copy(), self._origin_node
            )
        else:
            random_node = random_choice_safe(
                self._link_store.get_out_links_copy(), self._origin_node
            )
        if random_node in {self._origin_node, sender, tuple(walk_initiator)}:
            return self._origin_node
        result_node = await self.call_random_walk(
            random_node, index + 1, limit, link_type, walk_initiator
        )
        return result_node

    async def rpc_give_me_in_node(self, sender: NodeAddr) -> None:
        self._add_sender_to_queue(sender)
        in_node_given = False
        while not in_node_given:
            try:
                random_in_node = random_choice_safe(
                    self._link_store.get_in_links_copy(), self._origin_node
                )
                if random_in_node not in {self._origin_node, sender}:
                    await self.call_change_your_out_node(random_in_node, Node(*sender))
                in_node_given = True
            except RPCError:
                pass

    async def rpc_change_your_out_node(
        self, sender: NodeAddr, new_out_node: NodeAddr
    ) -> None:
        self._add_sender_to_queue(sender)
        new_out_node = Node(*new_out_node)
        old_out_node = Node(*sender)
        if sender == self._origin_node:
            return
        if (
            self._link_store.contains_out_link(old_out_node)
            and not len(self._link_store.get_out_links_copy()) < self._num_links
        ):
            self._link_store.remove_out_link(old_out_node)
        await self.call_im_your_in_node(new_out_node)
        self._link_store.add_out_link(new_out_node)

    async def rpc_im_your_in_node(self, sender: NodeAddr) -> None:
        self._add_sender_to_queue(sender)
        if sender != self._origin_node:
            self._link_store.add_in_link(Node(*sender))

    def _handle_call_response(self, result: Tuple[int, Any], node: Node) -> Any:
        """
        If we get a response, returns it.
         Otherwise raise error and remove the node from ILinkStore.
        """
        if not result[0]:
            self._link_store.remove_link(node)
            raise RPCError
        return result[1]

    def _add_sender_to_queue(self, sender: NodeAddr) -> None:
        self._links_queue.append(Node(*sender))
