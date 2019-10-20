from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import dataclass, field
from enum import IntEnum, auto
from typing import List, Tuple, Callable, Any

from swaplink.utils import ListWithCallback

NodeAddr = Tuple[str, int]
NeighborsCallback = Callable[[List["Node"]], Any]


class LinkType(IntEnum):  # IntEnum instead of enum for compatibility with MsgPack
    IN = auto()
    OUT = auto()


Node = namedtuple("Node", ["host", "port"])


@dataclass
class LinkStore:
    in_links: ListWithCallback = field(default_factory=ListWithCallback)
    out_links: ListWithCallback = field(default_factory=ListWithCallback)

    def remove_link(self, node: Node) -> None:
        if node in self.in_links:
            self.in_links.remove(node)
        if node in self.out_links:
            self.out_links.remove(node)

    def set_callback(self, callback):
        self.in_links.set_callback(callback)
        self.out_links.set_callback(callback)


class ISwaplink(ABC):
    """
    Higher-level API.
    These are the methods offer by Swaplink for upper layers.
    """

    _num_links: int
    _node: Node
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
    async def leave(self) -> None:
        pass

    @abstractmethod
    async def list_neighbours(
        self, callback_on_change: NeighborsCallback
    ) -> List[Node]:
        """
        In addition to providing the current set of neighbors,
        a callback allows Swaplinks to inform the application
        whenever the neighbor set has changed.
        :param callback_on_change: callback called when neighbors' set changes
        :return: neighbors list
        """
        pass

    @abstractmethod
    async def select(self) -> Node:
        """
        It randomly selects another node from the network.
        :return: randomly selected node
        """
        pass


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
