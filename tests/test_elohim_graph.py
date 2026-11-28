import pytest

from codex.elohim_graph import graph, neighbors


def test_unique_nodes_and_valid_edges():
    data = graph(True)
    ids = {node["id"] for node in data["nodes"]}
    assert len(ids) == len(data["nodes"])
    for edge in data["edges"]:
        assert edge["source"] in ids
        assert edge["target"] in ids
        assert edge["locator"]
        assert edge["url"].startswith("https://")


def test_analogies_opt_in_and_not_identity():
    default = graph()
    expanded = graph(True)
    assert all(edge["status"] == "textual" for edge in default["edges"])
    assert len(expanded["edges"]) == len(default["edges"]) + 2
    assert expanded["identity_inference"] is False


def test_shared_term_does_not_merge_entities():
    result = neighbors("elohim")
    assert result["node"]["kind"] == "term"
    assert {edge["source"] for edge in result["edges"]} == {
        "gen-god",
        "ps82-god",
        "ps82-assembly",
    }
    assert result["identity_inference"] is False


def test_genesis_addressees_remain_unknown():
    data = graph(True)
    assert data["genesis_addressee_count"] is None
    assert data["genesis_addressee_ids"] is None
    assert not any(edge["relation"] == "same-as" for edge in data["edges"])


def test_unknown_node_and_detached_graph():
    with pytest.raises(ValueError, match="Unknown node"):
        neighbors("missing")
    graph()["nodes"].clear()
    assert graph()["nodes"]
