"""Curated Hebrew morphology and textual witnesses for the Elohim atlas."""

import argparse
import json
import unicodedata

GENESIS = "https://www.sefaria.org/Genesis.1.26-27"
MORPHOLOGY = "https://tanakh.info/gn1-26"
TOV = "https://thetorah.com/article/the-sons-of-israel-or-god-deuteronomy-32-8"
QUMRAN = "https://www.deadseascrolls.org.il/explore-the-archive/manuscript/4Q37-1"

# ID, passage, surface form, lemma, morphology, contextual gloss, source.
TERMS = (
    ("speaker", "Genesis 1:26", "וַיֹּאמֶר", "אמר", "3ms verb", "he said", GENESIS),
    ("elohim", "Genesis 1:26", "אֱלֹהִים", "אלהים", "plural-form noun", "God", GENESIS),
    ("make", "Genesis 1:26", "נַעֲשֶׂה", "עשה", "1cp verb", "let us make", MORPHOLOGY),
    ("human", "Genesis 1:26", "אָדָם", "אדם", "collective noun", "humanity", GENESIS),
    ("image", "Genesis 1:26", "בְּצַלְמֵנוּ", "צלם", "1cp suffix", "our image", MORPHOLOGY),
    ("likeness", "Genesis 1:26", "כִּדְמוּתֵנוּ", "דמות", "1cp suffix", "our likeness", MORPHOLOGY),
    ("created", "Genesis 1:27", "בָּרָא", "ברא", "3ms verb", "he created", GENESIS),
    ("his-image", "Genesis 1:27", "בְּצַלְמוֹ", "צלם", "3ms suffix", "his image", GENESIS),
    ("them", "Genesis 1:27", "אֹתָם", "את", "3mp object", "them", GENESIS),
)

TERM_FIELDS = ("id", "passage", "surface", "lemma", "morphology", "gloss", "source")
WITNESSES = (
    {
        "id": "deut32-mt",
        "passage": "Deuteronomy 32:8",
        "tradition": "Masoretic Text",
        "language": "Hebrew",
        "reading": "בני ישראל",
        "gloss": "sons of Israel",
        "manuscript_id": None,
        "source": TOV,
        "archive": None,
    },
    {
        "id": "deut32-4q37",
        "passage": "Deuteronomy 32:8",
        "tradition": "Dead Sea Scrolls",
        "language": "Hebrew",
        "reading": "בני אלוהים",
        "gloss": "sons of God",
        "manuscript_id": "4Q37 (4QDeutj)",
        "source": TOV,
        "archive": QUMRAN,
    },
    {
        "id": "deut32-lxx-angels",
        "passage": "Deuteronomy 32:8",
        "tradition": "Septuagint (reading family)",
        "language": "Greek",
        "reading": "ἀγγέλων θεοῦ",
        "gloss": "angels of God",
        "manuscript_id": None,
        "source": TOV,
        "archive": None,
    },
)


def unpoint(text: str) -> str:
    """Remove Hebrew marks only, preserving other scripts and punctuation."""
    return "".join(
        ch
        for ch in text
        if not ("\u0591" <= ch <= "\u05c7" and unicodedata.category(ch).startswith("M"))
    )


def lexicon(query: str = "") -> list[dict]:
    """Find exact unpointed Hebrew surface forms, lemmas or stable IDs."""
    key = unpoint(query)
    return [
        dict(zip(TERM_FIELDS, row, strict=True))
        for row in TERMS
        if not key or key in (row[0], unpoint(row[2]), unpoint(row[3]))
    ]


def witness_report() -> dict:
    """Return reported readings without reconstructing an unattested original."""
    return {
        "passage": "Deuteronomy 32:8",
        "readings": [dict(item) for item in WITNESSES],
        "evidence_level": "published-textual-comparison",
        "image_transcription_verified": False,
        "reconstructed_original": None,
        "genesis_addressee_count": None,
    }


def grammar_report() -> dict:
    """Distinguish plural speech, singular action and plural objects."""
    return {
        "plural_speech": ["make", "image", "likeness"],
        "singular_narration": ["speaker", "created", "his-image"],
        "plural_object": ["them"],
        "plural_form_noun": ["elohim"],
        "genesis_addressee_count": None,
        "inference": "Grammatical number is not an enumeration of participants.",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    terms = sub.add_parser("lexicon")
    terms.add_argument("query", nargs="?", default="")
    sub.add_parser("grammar")
    sub.add_parser("witnesses")
    args = parser.parse_args()
    if args.command == "lexicon":
        result = lexicon(args.query)
    elif args.command == "grammar":
        result = grammar_report()
    else:
        result = witness_report()
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
