# Scripture Graph backend — Project 2

[Main project README](https://github.com/kadiekeslar/kadiekeslar.github.io/blob/main/scripture-graph/README.md) · [P2 prompt log](prompt_log.md) · [Earlier HW4 log](prompt_log_hw4.md)

## My backend explanation — student writing required

[Write in your own words what the API is responsible for, how you used AI, what code you changed yourself, and how secrets are handled. The main project README contains the fuller student explanation checklist.]

## AI-generated technical documentation

Codex wrote the following notes. The backend uses Flask to retrieve Bible data, route searches, and return graph JSON. The frontend is deployed at https://kadiekeslar.github.io/scripture-graph/ and the backend at https://scripture-graph-backend.onrender.com/.

| Endpoint | Purpose |
|---|---|
| `GET /health` | Lightweight availability check |
| `GET /explore?q=...&fast=1` | Retrieved graph before final AI explanations |
| `GET /explain?q=...` | AI summaries for a cached retrieved graph |
| `POST /compare` | Cited similarities/differences; JSON contains `left` and `right` search strings |

`app.py` handles routes and errors; `services.py` builds verse/entity/topic graphs; `bible_data.py` reads public Bible data and validates full ranges; `comparison.py` checks AI report shape and evidence membership; `ai_service.py` makes server-side OpenAI requests; `result_cache.py` bounds ten-minute cached results and shares identical in-flight work. Read the comments and the frontend `CODE_GUIDE.md` for a walkthrough.

### Run locally

```sh
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Before starting, put `OPENAI_API_KEY` and optionally `OPENAI_MODEL` in an ignored `.env` file or environment variables. Never commit real keys. The runtime model setting is independent of the development model (Codex GPT-6.1 Sol, medium reasoning, reported by the student). Without a key, retrieve-only paths can still work, but AI features/free-form interpretation cannot.

Run checks with `python -m unittest discover -s tests`. Deploy secrets through Render's environment settings. If a worker timeout is too short for synchronous provider requests, a suitable start command is `gunicorn app:app --workers 1 --threads 4 --timeout 120 --bind 0.0.0.0:$PORT`; the actual dashboard setting has not been inspected or changed.

### Attribution and limitations

The [Free Use Bible API](https://bible.helloao.org/) supplies Berean Standard Bible text, cross-references, and Theographic metadata. [Flask](https://flask.palletsprojects.com/) serves the endpoints; [OpenAI](https://openai.com/) supplies Codex and runtime AI interpretation. HW4 provided the foundation. Codex generated or substantially modified the P2 implementation; independent student edits must be documented separately. Interpretations describe limited retrieved evidence and are not Scripture. Browser notebook notes are stored in the frontend, not this server.
