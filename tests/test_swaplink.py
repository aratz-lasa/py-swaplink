import asyncio
import random
from asyncio import Event
from typing import List, Any

import pytest

from swaplink import defaults
from tests.utils import setup_network_by_relative_loads

# for speeding up tests
defaults.HBEAT_SEND_FREQUENCY *= 0.3
defaults.HBEAT_CHECK_FREQUENCY *= 0.3
defaults.RPC_TIMEOUT *= 0.3


@pytest.mark.asyncio
async def test_swaplink_neighbour_retrieval():
    my_num_links = 3
    others_amount = 10
    others_relative_load = [random.randrange(2, 20) for _ in range(others_amount)]
    my_network, other_networks = await setup_network_by_relative_loads(
        my_num_links, others_relative_load
    )
    await asyncio.sleep(defaults.HBEAT_CHECK_FREQUENCY * 1.5)
    neighbours = my_network.list_neighbours()
    assert len(neighbours) >= int(
        my_num_links * 0.8
    )  # todo: how much links should it have after two cycles?

    # clean up
    await my_network.leave()
    for network in other_networks:
        await network.leave()


@pytest.mark.asyncio
async def test_swaplink_callback():
    callback_flag = Event()
    callback_neighbors = []

    def callback(neighbors: List[Any]):
        nonlocal callback_flag, callback_neighbors
        callback_neighbors = neighbors
        callback_flag.set()

    my_num_links = 3
    others_amount = 10
    others_relative_load = [random.randrange(2, 20) for _ in range(others_amount)]
    my_network, other_networks = await setup_network_by_relative_loads(
        my_num_links, others_relative_load
    )
    my_network.list_neighbours(callback)
    await asyncio.sleep(defaults.HBEAT_CHECK_FREQUENCY * 1.5)
    cuurent_neighbors = my_network.list_neighbours(callback)

    assert callback_flag.is_set()
    assert callback_neighbors == cuurent_neighbors

    # clean up
    await my_network.leave()
    for network in other_networks:
        await network.leave()


@pytest.mark.asyncio
async def test_swaplink_random_selection():
    my_relative_load = 5
    others_amount = 10
    others_relative_load = [random.randrange(2, 20) for _ in range(others_amount)]
    my_network, other_networks = await setup_network_by_relative_loads(
        my_relative_load, others_relative_load
    )
    await asyncio.sleep(defaults.HBEAT_CHECK_FREQUENCY * 1.5)

    random_nodes = []
    for _ in range(others_amount):
        random_nodes.append(await my_network.select())
    unique_nodes = set(random_nodes)

    RANDOMNESS = 0.5  # todo: implement good randomness test

    assert len(unique_nodes) >= (RANDOMNESS * others_amount)

    # clean up
    await my_network.leave()
    for network in other_networks:
        await network.leave()


@pytest.mark.asyncio
async def test_swaplink_leave():
    my_num_links = 3
    others_amount = 10
    others_relative_load = [random.randrange(2, 20) for _ in range(others_amount)]
    my_network, other_networks = await setup_network_by_relative_loads(
        my_num_links, others_relative_load
    )
    await asyncio.sleep(defaults.HBEAT_CHECK_FREQUENCY * 1.5)

    await my_network.leave()
    for network in other_networks:
        await network.leave()
