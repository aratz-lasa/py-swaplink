from typing import Any, Tuple

from rpcudp.protocol import RPCProtocol

from swaplink.abc import ISwaplinkProtocol, LinkStore, LinkType, Node, NodeAddr
from swaplink.errors import RPCError
from swaplink.utils import get_random_int_min_zero


class SwaplinkProtocol(RPCProtocol, ISwaplinkProtocol):
    _origin_node: Node
    _link_store: LinkStore

    def __init__(self, origin_node: Node, link_store: LinkStore):
        RPCProtocol.__init__(self)
        self._origin_node = origin_node
        self._link_store = link_store

    # Calls
    async def call_random_walk(
        self, node_to_ask: Node, index: int, limit: int, link_type: LinkType
    ) -> Node:
        random_node: NodeAddr = None
        while not random_node:
            result = await self.random_walk(node_to_ask, index, limit, link_type)
            random_node = self.handle_call_response(result, node_to_ask)
        return Node(*random_node)

    async def call_give_me_in_node(self, node_to_ask: Node) -> Node:
        result = await self.give_me_in_node(node_to_ask)
        in_node = self.handle_call_response(result, node_to_ask)
        return Node(*in_node)

    async def call_change_your_out_node(
        self, node_to_ask: Node, new_in_node: Node
    ) -> None:
        result = await self.change_your_out_node(node_to_ask, new_in_node)
        self.handle_call_response(result, node_to_ask)

    async def call_im_your_in_node(self, node_to_ask: Node) -> None:
        result = await self.im_your_in_node(node_to_ask)
        self.handle_call_response(result, node_to_ask)

    # RPCs
    async def rpc_random_walk(
        self, sender: NodeAddr, index: int, limit: int, link_type: LinkType
    ) -> NodeAddr:
        random_node: Node
        if index >= limit:
            return self._origin_node
        if link_type == LinkType.IN:
            random_node = list(self._link_store.in_links)[
                get_random_int_min_zero(len(self._link_store.in_links))
            ]
        else:
            random_node = list(self._link_store.in_links)[
                get_random_int_min_zero(len(self._network._out_links))
            ]
        result_node = await self.call_random_walk(
            random_node, index + 1, limit, link_type
        )
        return result_node

    async def rpc_give_me_in_node(self, sender: NodeAddr) -> NodeAddr:
        node_stole = False
        while not node_stole:
            try:
                random_in_node = list(self._link_store.in_links)[
                    get_random_int_min_zero(len(self._link_store.in_links))
                ]
                await self.call_change_your_out_node(random_in_node, Node(*sender))
                return random_in_node
            except RPCError:
                pass
        assert False  # otherwise mypy raises error

    async def rpc_change_your_out_node(
        self, sender: NodeAddr, new_in_node: NodeAddr
    ) -> None:
        new_in_node = Node(*new_in_node)
        old_in_node = Node(*sender)
        if old_in_node in self._link_store.in_links:
            self._link_store.in_links.remove(old_in_node)
        await self.call_im_your_in_node(new_in_node)
        self._link_store.out_links.add(new_in_node)

    async def rpc_im_your_in_node(self, sender: NodeAddr) -> None:
        self._link_store.in_links.add(sender)

    def handle_call_response(self, result: Tuple[int, Any], node: Node) -> Any:
        """
        If we get a response, returns it.
         Otherwise raise error and remove the node from LinkStore.
        """
        if not result[0]:
            self._link_store.remove_link(node)
            raise RPCError
        return result[1]
