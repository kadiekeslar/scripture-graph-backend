import json
import re
from difflib import SequenceMatcher
from functools import lru_cache
from urllib.request import Request, urlopen

BASE = "https://bible.helloao.org/api"
TRANSLATION = "BSB"

BOOK_ALIASES = {
    "genesis": "GEN", "gen": "GEN",
    "exodus": "EXO", "exod": "EXO", "exo": "EXO",
    "leviticus": "LEV", "lev": "LEV",
    "numbers": "NUM", "num": "NUM",
    "deuteronomy": "DEU", "deut": "DEU",
    "joshua": "JOS", "josh": "JOS",
    "judges": "JDG", "judg": "JDG",
    "ruth": "RUT",
    "1 samuel": "1SA", "1 sam": "1SA",
    "2 samuel": "2SA", "2 sam": "2SA",
    "1 kings": "1KI", "2 kings": "2KI",
    "1 chronicles": "1CH", "2 chronicles": "2CH",
    "ezra": "EZR", "nehemiah": "NEH", "esther": "EST",
    "job": "JOB", "psalm": "PSA", "psalms": "PSA", "ps": "PSA",
    "proverbs": "PRO", "prov": "PRO",
    "ecclesiastes": "ECC", "eccl": "ECC",
    "song of solomon": "SNG", "song of songs": "SNG",
    "isaiah": "ISA", "isa": "ISA",
    "jeremiah": "JER", "jer": "JER",
    "lamentations": "LAM", "ezekiel": "EZK", "daniel": "DAN",
    "hosea": "HOS", "joel": "JOL", "amos": "AMO", "obadiah": "OBA",
    "jonah": "JON", "micah": "MIC", "nahum": "NAM", "habakkuk": "HAB",
    "zephaniah": "ZEP", "haggai": "HAG", "zechariah": "ZEC", "malachi": "MAL",
    "matthew": "MAT", "matt": "MAT",
    "mark": "MRK", "luke": "LUK", "john": "JHN",
    "acts": "ACT", "romans": "ROM", "rom": "ROM",
    "1 corinthians": "1CO", "2 corinthians": "2CO",
    "galatians": "GAL", "ephesians": "EPH", "philippians": "PHP",
    "colossians": "COL", "1 thessalonians": "1TH", "2 thessalonians": "2TH",
    "1 timothy": "1TI", "2 timothy": "2TI", "titus": "TIT", "philemon": "PHM",
    "hebrews": "HEB", "james": "JAS", "1 peter": "1PE", "2 peter": "2PE",
    "1 john": "1JN", "2 john": "2JN", "3 john": "3JN",
    "jude": "JUD", "revelation": "REV", "rev": "REV",
}

BOOK_NAMES = {
    "GEN": "Genesis", "EXO": "Exodus", "LEV": "Leviticus", "NUM": "Numbers",
    "DEU": "Deuteronomy", "JOS": "Joshua", "JDG": "Judges", "RUT": "Ruth",
    "1SA": "1 Samuel", "2SA": "2 Samuel", "1KI": "1 Kings", "2KI": "2 Kings",
    "1CH": "1 Chronicles", "2CH": "2 Chronicles", "EZR": "Ezra", "NEH": "Nehemiah",
    "EST": "Esther", "JOB": "Job", "PSA": "Psalms", "PRO": "Proverbs",
    "ECC": "Ecclesiastes", "SNG": "Song of Solomon", "ISA": "Isaiah", "JER": "Jeremiah",
    "LAM": "Lamentations", "EZK": "Ezekiel", "DAN": "Daniel", "HOS": "Hosea",
    "JOL": "Joel", "AMO": "Amos", "OBA": "Obadiah", "JON": "Jonah", "MIC": "Micah",
    "NAM": "Nahum", "HAB": "Habakkuk", "ZEP": "Zephaniah", "HAG": "Haggai",
    "ZEC": "Zechariah", "MAL": "Malachi", "MAT": "Matthew", "MRK": "Mark",
    "LUK": "Luke", "JHN": "John", "ACT": "Acts", "ROM": "Romans",
    "1CO": "1 Corinthians", "2CO": "2 Corinthians", "GAL": "Galatians", "EPH": "Ephesians",
    "PHP": "Philippians", "COL": "Colossians", "1TH": "1 Thessalonians",
    "2TH": "2 Thessalonians", "1TI": "1 Timothy", "2TI": "2 Timothy", "TIT": "Titus",
    "PHM": "Philemon", "HEB": "Hebrews", "JAS": "James", "1PE": "1 Peter",
    "2PE": "2 Peter", "1JN": "1 John", "2JN": "2 John", "3JN": "3 John",
    "JUD": "Jude", "REV": "Revelation",
}

GOSPEL_BOOKS = {"MAT", "MRK", "LUK", "JHN"}


def _fetch_json(url):
    req = Request(url, headers={"User-Agent": "ScriptureGraph-HW4/2.0"})
    with urlopen(req, timeout=25) as response:
        return json.loads(response.read().decode("utf-8"))


def _normalize(text):
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


def parse_reference(text):
    text = text.strip()
    match = re.match(
        r"^((?:[1-3]\s+)?[A-Za-z]+(?:\s+[A-Za-z]+)*)\s+(\d+)(?::(\d+))?$",
        text,
        re.IGNORECASE,
    )
    if not match:
        return None

    book_text = _normalize(match.group(1))
    book = BOOK_ALIASES.get(book_text)
    if not book:
        return None

    return {
        "book": book,
        "chapter": int(match.group(2)),
        "verse": int(match.group(3)) if match.group(3) else None,
    }


def ref_label(book, chapter, verse=None, end_verse=None):
    base = f"{BOOK_NAMES.get(book, book)} {chapter}"
    if verse is None:
        return base
    if end_verse and end_verse != verse:
        return f"{base}:{verse}-{end_verse}"
    return f"{base}:{verse}"


def ref_id(book, chapter, verse=None):
    suffix = f"-{verse}" if verse is not None else ""
    return f"verse-{book}-{chapter}{suffix}".lower()


@lru_cache(maxsize=256)
def get_chapter(book, chapter):
    return _fetch_json(f"{BASE}/{TRANSLATION}/{book}/{chapter}.simple.json")


def get_verse_text(book, chapter, verse):
    data = get_chapter(book, chapter)
    for item in data.get("chapter", {}).get("content", []):
        if item.get("type") == "verse" and int(item.get("number", -1)) == int(verse):
            return item.get("text", "")
    return ""


def get_passage_text(book, chapter, verse, end_verse=None):
    """Retrieve every verse in a same-chapter range, never silently just its start."""
    end = verse if end_verse is None else int(end_verse)
    if verse < 1 or end < verse or end - verse > 175:
        raise ValueError("Please use a valid same-chapter verse range.")
    data = get_chapter(book, chapter)
    texts = {
        int(item["number"]): item.get("text", "")
        for item in data.get("chapter", {}).get("content", [])
        if item.get("type") == "verse"
    }
    if any(not texts.get(number) for number in range(verse, end + 1)):
        raise ValueError("One or more verses in this passage could not be found.")
    if end == verse:
        return texts[verse]
    return " ".join(f"[{number}] {texts[number]}" for number in range(verse, end + 1))


@lru_cache(maxsize=256)
def get_cross_references(book, chapter, verse, limit=10):
    data = _fetch_json(f"{BASE}/d/open-cross-ref/{book}/{chapter}.json")
    for item in data.get("chapter", {}).get("content", []):
        if int(item.get("verse", -1)) == int(verse):
            refs = item.get("references", [])
            refs = sorted(refs, key=lambda r: r.get("score", 0), reverse=True)
            return refs[:limit]
    return []


@lru_cache(maxsize=256)
def get_chapter_entities(book, chapter):
    try:
        return _fetch_json(f"{BASE}/d/theographic/{book}/{chapter}.json")
    except Exception:
        return {}


@lru_cache(maxsize=1)
def people_index():
    return _fetch_json(f"{BASE}/d/theographic/people.json").get("people", [])


@lru_cache(maxsize=1)
def places_index():
    return _fetch_json(f"{BASE}/d/theographic/places.json").get("places", [])


@lru_cache(maxsize=1)
def events_index():
    return _fetch_json(f"{BASE}/d/theographic/events.json").get("events", [])


def _best_entity_match(query, items, aliases_fields=()):
    q = _normalize(query)
    best = None
    best_score = 0.0
    best_exact = False

    for item in items:
        names = [item.get("name", "")]
        for field in aliases_fields:
            value = item.get(field)
            if isinstance(value, list):
                names.extend(value)
            elif value:
                names.append(str(value))

        for name in names:
            n = _normalize(name)
            if not n:
                continue

            if q == n:
                score = 1.0
                exact = True
            else:
                exact = False
                # Avoid "fear" -> "Ar" and similar short-substring accidents.
                if len(q) >= 4 and len(n) >= 4 and (q in n or n in q):
                    score = 0.90
                else:
                    score = SequenceMatcher(None, q, n).ratio()

            if score > best_score:
                best_score = score
                best = item
                best_exact = exact

    return best, best_score, best_exact


def find_person(query):
    return _best_entity_match(query, people_index(), aliases_fields=("alsoCalled",))


def find_place(query):
    return _best_entity_match(query, places_index(), aliases_fields=("aliases", "kjvName", "esvName"))


def find_event(query):
    return _best_entity_match(query, events_index())


@lru_cache(maxsize=256)
def get_entity_detail(kind, entity_id):
    plural = {"person": "people", "place": "places", "event": "events"}[kind]
    data = _fetch_json(f"{BASE}/d/theographic/{plural}/{entity_id}.json")
    return data.get(kind, {})


@lru_cache(maxsize=1)
def get_complete_translation():
    """
    Loads the full BSB once per server process. This enables real full-Bible
    keyword/topic retrieval without hard-coded verse lists.
    """
    return _fetch_json(f"{BASE}/{TRANSLATION}/complete.simple.json")


@lru_cache(maxsize=1)
def verse_corpus():
    data = get_complete_translation()
    verses = []

    for book in data.get("books", []):
        book_id = book.get("id") or book.get("bookId")
        if not book_id:
            continue

        for chapter in book.get("chapters", []):
            chapter_number = chapter.get("number") or chapter.get("chapterNumber")
            for item in chapter.get("content", []):
                if item.get("type") != "verse":
                    continue

                number = item.get("number")
                text = item.get("text", "")
                if not number or not text:
                    continue

                verses.append({
                    "book": book_id,
                    "chapter": int(chapter_number),
                    "verse": int(number),
                    "label": ref_label(book_id, int(chapter_number), int(number)),
                    "text": text,
                    "normalized": _normalize(text),
                })

    return verses


def search_bible_text(search_terms, limit=30, preferred_books=None):
    """
    Searches the complete BSB text for real lexical matches.

    A verse scores higher when:
    - it contains more of the requested terms
    - it contains a phrase exactly
    - it belongs to a preferred book set
    """
    clean_terms = []
    for term in search_terms:
        norm = _normalize(term)
        if norm and norm not in clean_terms:
            clean_terms.append(norm)

    if not clean_terms:
        return []

    patterns = [(term, re.compile(r"\b" + re.escape(term) + (r"\b" if " " in term else r"\w*\b"))) for term in clean_terms]
    preferred = set(preferred_books or [])
    results = []

    for verse in verse_corpus():
        text = verse["normalized"]
        score = 0

        for term, pattern in patterns:
            match = pattern.search(text)
            if match:
                # Match whole words or word-prefix variants, never "love" in "glove".
                score += 5 + len(term.split()) * 2 if match.group(0) == term else 3

        if score == 0:
            continue

        if verse["book"] in preferred:
            score += 4

        item = dict(verse)
        item["score"] = score
        results.append(item)

    results.sort(key=lambda x: (-x["score"], x["book"], x["chapter"], x["verse"]))
    return results[:limit]


def verify_reference(reference_text):
    parsed = parse_reference(reference_text)
    if not parsed or parsed["verse"] is None:
        return None

    try:
        text = get_verse_text(parsed["book"], parsed["chapter"], parsed["verse"])
        if not text:
            return None
        return {
            "book": parsed["book"],
            "chapter": parsed["chapter"],
            "verse": parsed["verse"],
            "label": ref_label(parsed["book"], parsed["chapter"], parsed["verse"]),
            "text": text,
        }
    except Exception:
        return None
