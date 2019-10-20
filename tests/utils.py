import asyncio
from asyncio.transports import DatagramTransport
from collections import deque
from typing import List, Tuple

from swaplink import Swaplink
from swaplink.core import LinkStore
from swaplink.abc import Node
from swaplink.protocol import SwaplinkProtocol


async def setup_network_by_relative_loads(
    my_relative_load: int, others_relative_loads: List[int]
) -> Tuple[Swaplink, List[Swaplink]]:
    localhost = "127.0.0.1"
    first_port = 5678
    port_i = 0
    bootstrap = Swaplink(localhost, first_port + port_i)
    await bootstrap.join(others_relative_loads[0])
    other_networks = [bootstrap]
    for load in others_relative_loads[1:]:
        port_i += 1
        network = Swaplink(localhost, port=first_port + port_i)
        await network.join(load, [bootstrap._node])
        other_networks.append(network)
    my_network = Swaplink(localhost, port=first_port + port_i + 1)
    await my_network.join(my_relative_load, [bootstrap._node])
    return my_network, other_networks


async def setup_n_protocols(
    n: int
) -> Tuple[List[SwaplinkProtocol], List[DatagramTransport]]:
    localhost = "127.0.0.1"
    protocols = []
    transports = []
    loop = asyncio.get_event_loop()
    for i in range(n):
        node = Node(localhost, 5678 + i)
        link_store = LinkStore()
        transport, protocol = await loop.create_datagram_endpoint(
            lambda: SwaplinkProtocol(node, link_store, deque(), n), local_addr=node
        )
        protocols.append(protocol)
        transports.append(transport)
    return protocols, transports


def close_transports(transports: List[DatagramTransport]) -> None:
    for udp in transports:
        udp.close()
