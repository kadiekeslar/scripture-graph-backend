from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from services import explore_query, enrich_graph
from comparison import compare_graphs
from result_cache import cached_result

load_dotenv()

app = Flask(__name__)
CORS(app)
app.config["MAX_CONTENT_LENGTH"] = 8192


def graph_result(query, fast):
    return cached_result(("graph", query.strip().casefold(), fast), lambda: explore_query(query, with_explanations=not fast))


@app.get("/")
def home():
    return jsonify({
        "name": "Scripture Graph API",
        "status": "ok",
        "version": "compare-connection-clarity-p2",
        "description": "AI-assisted Bible knowledge graph using retrieved Bible data.",
        "example": "/explore?q=fear"
    })


@app.get("/health")
def health():
    return jsonify({"status": "ok"})


@app.get("/explore")
def explore():
    query = request.args.get("q", "").strip()

    if not query:
        return jsonify({
            "error": "Missing search query.",
            "example": "/explore?q=fear"
        }), 400

    if len(query) > 300:
        return jsonify({"error": "Keep your search under 300 characters."}), 400

    try:
        return jsonify(graph_result(query, request.args.get("fast") == "1"))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        print("EXPLORE ERROR:", repr(exc))
        return jsonify({
            "error": "The graph could not be built right now. Please retry; a data service may be unavailable."
        }), 500


@app.post("/compare")
def compare():
    body = request.get_json(silent=True)
    if not isinstance(body, dict):
        return jsonify({"error": "Send two search strings."}), 400
    left, right = body.get("left"), body.get("right")
    if not all(isinstance(q, str) and 0 < len(q.strip()) <= 300 for q in [left, right]):
        return jsonify({"error": "Both searches must contain 1–300 characters."}), 400
    left, right = left.strip(), right.strip()
    try:
        report = cached_result(("compare", left.casefold(), right.casefold()), lambda: compare_graphs(graph_result(left, True), graph_result(right, True)))
        return jsonify(report)
    except Exception as exc:
        print("COMPARISON unavailable:", type(exc).__name__)
        return jsonify({"error": "The AI comparison is unavailable. The graph and text-based comparison still work.", "code": "invalid_comparison_response" if isinstance(exc, (ValueError, TypeError, KeyError)) else "comparison_service_unavailable"}), 503


@app.get("/explain")
def explain():
    query = request.args.get("q", "").strip()
    if not query or len(query) > 300:
        return jsonify({"error": "Use a search of 1–300 characters."}), 400
    try:
        result = cached_result(("explanation", query.casefold()), lambda: enrich_graph(graph_result(query, True)))
        return jsonify(result)
    except Exception as exc:
        print("EXPLANATION unavailable:", type(exc).__name__)
        return jsonify({"error": "AI explanations are unavailable. Retrieved Scripture is still available."}), 503


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Endpoint not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
