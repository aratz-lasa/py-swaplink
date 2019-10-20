from abc import ABC, abstractmethod
from typing import List, Tuple, Callable, Any

from swaplink.data_objects import Node, LinkType

NodeAddr = Tuple[str, int]
NeighborsCallback = Callable[[List["Node"]], Any]


class ISwaplink(ABC):
    """
    Higher-level API.
    These are the methods offer by Swaplink for upper layers.
    """

    _num_links: int
    _node: Node
    _link_store: "ILinkStore"

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
        self,
        node_to_ask: Node,
        index: int,
        limit: int,
        link_type: LinkType,
        walk_initiator: Node = None,
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


class ILinkStore(ABC):
    @abstractmethod
    def add_in_link(self, node: Node) -> None:
        pass

    @abstractmethod
    def get_in_link_hbeat(self, node: Node) -> float:
        pass

    @abstractmethod
    def get_in_links_copy(self) -> List[Any]:
        pass

    @abstractmethod
    def remove_in_link(self, node: Node) -> None:
        pass

    @abstractmethod
    def contains_in_link(self, node: Node) -> bool:
        pass

    @abstractmethod
    def add_out_link(self, node: Node) -> None:
        pass

    @abstractmethod
    def get_out_link_hbeat(self, node: Node) -> float:
        pass

    @abstractmethod
    def get_out_links_copy(self) -> List[Any]:
        pass

    @abstractmethod
    def remove_out_link(self, node: Node) -> None:
        pass

    @abstractmethod
    def remove_link(self, node: Node) -> None:
        pass

    @abstractmethod
    def contains_out_link(self, node: Node) -> bool:
        pass

    @abstractmethod
    def set_callback(self, callback: NeighborsCallback) -> None:
        pass
