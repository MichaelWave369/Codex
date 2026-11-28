"""Curated creation-account observations; not a historical truth engine."""

import argparse
import json

RECORDS = (
    {
        "id": "genesis-1",
        "tradition": "Hebrew",
        "locator": "Genesis 1:26-27",
        "url": "https://classic.net.bible.org/passage.php?passage=Gen+1%3A26",
        "relation": "anchor",
        "motifs": ["plural-declaration", "divine-likeness"],
        "observation": ("First-person plural speech in 1:26; singular creation verb in 1:27."),
        "count": None,
        "count_scope": "participants addressed in 1:26",
        "limit": "No addressee is named or counted; speech does not prove joint agency.",
    },
    {
        "id": "deuteronomy-32",
        "tradition": "Hebrew",
        "locator": "Deuteronomy 32:8-9; Tov, textual comparison",
        "url": "https://thetorah.com/article/the-sons-of-israel-or-god-deuteronomy-32-8",
        "relation": "manuscript-variant",
        "motifs": ["divine-assembly", "distributed-authority"],
        "observation": (
            "The Masoretic reading refers to Israel's sons; a Qumran reading "
            "refers to divine sons; Greek witnesses also reflect divine beings."
        ),
        "count": None,
        "count_scope": "divine beings in the passage",
        "limit": "A national allocation text, not a count of creators in Genesis.",
    },
    {
        "id": "enki-ninmah",
        "tradition": "Sumerian",
        "locator": "ETCSL 1.1.2, lines 24-37",
        "url": "https://etcsl.orinst.ox.ac.uk/section1/tr112.htm",
        "relation": "comparative-parallel",
        "motifs": ["collaborative-formation", "clay", "labor"],
        "observation": "Enki advises Namma on forming humans with birth goddesses.",
        "count": None,
        "count_scope": "all participants in human formation",
        "limit": "Motif overlap cannot establish identity or literary dependence.",
    },
    {
        "id": "atrahasis",
        "tradition": "Akkadian",
        "locator": "Atraḫasis I, lines 189-240 (SEAL composite)",
        "url": "https://seal.huji.ac.il/index.php/node/1515",
        "relation": "comparative-parallel",
        "motifs": ["collaborative-formation", "clay", "divine-substance", "labor"],
        "observation": "Human formation involves a birth goddess, clay and divine material.",
        "count": None,
        "count_scope": "all divine participants in human formation",
        "limit": "Not a biological mechanism or evidence of shared historical actors.",
    },
    {
        "id": "philo",
        "tradition": "Hellenistic Jewish",
        "locator": "Philo, On the Creation, sections 72-75",
        "url": "https://adfonteslibrary.org/work-st-philo-the-creation-of-the-world",
        "relation": "later-interpretation",
        "motifs": ["plural-declaration", "collaborative-formation"],
        "observation": "Philo interprets the plural as God involving assistants.",
        "count": None,
        "count_scope": "assistants in Philo's interpretation",
        "limit": "Reception history, not an independent witness to Genesis's composition.",
    },
    {
        "id": "apocryphon-john",
        "tradition": "Gnostic",
        "locator": "Apocryphon of John, long recension, creation of Adam",
        "url": "https://www.gnosis.org/naghamm/apocjn-long.html",
        "relation": "later-interpretation",
        "motifs": ["collaborative-formation", "divine-likeness", "animation"],
        "observation": (
            "Seven powers contribute to Adam's formation; further beings "
            "participate, and animation is described separately."
        ),
        "count": 7,
        "count_scope": "powers contributing to Adam's formation in this recension",
        "limit": "Seven is a local narrative count, not the total or Genesis addressee count.",
    },
)


def record(record_id: str) -> dict:
    """Return a detached record so callers cannot alter the curated registry."""
    for item in RECORDS:
        if item["id"] == record_id:
            return json.loads(json.dumps(item))
    raise ValueError(f"Unknown record: {record_id}")


def compare(left: str, right: str) -> dict:
    """Compare annotated motifs without promoting them to identity claims."""
    a, b = record(left), record(right)
    x, y = set(a["motifs"]), set(b["motifs"])
    return {
        "left": a,
        "right": b,
        "shared_motifs": sorted(x & y),
        "left_only": sorted(x - y),
        "right_only": sorted(y - x),
        "genesis_addressee_count": None,
        "inference_boundary": "Shared motifs do not establish identity or dependence.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    show = sub.add_parser("show")
    show.add_argument("id")
    comparison = sub.add_parser("compare")
    comparison.add_argument("left")
    comparison.add_argument("right")
    args = parser.parse_args()
    try:
        if args.command == "list":
            result = [record(item["id"]) for item in RECORDS]
        elif args.command == "show":
            result = record(args.id)
        else:
            result = compare(args.left, args.right)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
