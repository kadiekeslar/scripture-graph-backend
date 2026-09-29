# Prompt Log

## AI tools and models used

I used **ChatGPT by OpenAI** throughout the development process to help brainstorm, implement, debug, and refine Scripture Graph.

The deployed backend also uses the **OpenAI API** with the model configured as:

```text
gpt-5.6-luna
```

## Key prompts and requests that shaped the project

The following are representative prompts and requests used during development.

### Project idea and architecture

> Help me design a Bible exploration project with a frontend and backend where users can search a verse, person, topic, or question.

> Help me structure the project so the frontend is on GitHub Pages and the Python Flask backend is deployed on Render.

### Backend development

> Help me build a Flask backend that accepts a search query and returns structured JSON for my frontend.

> Help me organize the backend into separate files for the Flask app, Bible data retrieval, AI calls, and service logic.

### Frontend-backend communication

> Help me connect my JavaScript frontend to my Flask backend using fetch.

> Help me handle backend errors cleanly in the frontend.

### Bible search and data

> Help me retrieve relevant Bible passages for searches like fear, gospel, Moses, or John 3:16.

> Help me support natural-language searches like “What does Jesus say about fear?”

### AI integration

> Help me use AI to interpret a Bible-related search and organize retrieved passages into topics and subthemes.

> Help me return AI-generated explanations in structured JSON that my frontend can use.

### Graph visualization

> Help me build an interactive knowledge graph with Cytoscape.js where the searched topic is the main node and related concepts and verses appear around it.

> Help me center the searched node while still allowing the other nodes to spread naturally and avoid overlapping.

> Help me distinguish different types of relationships in the graph.

### Deployment and debugging

> Help me deploy my Flask backend to Render.

> Help me debug why the backend works locally but the OpenAI request fails on Render.

> Help me configure the required Render environment variables and Python dependencies.

### Portfolio integration

> Help me add Scripture Graph to my portfolio with an image, project description, live-project link, frontend repository link, and backend repository link.

## How AI was used

AI was used as a development assistant rather than as a replacement for testing or decision-making.

I used AI suggestions to help with:

- brainstorming
- code generation
- debugging
- explaining errors
- frontend/backend integration
- API usage
- graph layout
- deployment configuration
- documentation

I reviewed, tested, and revised the generated code while deciding the final project structure, functionality, visual design, and feature scope.
