import random

import pytest

from tests.utils import setup_network_by_relative_loads


@pytest.mark.asyncio
async def test_swaplink_neighbour_retrieval():
    my_relative_load = 5
    others_amount = 10
    others_relative_load = [random.randrange(2, 20) for _ in range(others_amount)]
    network = await setup_network_by_relative_loads(
        my_relative_load, others_relative_load
    )
    neighbours = await network.list_neighbours()
    assert len(neighbours) == neighbours


@pytest.mark.asyncio
async def test_swaplink_random_selection():
    my_relative_load = 5
    others_amount = 10
    others_relative_load = [random.randrange(2, 20) for _ in range(others_amount)]
    network = await setup_network_by_relative_loads(
        my_relative_load, others_relative_load
    )
    random_nodes = []
    for _ in range(others_amount):
        random_nodes.append(await network.select())
    unique_nodes = set(random_nodes)

    RANDOMNESS = 0.8  # todo: implement good randomness test

    assert len(unique_nodes) > (RANDOMNESS * others_amount)
