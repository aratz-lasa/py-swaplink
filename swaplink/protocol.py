from typing import Any, Tuple

from rpcudp.protocol import RPCProtocol

from swaplink.defaults import RPC_TIMEOUT
from swaplink.abc import ISwaplinkProtocol, LinkStore, LinkType, Node, NodeAddr
from swaplink.errors import RPCError
from swaplink.utils import random_choice_safe


class SwaplinkProtocol(RPCProtocol, ISwaplinkProtocol):
    _origin_node: Node
    _link_store: LinkStore
    _num_links: int

    def __init__(self, origin_node: Node, link_store: LinkStore, num_links: int):
        RPCProtocol.__init__(self, RPC_TIMEOUT)
        self._origin_node = origin_node
        self._link_store = link_store
        self._num_links = num_links

    # Calls
    async def call_random_walk(
        self, node_to_ask: Node, index: int, limit: int, link_type: LinkType
    ) -> Node:
        result = await self.random_walk(node_to_ask, index, limit, link_type)
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
        self, sender: NodeAddr, index: int, limit: int, link_type: LinkType
    ) -> NodeAddr:
        random_node: Node
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
        if random_node == self._origin_node or random_node == sender:
            return self._origin_node
        result_node = await self.call_random_walk(
            random_node, index + 1, limit, link_type
        )
        return result_node

    async def rpc_give_me_in_node(self, sender: NodeAddr) -> None:
        in_node_given = False
        while not in_node_given:
            try:
                random_in_node = random_choice_safe(
                    self._link_store.get_in_links_copy(), self._origin_node
                )
                if random_in_node != self._origin_node and random_in_node != sender:
                    await self.call_change_your_out_node(random_in_node, Node(*sender))
                in_node_given = True
            except RPCError:
                pass

    async def rpc_change_your_out_node(
        self, sender: NodeAddr, new_out_node: NodeAddr
    ) -> None:
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
        if sender != self._origin_node:
            self._link_store.add_in_link(Node(*sender))

    def _handle_call_response(self, result: Tuple[int, Any], node: Node) -> Any:
        """
        If we get a response, returns it.
         Otherwise raise error and remove the node from LinkStore.
        """
        if not result[0]:
            self._link_store.remove_link(node)
            raise RPCError
        return result[1]
