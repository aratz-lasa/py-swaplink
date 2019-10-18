from typing import List

from swaplink import Swaplink
from swaplink.abc import LinkStore
from swaplink.abc import Node
from swaplink.protocol import SwaplinkProtocol


async def setup_network_by_relative_loads(
    my_relative_load: int, others_relative_loads: List[int]
) -> Swaplink:
    bootstrap = Swaplink(others_relative_loads[0])
    for load in others_relative_loads:
        network = Swaplink()
        await network.join(load, bootstrap._node.get_addr())
    # todo: init nodes?
    return Swaplink(my_relative_load, bootstrap._node.get_addr())


def setup_n_protocols(n: int) -> List[SwaplinkProtocol]:
    localhost = "127.0.0.1"
    protocols = []
    for i in range(n):
        node = Node(localhost, 5678 + i)
        link_store = LinkStore()
        protocols.append(SwaplinkProtocol(node, link_store))
    return protocols
