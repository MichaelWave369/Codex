"""Passage-scoped creation sequence comparisons; no inferred historical mechanisms."""

import argparse
import json
from copy import deepcopy

ACCOUNTS = (
    {
        "id": "genesis-1",
        "tradition": "Hebrew",
        "edition": "Masoretic text, Sefaria",
        "url": "https://www.sefaria.org/Genesis.1.26-28",
        "boundary": (
            "Plural speech does not identify the addressees; creation is narrated "
            "in singular grammar."
        ),
        "steps": [
            {
                "stage": "intention",
                "actor": "God",
                "summary": "Humanity is proposed in divine likeness.",
                "locator": "Genesis 1:26",
                "mode": "proposed",
            },
            {
                "stage": "purpose",
                "actor": "God",
                "summary": "Human dominion is proposed.",
                "locator": "Genesis 1:26",
                "mode": "proposed",
            },
            {
                "stage": "formation",
                "actor": "God",
                "summary": "Humanity, male and female, is created.",
                "locator": "Genesis 1:27",
                "mode": "narrated",
            },
            {
                "stage": "purpose",
                "actor": "God",
                "summary": "Humans are blessed and given dominion.",
                "locator": "Genesis 1:28",
                "mode": "narrated",
            },
        ],
    },
    {
        "id": "genesis-2",
        "tradition": "Hebrew",
        "edition": "Masoretic text, Sefaria",
        "url": "https://www.sefaria.org/Genesis.2.7-15",
        "boundary": "Separate passage; no composite sequence or creator count inferred.",
        "steps": [
            {
                "stage": "material",
                "actor": "Yahweh God",
                "summary": "Ground dust is the formation material.",
                "locator": "Genesis 2:7",
                "mode": "narrated",
            },
            {
                "stage": "formation",
                "actor": "Yahweh God",
                "summary": "The human is formed.",
                "locator": "Genesis 2:7",
                "mode": "narrated",
            },
            {
                "stage": "animation",
                "actor": "Yahweh God",
                "summary": "Divine breath makes the human a living being.",
                "locator": "Genesis 2:7",
                "mode": "narrated",
            },
            {
                "stage": "purpose",
                "actor": "Yahweh God",
                "summary": "The human is placed in the garden to tend and keep it.",
                "locator": "Genesis 2:15",
                "mode": "narrated",
            },
        ],
    },
    {
        "id": "enki-ninmah",
        "tradition": "Sumerian",
        "edition": "ETCSL 1.1.2, Oxford",
        "url": "https://etcsl.orinst.ox.ac.uk/section1/tr112.htm",
        "boundary": (
            "The initial creation instructions are followed by fragmentary lines; "
            "do not fill the gap."
        ),
        "steps": [
            {
                "stage": "intention",
                "actor": "Namma",
                "summary": "Requests relief for the gods from their work.",
                "locator": "lines 12-23",
                "mode": "narrated",
            },
            {
                "stage": "design",
                "actor": "Enki",
                "summary": "Considers the problem and prepares birth goddesses.",
                "locator": "lines 24-37",
                "mode": "narrated",
            },
            {
                "stage": "purpose",
                "actor": "Enki",
                "summary": "Assigns intended basket labor to the creature.",
                "locator": "lines 24-37",
                "mode": "proposed",
            },
            {
                "stage": "material",
                "actor": "Enki to Namma",
                "summary": "Prescribes clay from the abzu.",
                "locator": "lines 24-37",
                "mode": "proposed",
            },
            {
                "stage": "formation",
                "actor": "Namma and assistants",
                "summary": "Formation and birth are instructed.",
                "locator": "lines 24-37",
                "mode": "proposed",
            },
            {
                "stage": "purpose",
                "actor": "Namma and Ninmah",
                "summary": "Fate and labor are prescribed again.",
                "locator": "lines 24-37",
                "mode": "proposed",
            },
        ],
    },
    {
        "id": "atrahasis",
        "tradition": "Akkadian",
        "edition": "SEAL, Atraḫasis I composite",
        "url": "https://seal.huji.ac.il/index.php/node/1515",
        "boundary": (
            "Composite edition with variants; no separate animation event is asserted here."
        ),
        "steps": [
            {
                "stage": "intention",
                "actor": "Gods",
                "summary": "Summon the birth goddess to create humans.",
                "locator": "I 188-190",
                "mode": "narrated",
            },
            {
                "stage": "purpose",
                "actor": "Gods",
                "summary": "Intend humans to take on divine labor.",
                "locator": "I 191-197",
                "mode": "proposed",
            },
            {
                "stage": "material",
                "actor": "Enki and gods",
                "summary": "Clay and divine flesh and blood are prescribed.",
                "locator": "I 198-217",
                "mode": "proposed",
            },
            {
                "stage": "material",
                "actor": "Gods and birth goddess",
                "summary": "A deity is slain and divine matter mixed with clay.",
                "locator": "I 221-230",
                "mode": "narrated",
            },
            {
                "stage": "formation",
                "actor": "Birth goddess and helpers",
                "summary": "The birth process produces human beings.",
                "locator": "I 246-293",
                "mode": "narrated",
            },
        ],
    },
    {
        "id": "apocryphon-john",
        "tradition": "Gnostic",
        "edition": "Long recension, Waldstein and Wisse",
        "url": "https://www.gnosis.org/naghamm/apocjn-long.html",
        "boundary": "Later reception account, not an earlier witness to Genesis.",
        "steps": [
            {
                "stage": "intention",
                "actor": "Rulers",
                "summary": "Resolve to fashion a human after a revealed image.",
                "locator": "Human creation episode",
                "mode": "proposed",
            },
            {
                "stage": "formation",
                "actor": "Powers and angels",
                "summary": "Assemble Adam's body through many contributions.",
                "locator": "Human creation episode",
                "mode": "narrated",
            },
            {
                "stage": "inactivity",
                "actor": "Adam",
                "summary": "The assembled body initially remains inactive.",
                "locator": "Human creation episode",
                "mode": "narrated",
            },
            {
                "stage": "animation",
                "actor": "Yaldabaoth",
                "summary": "Breath transfers power and Adam becomes active.",
                "locator": "Animation of Adam episode",
                "mode": "narrated",
            },
        ],
    },
)


def account(account_id: str) -> dict:
    """Return an independent record for a source passage."""
    for item in ACCOUNTS:
        if item["id"] == account_id:
            return deepcopy(item)
    raise ValueError(f"Unknown creation account: {account_id}")


def compare(left: str, right: str, narrated_only: bool = False) -> dict:
    """Compare category coverage and preserve ordered, repeated annotations."""
    a, b = account(left), account(right)

    def sequence(item: dict) -> list[str]:
        return [
            step["stage"]
            for step in item["steps"]
            if not narrated_only or step["mode"] == "narrated"
        ]

    x, y = sequence(a), sequence(b)
    common = set(x) & set(y)
    return {
        "left": a,
        "right": b,
        "narrated_only": narrated_only,
        "left_sequence": x,
        "right_sequence": y,
        "shared_categories": sorted(common),
        "left_only": sorted(set(x) - set(y)),
        "right_only": sorted(set(y) - set(x)),
        "shared_order_equal": [s for s in x if s in common] == [s for s in y if s in common],
        "genesis_addressee_count": None,
        "boundary": "Sequence annotations are not proof of dependence or historical mechanism.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("list")
    show = sub.add_parser("show")
    show.add_argument("id")
    pair = sub.add_parser("compare")
    pair.add_argument("left")
    pair.add_argument("right")
    pair.add_argument("--narrated-only", action="store_true")
    args = parser.parse_args()
    try:
        if args.command == "list":
            result = [account(item["id"]) for item in ACCOUNTS]
        elif args.command == "show":
            result = account(args.id)
        else:
            result = compare(args.left, args.right, args.narrated_only)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
