import os
from typing import Literal
from pydantic import BaseModel, Field
from openai import OpenAI


class Subtheme(BaseModel):
    name: str
    description: str
    search_terms: list[str] = Field(default_factory=list)


class QueryAnalysis(BaseModel):
    query_type: Literal["verse", "person", "place", "event", "topic", "question"]
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


def get_client():
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)


def analyze_query(query):
    client = get_client()
    if client is None:
        return None

    response = client.responses.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        reasoning={"effort": "low"},
        input=[
            {
                "role": "system",
                "content": (
                    "You interpret searches for an interactive Bible knowledge graph. "
                    "Classify the search as verse, person, place, event, topic, or question. "
                    "Words such as fear, anxiety, faith, grace, forgiveness, suffering, love, hope, "
                    "anger, temptation, salvation, prayer, and sin are topics, not entity names. "
                    "Natural-language questions are questions. "
                    "For topic/question searches, create 3 to 5 useful subthemes that help a reader "
                    "understand how Scripture treats the subject. "
                    "For each subtheme provide 1 to 4 short lexical search terms or phrases that are "
                    "likely to occur in actual Bible text. "
                    "Also provide overall search_terms for direct retrieval from the Bible text. "
                    "If the user asks specifically about Jesus, prefer MAT, MRK, LUK, JHN. "
                    "If the user asks about Paul, preferred_books may include ACT, ROM, 1CO, 2CO, GAL, "
                    "EPH, PHP, COL, 1TH, 2TH, 1TI, 2TI, TIT, PHM. "
                    "preferred_books must use standard three-character Bible IDs like MAT, JHN, ROM. "
                    "You may propose up to 8 candidate verse references for concepts that are not easy "
                    "to retrieve lexically, but these references will be independently verified. "
                    "Do not invent books, chapters, or verses. "
                    "For a clear person/place/event name, candidate_references and subthemes may be empty."
                ),
            },
            {"role": "user", "content": query},
        ],
        text_format=QueryAnalysis,
    )
    return response.output_parsed


def summarize_topic(query, center_label, retrieved_by_subtheme):
    client = get_client()
    if client is None:
        return None

    lines = []
    for subtheme, verses in retrieved_by_subtheme.items():
        lines.append(f"\nSUBTHEME: {subtheme}")
        for verse in verses[:5]:
            lines.append(f"- {verse['label']}: {verse['text'][:350]}")

    evidence = "\n".join(lines)

    response = client.responses.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        reasoning={"effort": "low"},
        input=[
            {
                "role": "system",
                "content": (
                    "Summarize a Bible topic using ONLY the supplied retrieved Scripture text. "
                    "Do not introduce new verse references. "
                    "Give a concise neutral overview and one short explanation per supplied subtheme. "
                    "Do not claim one theological interpretation is the only possible interpretation."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Original search: {query}\n"
                    f"Topic center: {center_label}\n"
                    f"Retrieved evidence:\n{evidence}"
                ),
            },
        ],
        text_format=TopicSummary,
    )
    return response.output_parsed


def explain_connections(query, center_label, center_text, retrieved_connections):
    client = get_client()
    if client is None or not retrieved_connections:
        return None

    evidence_lines = []
    for item in retrieved_connections[:12]:
        evidence_lines.append(
            f"- {item['label']}: {item.get('text', '')[:420]} "
            f"[source={item.get('source', 'retrieved')}]"
        )

    response = client.responses.parse(
        model=os.getenv("OPENAI_MODEL", "gpt-5.6-luna"),
        reasoning={"effort": "low"},
        input=[
            {
                "role": "system",
                "content": (
                    "You explain a Bible knowledge graph. "
                    "Use ONLY the retrieved references supplied by the application. "
                    "Do not add new Bible references. "
                    "Explain each connection in 1-2 clear sentences."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Original search: {query}\n"
                    f"Center: {center_label}\n"
                    f"Center text/context: {center_text[:700]}\n\n"
                    f"Retrieved connections:\n" + "\n".join(evidence_lines)
                ),
            },
        ],
        text_format=ExplanationBundle,
    )
    return response.output_parsed
