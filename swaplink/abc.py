import time
from abc import ABC, abstractmethod
from collections import namedtuple
from dataclasses import field
from enum import IntEnum, auto
from typing import List, Tuple, Callable, Any

from swaplink.utils import DictWithCallback

Node = namedtuple("Node", ["host", "port"])

NodeAddr = Tuple[str, int]
NeighborsCallback = Callable[[List[Node]], Any]


class LinkType(IntEnum):  # IntEnum instead of enum for compatibility with MsgPack
    IN = auto()
    OUT = auto()


class LinkStore:
    _in_links: DictWithCallback = field(default_factory=DictWithCallback)
    _out_links: DictWithCallback = field(default_factory=DictWithCallback)

    def __init__(
        self,
        in_links: DictWithCallback = None,
        out_links: DictWithCallback = None,
        callback: NeighborsCallback = None,
    ):
        self._in_links = in_links or DictWithCallback()
        self._out_links = out_links or DictWithCallback()
        self.set_callback(callback)
        self._out_links.set_callback(self._my_callback)

    def add_in_link(self, node: Node) -> None:
        self._in_links[node] = time.monotonic()

    def get_in_link_hbeat(self, node: Node) -> float:
        return self._in_links[node]

    def get_in_links_copy(self) -> List[Any]:
        return list(self._in_links.keys())

    def remove_in_link(self, node: Node) -> None:
        if self._in_links.get(node):
            del self._in_links[node]

    def contains_in_link(self, node: Node) -> bool:
        return node in self._in_links

    def add_out_link(self, node: Node) -> None:
        self._out_links[node] = time.monotonic()

    def get_out_link_hbeat(self, node: Node) -> float:
        return self._out_links[node]

    def get_out_links_copy(self) -> List[Any]:
        return list(self._out_links.keys())

    def remove_out_link(self, node: Node) -> None:
        if self._out_links.get(node):
            del self._out_links[node]

    def remove_link(self, node: Node) -> None:
        self.remove_in_link(node)
        self.remove_out_link(node)

    def contains_out_link(self, node: Node) -> bool:
        return node in self._out_links

    def set_callback(self, callback: NeighborsCallback):
        self._callback: NeighborsCallback
        self._callback = callback

    def _my_callback(self, changed_dict: DictWithCallback):
        if self._callback:
            changed_nodes: List[Node]
            changed_nodes = list(changed_dict.keys())
            self._callback(changed_nodes)


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
    def list_neighbours(self, callback_on_change: NeighborsCallback) -> List[Node]:
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
    async def call_give_me_in_node(self, node_to_ask: Node) -> None:
        pass  # todo

    @abstractmethod
    async def call_change_your_out_node(
        self, node_to_ask: Node, new_in_node: Node
    ) -> None:
        pass  # todo

    @abstractmethod
    async def call_im_your_in_node(self, node_to_ask: Node) -> None:
        pass  # todo
