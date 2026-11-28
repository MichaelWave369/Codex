"""Source-scoped relationships in creation literature, not a unified pantheon."""

import argparse
import json

# IDs deliberately distinguish local referents, titles, terms and collectives.
NODES = (
    ("gen-god", "God in Genesis 1", "Hebrew", "entity"),
    ("gen-humanity", "Humanity", "Hebrew", "group"),
    ("elohim", "Elohim", "Hebrew", "term"),
    ("yahweh", "Yahweh", "Hebrew", "entity"),
    ("el-shaddai", "El Shaddai", "Hebrew", "title"),
    ("el-elyon", "El Elyon", "Hebrew", "title"),
    ("ps82-god", "Presiding God in Psalm 82", "Hebrew", "entity"),
    ("ps82-assembly", "Assembly in Psalm 82", "Hebrew", "group"),
    ("bene-elohim", "Bene Elohim in Job", "Hebrew", "group"),
    ("athirat", "Athirat", "Ugaritic", "entity"),
    ("athirat-sons", "Sons of Athirat", "Ugaritic", "group"),
    ("enki", "Enki", "Sumerian", "entity"),
    ("namma", "Namma", "Sumerian", "entity"),
    ("ninmah", "Ninmah", "Sumerian", "entity"),
    ("birth-goddesses", "Birth goddesses", "Sumerian", "group"),
    ("sumer-humanity", "Humankind", "Sumerian", "group"),
    ("sophia", "Sophia", "Gnostic", "entity"),
    ("yaldabaoth", "Yaldabaoth", "Gnostic", "entity"),
    ("rulers", "Rulers", "Gnostic", "group"),
    ("seven-powers", "Seven powers", "Gnostic", "group"),
    ("adam", "Adam", "Gnostic", "entity"),
)

GEN = "https://www.sefaria.org/Genesis.1.26-27"
PSALM = "https://www.sefaria.org/Psalms.82"
JOB = "https://www.sefaria.org/Job.1.6"
EXODUS = "https://www.sefaria.org/Exodus.6.2-3"
GEN14 = "https://www.sefaria.org/Genesis.14.22"
ETCSL = "https://etcsl.orinst.ox.ac.uk/section1/tr112.htm"
JOHN = "https://www.gnosis.org/naghamm/apocjn-long.html"
UGARIT = "https://brill.com/previewpdf/book/9789047408000/Bej.9789004145122.i-577_034.xml"

# Each relation is a passage-specific assertion or a labeled interpretive comparison.
# No relation can be used to infer identity transitively.
EDGES = (
    ("gen-god", "designated-by", "elohim", "Genesis 1:26", GEN, "textual"),
    ("gen-god", "creates", "gen-humanity", "Genesis 1:27", GEN, "textual"),
    ("yahweh", "self-identifies-as", "el-shaddai", "Exodus 6:2-3", EXODUS, "textual"),
    ("yahweh", "associated-title", "el-elyon", "Genesis 14:22", GEN14, "textual"),
    ("ps82-god", "judges-among", "ps82-assembly", "Psalm 82:1", PSALM, "textual"),
    ("ps82-god", "designated-by", "elohim", "Psalm 82:1", PSALM, "textual"),
    ("ps82-assembly", "described-as", "elohim", "Psalm 82:1,6", PSALM, "textual"),
    ("bene-elohim", "appears-before", "yahweh", "Job 1:6", JOB, "textual"),
    ("athirat", "mother-of", "athirat-sons", "KTU 1.4 VI 46", UGARIT, "textual"),
    ("namma", "mother-of", "enki", "ETCSL 1.1.2 lines 24-37", ETCSL, "textual"),
    ("enki", "advises", "namma", "ETCSL 1.1.2 lines 24-37", ETCSL, "textual"),
    ("namma", "forms", "sumer-humanity", "ETCSL 1.1.2 lines 24-37", ETCSL, "textual"),
    ("ninmah", "assists", "namma", "ETCSL 1.1.2 lines 24-37", ETCSL, "textual"),
    ("birth-goddesses", "assist", "namma", "ETCSL 1.1.2 lines 24-37", ETCSL, "textual"),
    ("sophia", "produces", "yaldabaoth", "Apocryphon of John, long, 10-11", JOHN, "textual"),
    ("yaldabaoth", "generates", "rulers", "Apocryphon of John, long, 11-13", JOHN, "textual"),
    ("rulers", "create", "seven-powers", "Apocryphon of John, long, 13", JOHN, "textual"),
    ("seven-powers", "contribute-to", "adam", "Apocryphon of John, long, 15", JOHN, "textual"),
    ("ps82-assembly", "assembly-analogy", "athirat-sons", "Psalm 82; KTU 1.4", UGARIT, "analogy"),
    (
        "gen-humanity",
        "formation-analogy",
        "sumer-humanity",
        "Genesis 1; ETCSL 1.1.2",
        ETCSL,
        "analogy",
    ),
)

NODE_FIELDS = ("id", "label", "tradition", "kind")
EDGE_FIELDS = ("source", "relation", "target", "locator", "url", "status")


def graph(include_analogies: bool = False) -> dict:
    """Export a fresh graph; comparative analogies are explicitly opt-in."""
    return {
        "nodes": [dict(zip(NODE_FIELDS, node, strict=True)) for node in NODES],
        "edges": [
            dict(zip(EDGE_FIELDS, edge, strict=True))
            for edge in EDGES
            if include_analogies or edge[-1] == "textual"
        ],
        "genesis_addressee_count": None,
        "genesis_addressee_ids": None,
        "identity_inference": False,
    }


def neighbors(node_id: str, include_analogies: bool = False) -> dict:
    """Return direct evidence edges, never inferred transitive relationships."""
    data = graph(include_analogies)
    by_id = {node["id"]: node for node in data["nodes"]}
    if node_id not in by_id:
        raise ValueError(f"Unknown node: {node_id}")
    edges = [edge for edge in data["edges"] if node_id in (edge["source"], edge["target"])]
    return {
        "node": by_id[node_id],
        "edges": edges,
        "identity_inference": False,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--analogies", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("export")
    lookup = sub.add_parser("neighbors")
    lookup.add_argument("id")
    args = parser.parse_args()
    try:
        if args.command == "export":
            result = graph(args.analogies)
        else:
            result = neighbors(args.id, args.analogies)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
