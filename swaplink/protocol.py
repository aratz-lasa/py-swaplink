from rpcudp.protocol import RPCProtocol

from swaplink.abc import INode, LinkType


class SwaplinkProtocl(RPCProtocol):
    def __init__(self):
        RPCProtocol.__init__(self)
        # todo

    async def call_random_walk(
        self, node_to_ask: INode, index: int, limit: int, link_type: LinkType
    ):
        random_node: INode = None
        while not random_node:
            random_node = await self.random_walk(
                node_to_ask.get_addr(), index, limit, link_type
            )
        return random_node

    async def rpc_random_walk(self, index: int, limit: int, link_type: LinkType):
        pass  # todo
