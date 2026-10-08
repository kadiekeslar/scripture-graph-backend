from collections import defaultdict

from bible_data import (
    parse_reference,
    ref_id,
    ref_label,
    get_verse_text,
    get_passage_text,
    get_cross_references,
    get_chapter_entities,
    find_person,
    find_place,
    find_event,
    get_entity_detail,
    search_bible_text,
    verify_reference,
)
from ai_service import analyze_query, explain_connections, summarize_topic


MAX_GRAPH_NODES = 34
MAX_GRAPH_EDGES = 42


def node(node_id, label, node_type, summary="", **extra):
    data = {
        "id": node_id,
        "label": label,
        "type": node_type,
        "summary": summary,
    }
    data.update(extra)
    return {"data": data}


def edge(edge_id, source, target, edge_type, label, explanation="", source_name=""):
    return {
        "data": {
            "id": edge_id,
            "source": source,
            "target": target,
            "type": edge_type,
            "label": label,
            "explanation": explanation,
            "sourceName": source_name,
        }
    }


def dedupe_graph(nodes, edges):
    seen_nodes = set()
    clean_nodes = []
    for item in nodes:
        node_id = item["data"]["id"]
        if node_id not in seen_nodes:
            seen_nodes.add(node_id)
            clean_nodes.append(item)

    seen_edges = set()
    clean_edges = []
    for item in edges:
        d = item["data"]
        key = (d["source"], d["target"], d["type"])
        if key not in seen_edges and d["source"] != d["target"]:
            seen_edges.add(key)
            clean_edges.append(item)

    return clean_nodes, clean_edges


def add_ai_explanations(query, center_id, center_label, center_text, nodes, edges):
    by_id = {n["data"]["id"]: n["data"] for n in nodes}
    retrieved = []

    for e in edges:
        d = e["data"]
        other_id = d["target"] if d["source"] == center_id else d["source"]
        other = by_id.get(other_id, {})
        if other.get("type") == "verse":
            retrieved.append({
                "label": other.get("label", ""),
                "text": other.get("text", ""),
                "source": d.get("sourceName", ""),
            })

    try:
        bundle = explain_connections(
            query=query,
            center_label=center_label,
            center_text=center_text,
            retrieved_connections=retrieved,
        )
    except Exception as exc:
        print("AI explanation error:", repr(exc))
        bundle = None

    if not bundle:
        return nodes, edges, ""

    explanation_map = {
        item.target_reference.lower(): item.explanation
        for item in bundle.connection_explanations
    }

    for e in edges:
        target = by_id.get(e["data"]["target"], {})
        label = target.get("label", "").lower()
        if label in explanation_map:
            e["data"]["explanation"] = explanation_map[label]

    return nodes, edges, bundle.center_summary


def build_verse_graph(query, parsed):
    book = parsed["book"]
    chapter = parsed["chapter"]
    verse = parsed["verse"]

    if verse is None:
        raise ValueError("Please include a verse number, for example John 3:16.")

    center_id = ref_id(book, chapter, verse)
    center_label = ref_label(book, chapter, verse)
    center_text = get_verse_text(book, chapter, verse)

    if not center_text:
        raise ValueError(f"Could not find {center_label}.")

    nodes = [
        node(
            center_id,
            center_label,
            "verse",
            summary="Selected passage",
            reference=center_label,
            text=center_text,
            sourceName="Berean Standard Bible / Free Use Bible API",
            isCenter=True,
        )
    ]
    edges = []

    refs = get_cross_references(book, chapter, verse, limit=12)
    for i, r in enumerate(refs):
        target_book = r["book"]
        target_chapter = r["chapter"]
        target_verse = r["verse"]
        target_id = ref_id(target_book, target_chapter, target_verse)
        target_label = ref_label(
            target_book,
            target_chapter,
            target_verse,
            r.get("endVerse"),
        )
        try:
            target_text = get_passage_text(target_book, target_chapter, target_verse, r.get("endVerse"))
        except Exception:
            target_text = ""

        nodes.append(
            node(
                target_id,
                target_label,
                "verse",
                summary="Retrieved cross-reference",
                reference=target_label,
                text=target_text,
                score=r.get("score"),
                sourceName="Berean Standard Bible text / Open Bible Cross References",
            )
        )
        edges.append(
            edge(
                f"xref-{i}",
                center_id,
                target_id,
                "cross-reference",
                "Cross-reference",
                source_name="Open Bible Cross References",
            )
        )

    try:
        entity_data = get_chapter_entities(book, chapter).get("chapter", {})
        for kind, plural in [
            ("person", "people"),
            ("place", "places"),
            ("event", "events"),
        ]:
            for item in entity_data.get(plural, [])[:3]:
                entity_id = f"{kind}-{item['id']}"
                nodes.append(
                    node(
                        entity_id,
                        item.get("name", item["id"]),
                        kind,
                        summary=f"{kind.title()} appearing in {ref_label(book, chapter)}.",
                        sourceName="Theographic Bible Metadata",
                    )
                )
                edges.append(
                    edge(
                        f"entity-{kind}-{len(edges)}",
                        center_id,
                        entity_id,
                        "context",
                        f"Appears in {ref_label(book, chapter)}",
                        source_name="Theographic Bible Metadata",
                    )
                )
    except Exception as exc:
        print("Entity enrichment skipped:", repr(exc))

    nodes, edges = dedupe_graph(nodes, edges)
    nodes, edges, ai_summary = add_ai_explanations(
        query, center_id, center_label, center_text, nodes, edges
    )
    if ai_summary:
        nodes[0]["data"]["summary"] = ai_summary

    return {
        "query": query,
        "queryType": "verse",
        "center": center_id,
        "centerLabel": center_label,
        "nodes": nodes[:MAX_GRAPH_NODES],
        "edges": edges[:MAX_GRAPH_EDGES],
        "sources": [
            "Berean Standard Bible via Free Use Bible API",
            "Open Bible Cross References via Free Use Bible API",
            "Theographic Bible Metadata via Free Use Bible API",
            "AI explanations generated only from retrieved data",
        ],
    }


def build_entity_graph(query, kind, match):
    detail = get_entity_detail(kind, match["id"])
    center_id = f"{kind}-{detail['id']}"
    center_label = detail.get("name", query)

    description = detail.get("description", "")
    if isinstance(description, list):
        description = " ".join(description[:2])

    nodes = [
        node(
            center_id,
            center_label,
            kind,
            summary=description or f"Biblical {kind}.",
            sourceName="Theographic Bible Metadata",
            isCenter=True,
        )
    ]
    edges = []

    for i, r in enumerate(detail.get("references", [])[:12]):
        target_id = ref_id(r["book"], r["chapter"], r["verse"])
        target_label = ref_label(
            r["book"], r["chapter"], r["verse"], r.get("endVerse")
        )
        try:
            text = get_passage_text(r["book"], r["chapter"], r["verse"], r.get("endVerse"))
        except Exception:
            text = ""

        nodes.append(
            node(
                target_id,
                target_label,
                "verse",
                summary=f"Passage mentioning {center_label}.",
                reference=target_label,
                text=text,
                sourceName="Theographic Bible Metadata + BSB",
            )
        )
        edges.append(
            edge(
                f"reference-{i}",
                center_id,
                target_id,
                "reference",
                f"Mentions {center_label}",
                source_name="Theographic Bible Metadata",
            )
        )

    nodes, edges = dedupe_graph(nodes, edges)
    nodes, edges, ai_summary = add_ai_explanations(
        query, center_id, center_label, description, nodes, edges
    )
    if ai_summary:
        nodes[0]["data"]["summary"] = ai_summary

    return {
        "query": query,
        "queryType": kind,
        "center": center_id,
        "centerLabel": center_label,
        "nodes": nodes[:MAX_GRAPH_NODES],
        "edges": edges[:MAX_GRAPH_EDGES],
        "sources": [
            "Theographic Bible Metadata via Free Use Bible API",
            "Berean Standard Bible via Free Use Bible API",
            "AI explanations generated only from retrieved data",
        ],
    }


def _verse_node_from_search_result(result, topic_label):
    rid = ref_id(result["book"], result["chapter"], result["verse"])
    return node(
        rid,
        result["label"],
        "verse",
        summary=f"Retrieved Bible passage related to {topic_label}.",
        reference=result["label"],
        text=result["text"],
        relevance=result.get("score"),
        sourceName="Full-text BSB search / Free Use Bible API",
    )


def build_topic_graph(query, analysis):
    center_id = "topic-center"
    center_label = analysis.center_label or analysis.normalized_query or query

    nodes = [
        node(
            center_id,
            center_label,
            "topic",
            summary=analysis.short_description or "Bible topic search",
            sourceName="AI query interpretation + real Bible text retrieval",
            isCenter=True,
        )
    ]
    edges = []

    # Retrieve direct lexical matches from the actual full Bible text.
    overall_terms = analysis.search_terms or [analysis.normalized_query]
    direct_matches = search_bible_text(
        overall_terms,
        limit=10,
        preferred_books=analysis.preferred_books,
    )

    # Verify any AI-proposed references, then merge them into the direct pool.
    proposed = []
    for candidate in analysis.candidate_references[:8]:
        verified = verify_reference(candidate)
        if verified:
            verified["score"] = 1
            proposed.append(verified)

    used_verse_ids = set()
    retrieved_by_subtheme = defaultdict(list)

    # Build subtheme branches first.
    subthemes = analysis.subthemes[:5]
    if not subthemes:
        # Always make at least one branch for broad topics.
        from types import SimpleNamespace
        subthemes = [
            SimpleNamespace(
                name="Key passages",
                description=f"Passages directly related to {center_label}.",
                search_terms=overall_terms,
            )
        ]

    for s_index, subtheme in enumerate(subthemes):
        theme_id = f"subtheme-{s_index}"
        nodes.append(
            node(
                theme_id,
                subtheme.name,
                "subtheme",
                summary=subtheme.description,
                sourceName="AI-organized category; verses retrieved from Bible text",
            )
        )
        edges.append(
            edge(
                f"center-theme-{s_index}",
                center_id,
                theme_id,
                "topic",
                subtheme.description,
                source_name="AI organization of retrieved Bible data",
            )
        )

        matches = search_bible_text(
            subtheme.search_terms or overall_terms,
            limit=14,
            preferred_books=analysis.preferred_books,
        )

        # Prefer unique verses and keep four per category so the graph stays readable.
        added = 0
        for result in matches:
            rid = ref_id(result["book"], result["chapter"], result["verse"])
            if rid in used_verse_ids:
                continue

            used_verse_ids.add(rid)
            retrieved_by_subtheme[subtheme.name].append(result)
            nodes.append(_verse_node_from_search_result(result, center_label))
            edges.append(
                edge(
                    f"theme-verse-{s_index}-{added}",
                    theme_id,
                    rid,
                    "topic-match",
                    f"Matches: {', '.join(subtheme.search_terms[:3])}",
                    source_name="Full-text Berean Standard Bible search",
                )
            )
            added += 1
            if added >= 4:
                break

    # Add a few top-level direct matches that were not used in subthemes.
    direct_added = 0
    for result in direct_matches + proposed:
        rid = ref_id(result["book"], result["chapter"], result["verse"])
        if rid in used_verse_ids:
            continue
        used_verse_ids.add(rid)
        nodes.append(_verse_node_from_search_result(result, center_label))
        edges.append(
            edge(
                f"direct-{direct_added}",
                center_id,
                rid,
                "direct-match",
                "Direct topic match",
                source_name="Verified Bible text retrieval",
            )
        )
        direct_added += 1
        if direct_added >= 5:
            break

    if not any(item["data"]["type"] == "verse" for item in nodes):
        raise ValueError(
            "I understood the topic, but could not retrieve matching Bible passages."
        )

    # AI summarizes ONLY the retrieved verses/subthemes.
    try:
        topic_summary = summarize_topic(
            query=query,
            center_label=center_label,
            retrieved_by_subtheme=dict(retrieved_by_subtheme),
        )
    except Exception as exc:
        print("Topic summary error:", repr(exc))
        topic_summary = None

    if topic_summary:
        nodes[0]["data"]["summary"] = topic_summary.center_summary

        summary_map = topic_summary.subtheme_summaries
        for n in nodes:
            if n["data"]["type"] == "subtheme":
                label = n["data"]["label"]
                if label in summary_map:
                    n["data"]["summary"] = summary_map[label]

    nodes, edges = dedupe_graph(nodes, edges)

    return {
        "query": query,
        "queryType": analysis.query_type,
        "center": center_id,
        "centerLabel": center_label,
        "nodes": nodes[:MAX_GRAPH_NODES],
        "edges": edges[:MAX_GRAPH_EDGES],
        "sources": [
            "AI interprets the topic and creates organizational subthemes",
            "Passages are retrieved from the complete Berean Standard Bible text",
            "AI-proposed references are verified against real Bible text before display",
            "AI summaries are generated only from the retrieved passages",
            "Bible text supplied by the Free Use Bible API",
        ],
    }


def explore_query(query):
    # 1. Exact Bible references are deterministic.
    parsed = parse_reference(query)
    if parsed and parsed["verse"] is not None:
        return build_verse_graph(query, parsed)

    # 2. Only exact or exceptionally strong entity matches bypass AI.
    def optional_match(finder, value):
        try:
            return finder(value)
        except Exception as exc:
            print("Entity lookup unavailable:", type(exc).__name__)
            return None, 0.0, False

    person, person_score, person_exact = optional_match(find_person, query)
    place, place_score, place_exact = optional_match(find_place, query)
    event, event_score, event_exact = optional_match(find_event, query)

    ranked = sorted(
        [
            ("person", person, person_score, person_exact),
            ("place", place, place_score, place_exact),
            ("event", event, event_score, event_exact),
        ],
        key=lambda x: x[2],
        reverse=True,
    )

    kind, match, score, exact = ranked[0]
    if match and (exact or score >= 0.97):
        return build_entity_graph(query, kind, match)

    # 3. Free-form topics/questions are interpreted by AI.
    try:
        analysis = analyze_query(query)
        if analysis is None:
            raise RuntimeError("AI interpretation unavailable")
    except Exception as exc:
        print("Query interpretation unavailable:", type(exc).__name__)
        raise RuntimeError("Query interpretation service unavailable") from exc

    # If AI recognizes a normalized entity, resolve it against the real entity dataset.
    if analysis.query_type in {"person", "place", "event"}:
        finder = {
            "person": find_person,
            "place": find_place,
            "event": find_event,
        }[analysis.query_type]

        match, score, exact = optional_match(finder, analysis.normalized_query)
        if match and (exact or score >= 0.92):
            return build_entity_graph(query, analysis.query_type, match)

    # If AI normalized a Bible reference, parse and retrieve it normally.
    if analysis.query_type == "verse":
        parsed = parse_reference(analysis.normalized_query)
        if parsed and parsed["verse"] is not None:
            return build_verse_graph(query, parsed)

    # Everything else becomes a data-driven topic/question graph.
    return build_topic_graph(query, analysis)
