from rpcudp.protocol import RPCProtocol

from swaplink.abc import ISwaplinkProtocol, LinkStore, LinkType, Node
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
        random_node: Node = None
        while not random_node:
            random_node = await self.random_walk(
                node_to_ask.get_addr(), index, limit, link_type
            )
        return random_node

    async def call_give_me_in_node(self, node_to_ask: Node) -> Node:
        return await self.give_me_in_node(node_to_ask, self._origin_node)

    async def call_change_your_out_node(
        self, node_to_ask: Node, new_in_node: Node
    ) -> None:
        await self.change_your_out_node(node_to_ask, self._origin_node, new_in_node)

    async def call_im_your_in_node(self, node_to_ask: Node) -> None:
        await self.im_your_in_node(node_to_ask, self._origin_node)

    # RPCs
    async def rpc_random_walk(
        self, index: int, limit: int, link_type: LinkType
    ) -> Node:
        random_node: Node
        if link_type is LinkType.IN:
            random_node = self._link_store.in_links[
                get_random_int_min_zero(len(self._link_store.in_links))
            ]
        else:
            random_node = self._link_store.in_links[
                get_random_int_min_zero(len(self._network._out_links))
            ]
        if index < limit:
            return await self.call_random_walk(random_node, index + 1, limit, link_type)
        else:
            return self._origin_node

    async def rpc_give_me_in_node(self, orign_node: Node) -> Node:
        node_stole = False
        while not node_stole:
            try:
                random_in_node = self._link_store.in_links[
                    get_random_int_min_zero(len(self._link_store.in_links))
                ]
                await self.call_change_your_out_node(random_in_node, orign_node)
                return random_in_node
            except Exception:
                pass
        assert False  # otherwise mypy raises error

    async def rpc_change_your_out_node(
        self, old_in_node: Node, new_in_node: Node
    ) -> None:
        if old_in_node in self._link_store.in_links:
            self._link_store.in_links.remove(old_in_node)
        await self.call_im_your_in_node(new_in_node)
        self._link_store.in_links.append(new_in_node)

    async def rpc_im_your_in_node(self, in_node: Node) -> None:
        self._link_store.in_links.append(in_node)
