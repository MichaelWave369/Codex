"""Source-scoped chronological intervals; temporal order is not transmission."""

import argparse
import json

YALE = (
    "https://yalebiblestudy.org/courses/reading-the-bible/"
    "lessons/genesis-introduction-study-guide/"
)
IAA = "https://www.deadseascrolls.org.il/explore-the-archive/manuscript/4Q37-1?locale=en_US"
CAMBRIDGE = (
    "https://www.cambridge.org/core/books/nag-hammadi-codices-and-their-ancient-readers/"
    "textual-fluidity-and-multiple-versions-in-monastic-textual-practice/"
    "672312FB2CCCA8612E655243EC20886C"
)
FIELDS = ("id", "work", "kind", "start", "end", "region", "source", "basis")
# Signed historical years: -1 = 1 BCE, 1 = 1 CE; zero is invalid.
ROWS = (
    (
        "atrahasis-morgan",
        "Atraḫasis",
        "manuscript",
        -1700,
        -1601,
        "Mesopotamia",
        "https://www.themorgan.org/seals-and-tablets/225906",
        "Catalog century; indexed excerpt only, direct retrieval denied.",
    ),
    (
        "baal-tablet4",
        "Baal Cycle",
        "manuscript",
        -1500,
        -1400,
        "Ugarit",
        "https://virtual-museum-syria.org/aleppo/the-cycle-of-baal-tablet-4/",
        "Approximate range in this catalog; not a consensus composition date.",
    ),
    (
        "genesis-priestly",
        "Genesis 1",
        "composition-model",
        -600,
        -401,
        "Judah and Babylonian exile context",
        YALE,
        "Coarse working interval for exilic or early postexilic Priestly model.",
    ),
    (
        "genesis2-monarchy",
        "Genesis 2",
        "composition-model",
        -800,
        -601,
        "Judah",
        YALE,
        "One proposed date for the Yahwist strand; disputed.",
    ),
    (
        "genesis2-exile",
        "Genesis 2",
        "composition-model",
        -600,
        -501,
        "Babylonian exile context",
        YALE,
        "Alternative proposed date for the Yahwist strand; disputed.",
    ),
    (
        "deut-4q37",
        "Deuteronomy",
        "manuscript",
        None,
        None,
        "Qumran (findspot)",
        IAA,
        "Catalog identifies 4Q37; date not exposed in retrieved page.",
    ),
    (
        "philo-context",
        "Philo, On the Creation",
        "author-context",
        -100,
        100,
        "Alexandria",
        "https://plato.stanford.edu/entries/philo/",
        "Broad century-scale author context, not a date of composition.",
    ),
    (
        "john-irenaeus",
        "Apocryphon of John",
        "related-attestation",
        101,
        200,
        "Early Christian literary context",
        CAMBRIDGE,
        "Second-century related account in Irenaeus; not a surviving copy.",
    ),
    (
        "john-nhc2",
        "Apocryphon of John",
        "manuscript",
        300,
        399,
        "Egypt",
        "https://4care-skos.mf.no/4care-artefacts/81/",
        "4CARE relative date for Nag Hammadi Codex II, TM 107742.",
    ),
)


def records() -> list[dict]:
    """Return detached interval records with their dating basis."""
    return [dict(zip(FIELDS, row, strict=True)) for row in ROWS]


def lookup(record_id: str) -> dict:
    """Return one dated observation."""
    for item in records():
        if item["id"] == record_id:
            return item
    raise ValueError(f"Unknown chronology record: {record_id}")


def interval_relation(a: tuple, b: tuple) -> str:
    """Compare inclusive ranges; reject invalid dates and preserve unknowns."""
    for start, end in (a, b):
        if start is None and end is None:
            continue
        if type(start) is not int or type(end) is not int:
            raise ValueError("Expected two integer years or two nulls")
        if start == 0 or end == 0 or start > end:
            raise ValueError("Invalid historical interval")
    if None in a or None in b:
        return "unknown"
    if a[1] < b[0]:
        return "before"
    if a[0] > b[1]:
        return "after"
    return "overlap"


def compare(left: str, right: str) -> dict:
    """Describe date bounds without asserting priority of underlying ideas."""
    a, b = lookup(left), lookup(right)
    relation = interval_relation((a["start"], a["end"]), (b["start"], b["end"]))
    return {
        "left": a,
        "right": b,
        "interval_relation": relation,
        "same_date_kind": a["kind"] == b["kind"],
        "transmission_established": False,
        "idea_origin_established": False,
        "genesis_addressee_count": None,
    }


def timeline() -> dict:
    """Sort known intervals by earliest bound; keep unknown dates separate."""
    data = records()
    known = [item for item in data if item["start"] is not None]
    return {
        "dated": sorted(known, key=lambda item: (item["start"], item["id"])),
        "undated": [item for item in data if item["start"] is None],
        "year_convention": "Signed historical years, no year zero",
        "boundary": "Order of earliest bounds is not an established order of composition.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("timeline")
    show = sub.add_parser("show")
    show.add_argument("id")
    pair = sub.add_parser("compare")
    pair.add_argument("left")
    pair.add_argument("right")
    args = parser.parse_args()
    try:
        if args.command == "timeline":
            result = timeline()
        elif args.command == "show":
            result = lookup(args.id)
        else:
            result = compare(args.left, args.right)
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
