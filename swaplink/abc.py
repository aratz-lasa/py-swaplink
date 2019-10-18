from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum, auto
from typing import List, Tuple, Callable, Any

NodeAddr = Tuple[str, int]
NeighborsCallback = Callable[[List["Node"]], Any]


class LinkType(Enum):
    IN = auto()
    OUT = auto()


@dataclass
class LinkStore:
    in_links: List["Node"] = field(default_factory=list)
    out_links: List["Node"] = field(default_factory=list)


class ISwaplink(ABC):
    """
    Higher-level API.
    These are the methods offer by Swaplink for upper layers.
    """

    _relative_load: int
    _node: "Node"
    _link_store: LinkStore

    @abstractmethod
    async def join(self, num_links: int, bootstrap: List[NodeAddr] = None) -> None:
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
    ) -> List["Node"]:
        """
        In addition to providing the current set of neighbors,
        a callback allows Swaplinks to inform the application
        whenever the neighbor set has changed.
        :param callback_on_change: callback called when neighbors' set changes
        :return: neighbors list
        """
        pass

    @abstractmethod
    async def select(self) -> "Node":
        """
        It randomly selects another node from the network.
        :return: randomly selected node
        """
        pass


@dataclass(eq=True)
class Node(ABC):
    host: str
    port: int

    def get_addr(self) -> NodeAddr:
        return self.host, self.port


class ISwaplinkProtocol(ABC):
    @abstractmethod
    async def call_random_walk(
        self, node_to_ask: Node, index: int, limit: int, link_type: LinkType
    ):
        pass

    @abstractmethod
    async def call_give_me_in_node(self, node_to_ask: Node) -> Node:
        pass  # todo

    @abstractmethod
    async def call_change_your_out_node(
        self, node_to_ask: Node, new_in_node: Node
    ) -> None:
        pass  # todo

    @abstractmethod
    async def call_im_your_in_node(self, node_to_ask: Node) -> None:
        pass  # todo
