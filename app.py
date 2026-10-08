from flask import Flask, jsonify, request
from flask_cors import CORS
from dotenv import load_dotenv
from services import explore_query

load_dotenv()

app = Flask(__name__)
CORS(app)


@app.get("/")
def home():
    return jsonify({
        "name": "Scripture Graph API",
        "status": "ok",
        "version": "compare-study-p2",
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
        return jsonify(explore_query(query))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400
    except Exception as exc:
        print("EXPLORE ERROR:", repr(exc))
        return jsonify({
            "error": "The graph could not be built right now. Please retry; a data service may be unavailable."
        }), 500


@app.errorhandler(404)
def not_found(_error):
    return jsonify({"error": "Endpoint not found"}), 404


if __name__ == "__main__":
    app.run(debug=True)
