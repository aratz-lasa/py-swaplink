import pytest

from swaplink.abc import LinkType
from tests.utils import setup_n_protocols


@pytest.mark.asyncio
async def test_random_walk():
    protocol_a, protocol_b, protocol_c = setup_n_protocols(3)
    walk_length = 0
    random_node = await protocol_a.call_random_walk(
        protocol_b._origin_node, 0, 0 + walk_length, LinkType.IN
    )
    assert random_node == protocol_b._origin_node

    walk_length = 1
    protocol_b._link_store.in_links.append(protocol_c._origin_node)
    random_node = await protocol_a.call_random_walk(
        protocol_b._origin_node, 0, 0 + walk_length, LinkType.IN
    )
    assert random_node == protocol_c._origin_node


@pytest.mark.asyncio
async def test_im_your_in_node():
    protocol_a, protocol_b, protocol_c = setup_n_protocols(3)

    await protocol_b.call_im_your_in_node(protocol_b._origin_node)

    assert protocol_a._origin_node in protocol_b._link_store.in_links


@pytest.mark.asyncio
async def test_change_your_out_node():
    protocol_a, protocol_b, protocol_c = setup_n_protocols(3)
    protocol_c._link_store.in_links.append(protocol_b._origin_node)

    await protocol_a.call_change_your_out_node(
        protocol_c._origin_node, protocol_a._origin_node
    )

    assert protocol_b._origin_node not in protocol_c._link_store.out_links
    assert protocol_a._origin_node in protocol_c._link_store.out_links
    assert protocol_c._origin_node in protocol_a._link_store.in_links


@pytest.mark.asyncio
async def test_give_me_in_node():
    protocol_a, protocol_b, protocol_c = setup_n_protocols(3)
    protocol_c._link_store.in_links.append(protocol_b._origin_node)

    with pytest.raises(Exception):
        in_node = await protocol_a.call_give_me_in_node(protocol_b._origin_node)

    in_node = await protocol_a.call_give_me_in_node(protocol_c._origin_node)

    assert in_node == protocol_b._origin_node
    assert protocol_b._origin_node not in protocol_c._link_store.out_links
    assert protocol_a._origin_node in protocol_c._link_store.out_links
    assert protocol_c._origin_node in protocol_a._link_store.in_links
