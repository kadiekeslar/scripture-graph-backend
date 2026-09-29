# Scripture Graph Backend

Backend service for **Scripture Graph**, an interactive Bible exploration tool that lets users search for a verse, person, topic, or natural-language question and view related Scripture and concepts as a graph.

The backend is built with **Python + Flask** and is deployed on **Render**. The frontend is deployed separately with GitHub Pages.

## What the backend does

The backend accepts a Bible-related search query, retrieves relevant Bible data, uses AI to interpret and organize the result, and returns structured JSON for the frontend.

### Endpoint

#### `GET /explore`

Accepts a query using the `q` URL parameter.

Example:

```text
/explore?q=fear
```

Example deployed request:

```text
https://scripture-graph-backend.onrender.com/explore?q=fear
```

### Parameter

- `q` — the user's search query

Example queries include:

```text
fear
Moses
John 3:16
what does Jesus say about fear?
```

### Response

The endpoint returns JSON that the frontend uses to build the interactive Scripture Graph.

The response includes information such as:

- the center node for the search
- related graph nodes
- graph edges / relationships
- Bible passages
- subthemes or related concepts
- source information
- AI-generated summaries or explanations based on retrieved Bible data

## How the frontend communicates with the backend

The frontend is hosted at:

```text
https://kadiekeslar.github.io/scripture-graph/
```

When a user enters a search, the frontend sends a request to the backend with JavaScript `fetch()`.

Example:

```javascript
fetch(
  `https://scripture-graph-backend.onrender.com/explore?q=${encodeURIComponent(query)}`
)
```

The frontend then:

1. receives the JSON response
2. reads the returned nodes and edges
3. renders the network using Cytoscape.js
4. shows details about selected verses, topics, and connections
5. displays an error message if the backend request fails

## Running the backend locally

### 1. Clone the repository

```bash
git clone https://github.com/kadiekeslar/scripture-graph-backend.git
cd scripture-graph-backend
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Create a local `.env` file

Add the required environment variables:

```text
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-5.6-luna
```

Do **not** commit the `.env` file to GitHub.

### 4. Run the Flask app

```bash
python app.py
```

The backend should run locally, typically at:

```text
http://127.0.0.1:5000
```

You can test it in a browser with:

```text
http://127.0.0.1:5000/explore?q=fear
```

## Environment variables and secrets

The project uses an OpenAI API key.

The key is **not stored in the frontend code** and should never be committed to GitHub.

For local development:

- store the key in a `.env` file
- keep `.env` excluded with `.gitignore`

For deployment:

- store `OPENAI_API_KEY` as an environment variable in Render
- store `OPENAI_MODEL` as an environment variable in Render

This keeps private credentials on the backend instead of exposing them in browser-side JavaScript.

## Deployment

Backend:

```text
https://scripture-graph-backend.onrender.com
```

Frontend:

```text
https://kadiekeslar.github.io/scripture-graph/
```

## Main technologies

- Python
- Flask
- Flask-CORS
- JavaScript
- Cytoscape.js
- OpenAI API
- Render
- GitHub Pages

## AI usage

AI tools were used during brainstorming, implementation, debugging, and refinement of the project.

See [`prompt_log.md`](prompt_log.md) for the AI tools/models used and the key prompts that shaped the implementation.
