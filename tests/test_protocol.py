import pytest

from swaplink.abc import LinkType
from tests.utils import setup_n_protocols, close_transports


@pytest.mark.asyncio
async def test_random_walk():
    protocols, transports = await setup_n_protocols(3)
    protocol_a, protocol_b, protocol_c = protocols
    walk_length = 0
    random_node = await protocol_a.call_random_walk(
        protocol_b._origin_node, 0, 0 + walk_length, LinkType.IN
    )
    assert random_node == protocol_b._origin_node

    walk_length = 1
    protocol_b._link_store.add_in_link(protocol_c._origin_node)
    random_node = await protocol_a.call_random_walk(
        protocol_b._origin_node, 0, 0 + walk_length, LinkType.IN
    )
    assert random_node == protocol_c._origin_node

    # clean up
    close_transports(transports)


@pytest.mark.asyncio
async def test_im_your_in_node():
    protocols, transports = await setup_n_protocols(3)
    protocol_a, protocol_b, protocol_c = protocols

    await protocol_a.call_im_your_in_node(protocol_b._origin_node)

    assert protocol_b._link_store.contains_in_link(protocol_a._origin_node)

    # clean up
    close_transports(transports)


@pytest.mark.asyncio
async def test_change_your_out_node():
    protocols, transports = await setup_n_protocols(3)
    protocol_a, protocol_b, protocol_c = protocols
    protocol_c._link_store.add_in_link(protocol_b._origin_node)

    await protocol_a.call_change_your_out_node(
        protocol_c._origin_node, protocol_a._origin_node
    )

    assert not protocol_c._link_store.contains_out_link(protocol_b._origin_node)
    assert protocol_c._link_store.contains_out_link(protocol_a._origin_node)
    assert protocol_a._link_store.contains_in_link(protocol_c._origin_node)

    # clean up
    close_transports(transports)


@pytest.mark.asyncio
async def test_give_me_in_node():
    protocols, transports = await setup_n_protocols(3)
    protocol_a, protocol_b, protocol_c = protocols
    protocol_c._link_store.add_in_link(protocol_b._origin_node)

    await protocol_a.call_give_me_in_node(protocol_b._origin_node)
    assert (
        len(protocol_a._link_store.get_in_links_copy()) == 0
    )  # B has no in-link to give

    await protocol_a.call_give_me_in_node(protocol_c._origin_node)

    assert not protocol_c._link_store.contains_out_link(protocol_b._origin_node)
    assert protocol_b._link_store.contains_out_link(protocol_a._origin_node)
    assert protocol_a._link_store.contains_in_link(protocol_b._origin_node)

    # clean up
    close_transports(transports)
