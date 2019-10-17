from abc import ABC, abstractmethod
from enum import Enum, auto
from typing import List, Tuple, Callable, Any

NodeAddr = Tuple[str, int]
NeighborsCallback = Callable[[List["INode"]], Any]


class LinkType(Enum):
    IN = auto()
    OUT = auto()


class ISwaplink(ABC):
    """
    Higher-level API.
    These are the methods offer by Swaplink for upper layers.
    """

    @abstractmethod
    async def join(self, num_links: int, bootstrap: NodeAddr = None) -> None:
        """
        Method for joining network
        :param num_links: Node's relative load
        :param bootstrap: entrypoint node. None --> first node
        :return:
        """
        pass

    @abstractmethod
    async def list_neighbours(
        self, callback_on_change: NeighborsCallback
    ) -> List["INode"]:
        """
        In addition to providing the current set of neighbors,
        a callback allows Swaplinks to inform the application
        whenever the neighbor set has changed.
        :param callback_on_change: callback called when neighbors' set changes
        :return: neighbors list
        """
        pass

    @abstractmethod
    async def select(self) -> "INode":
        """
        It randomly selects another node from the network.
        :return: randomly selected node
        """
        pass


class INode(ABC):
    @abstractmethod
    def get_addr(self) -> NodeAddr:
        pass


class ISwaplinkProtocol(ABC):
    @abstractmethod
    async def call_random_walk(
        self, node_to_ask: INode, index: int, limit: int, link_type: LinkType
    ):
        pass
