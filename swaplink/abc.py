from abc import abstractmethod
from typing import List, Tuple


NodeAddr = Tuple[str, int]


class ISwaplink:
    """
    Higher-level API.
    These are the methods offer by Swaplink for upper layers.
    """

    @abstractmethod
    async def get_neighbour_nodes(self) -> List["INode"]:
        pass

    @abstractmethod
    async def get_random_node(self) -> "INode":
        pass


class INode:
    @abstractmethod
    def get_addr(self) -> NodeAddr:
        pass  # todo
