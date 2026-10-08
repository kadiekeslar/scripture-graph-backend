import json
from functools import lru_cache
import os
from typing import Literal
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

from pydantic import BaseModel, Field


OPENAI_URL = "https://api.openai.com/v1/chat/completions"


class Subtheme(BaseModel):
    name: str
    description: str
    search_terms: list[str] = Field(default_factory=list)


class QueryAnalysis(BaseModel):
    query_type: Literal[
        "verse",
        "person",
        "place",
        "event",
        "topic",
        "question"
    ]

    normalized_query: str
    center_label: str
    short_description: str

    search_terms: list[str] = Field(default_factory=list)
    preferred_books: list[str] = Field(default_factory=list)
    candidate_references: list[str] = Field(default_factory=list)
    subthemes: list[Subtheme] = Field(default_factory=list)


class TopicSummary(BaseModel):
    center_summary: str
    subtheme_summaries: dict[str, str] = Field(default_factory=dict)


class ConnectionExplanation(BaseModel):
    target_reference: str
    explanation: str


class ExplanationBundle(BaseModel):
    center_summary: str
    connection_explanations: list[ConnectionExplanation]


def call_openai_json(system_prompt, user_prompt):
    """
    Call OpenAI directly over HTTPS instead of using the OpenAI Python SDK.

    Returns a Python dictionary parsed from the model's JSON response.
    """

    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is missing from the environment."
        )

    model = os.getenv(
        "OPENAI_MODEL",
        "gpt-5.6-luna"
    )

    body = {
        "model": model,

        "messages": [
            {
                "role": "system",
                "content": system_prompt
            },
            {
                "role": "user",
                "content": user_prompt
            }
        ],

        "response_format": {
            "type": "json_object"
        }
    }

    request = Request(
        OPENAI_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
            "User-Agent": "ScriptureGraph-HW4/2.0"
        },
        method="POST"
    )

    try:
        with urlopen(request, timeout=60) as response:
            response_data = json.loads(
                response.read().decode("utf-8")
            )

    except HTTPError as exc:
        error_body = exc.read().decode(
            "utf-8",
            errors="replace"
        )

        print(
            "OPENAI HTTP ERROR:",
            exc.code,
            error_body
        )

        raise RuntimeError(
            f"OpenAI returned HTTP {exc.code}: {error_body}"
        )

    except URLError as exc:
        print(
            "OPENAI CONNECTION ERROR:",
            repr(exc.reason)
        )

        raise RuntimeError(
            f"Could not connect to OpenAI: {exc.reason}"
        )

    except Exception as exc:
        print(
            "OPENAI UNKNOWN ERROR:",
            repr(exc)
        )

        raise RuntimeError(
            f"OpenAI request failed: {exc}"
        )

    try:
        content = (
            response_data["choices"][0]
            ["message"]["content"]
        )

        return json.loads(content)

    except Exception as exc:
        print(
            "OPENAI RESPONSE PARSE ERROR:",
            repr(exc)
        )

        print(
            "OPENAI RAW RESPONSE:",
            response_data
        )

        raise RuntimeError(
            "OpenAI returned a response that could not be parsed."
        )


@lru_cache(maxsize=128)
def analyze_query(query):
    system_prompt = """
You interpret searches for an interactive Bible knowledge graph.

Return ONLY a valid JSON object.

Use exactly this structure:

{
  "query_type": "verse | person | place | event | topic | question",
  "normalized_query": "string",
  "center_label": "string",
  "short_description": "string",
  "search_terms": ["string"],
  "preferred_books": ["MAT"],
  "candidate_references": ["Matthew 6:25"],
  "subthemes": [
    {
      "name": "string",
      "description": "string",
      "search_terms": ["string"]
    }
  ]
}

Rules:

Classify the user's search as:
verse, person, place, event, topic, or question.

Words describing biblical concepts or human experiences such as
fear, anxiety, faith, grace, forgiveness, suffering, love, hope,
anger, temptation, salvation, prayer, and sin are topics.

Do NOT classify those words as places or people.

Natural-language questions such as
"what does Jesus say about fear?"
should be classified as question.

For topic and question searches:

- create 3 to 5 useful subthemes
- provide short search terms likely to appear in Bible text
- provide overall search terms
- provide up to 8 candidate Bible verse references

Candidate references will be verified by the application,
so do not invent references.

If the user specifically asks about Jesus,
prefer these books:

MAT
MRK
LUK
JHN

If the user specifically asks about Paul,
preferred books may include:

ACT
ROM
1CO
2CO
GAL
EPH
PHP
COL
1TH
2TH
1TI
2TI
TIT
PHM

preferred_books must use standard 3-character Bible IDs.

For clear people, places, events, or verses,
subthemes and candidate_references may be empty.
"""

    result = call_openai_json(
        system_prompt,
        query
    )

    return QueryAnalysis(**result)


def summarize_topic(
    query,
    center_label,
    retrieved_by_subtheme
):
    evidence_lines = []

    for subtheme, verses in retrieved_by_subtheme.items():

        evidence_lines.append(
            f"\nSUBTHEME: {subtheme}"
        )

        for verse in verses[:5]:

            evidence_lines.append(
                f"- {verse['label']}: "
                f"{verse['text'][:350]}"
            )

    evidence = "\n".join(
        evidence_lines
    )

    system_prompt = """
You summarize Bible topic data.

Return ONLY a valid JSON object using this structure:

{
  "center_summary": "string",
  "subtheme_summaries": {
    "exact subtheme name": "short explanation"
  }
}

Use ONLY the Scripture text supplied by the application.

Do not introduce new Bible verse references.

Give a concise overview of the topic.

Give one short explanation for every supplied subtheme.

Do not claim one theological interpretation is the only possible interpretation.
"""

    user_prompt = f"""
Original search:
{query}

Topic center:
{center_label}

Retrieved Bible evidence:
{evidence}
"""

    result = call_openai_json(
        system_prompt,
        user_prompt
    )

    return TopicSummary(**result)


def explain_connections(
    query,
    center_label,
    center_text,
    retrieved_connections
):
    if not retrieved_connections:
        return None

    evidence_lines = []

    for item in retrieved_connections[:12]:

        evidence_lines.append(
            f"- {item['label']}: "
            f"{item.get('text', '')[:420]} "
            f"[source={item.get('source', 'retrieved')}]"
        )

    evidence = "\n".join(
        evidence_lines
    )

    system_prompt = """
You explain relationships inside a Bible knowledge graph.

Return ONLY a valid JSON object using exactly this structure:

{
  "center_summary": "string",
  "connection_explanations": [
    {
      "target_reference": "John 3:16",
      "explanation": "string"
    }
  ]
}

Use ONLY the retrieved references supplied by the application.

Do not add new Bible references.

Explain each connection in one or two clear sentences.

The target_reference value must exactly match one of the supplied reference labels.

Avoid claiming that one theological interpretation is the only possible interpretation.
"""

    user_prompt = f"""
Original search:
{query}

Center:
{center_label}

Center text/context:
{center_text[:700]}

Retrieved connections:
{evidence}
"""

    result = call_openai_json(
        system_prompt,
        user_prompt
    )

    return ExplanationBundle(**result)