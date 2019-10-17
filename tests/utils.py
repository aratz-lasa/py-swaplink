from typing import List

from swaplink import Swaplink


async def setup_network_by_relative_loads(
    my_relative_load: int, others_relative_loads: List[int]
) -> Swaplink:
    bootstrap = Swaplink(others_relative_loads[0])
    for load in others_relative_loads:
        network = Swaplink()
        await network.join(load, bootstrap._node.get_addr())
    # todo: init nodes?
    return Swaplink(my_relative_load, bootstrap._node.get_addr())
