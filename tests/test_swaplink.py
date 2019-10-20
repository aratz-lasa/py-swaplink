import asyncio
import random
from asyncio import Event

import pytest

from swaplink import defaults
from tests.utils import setup_network_by_relative_loads

# for speeding up tests
defaults.HBEAT_SEND_FREQUENCY *= 0.3
defaults.HBEAT_CHECK_FREQUENCY *= 0.3
defaults.RPC_TIMEOUT *= 0.3


@pytest.mark.asyncio
async def test_swaplink_neighbour_retrieval():
    callback_flag = Event()

    def callback():
        global callback_flag
        callback_flag.set()

    my_relative_load = 3
    others_amount = 10
    others_relative_load = [random.randrange(2, 20) for _ in range(others_amount)]
    my_network, other_networks = await setup_network_by_relative_loads(
        my_relative_load, others_relative_load
    )
    await asyncio.sleep(defaults.HBEAT_CHECK_FREQUENCY * 1.5)
    neighbours = my_network.list_neighbours(callback)  # todo: callback
    assert len(neighbours) == my_relative_load


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
