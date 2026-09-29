# Prompt Log

## AI Tool Used

I used ChatGPT by OpenAI throughout the development of Scripture Graph.

The deployed backend also uses the OpenAI API with the model configured as:

```text
gpt-5.6-luna
```

## Actual Prompts from Development

Below are real prompts and requests from my conversations with ChatGPT while building the project.

### Initial Project Direction

> I want to make a Bible explorer / translator type of site where you can search something and it shows biblical relationships and cross references.

> I want the bigger version, modern and creative, not vibe coded, and more technical and data driven.

These prompts shaped the overall idea of Scripture Graph as an interactive Bible knowledge network instead of a basic search page.

### Search Behavior

> I want people to be able to search anything like fear, Moses, John 3:16, or what does Jesus say about fear?

This led to the design where the backend accepts broad topics, people, verses, and natural-language questions.

### Graph Structure

> I want the searched entity centered, then subthemes around it, then verses correlated with each subtheme.

This shaped the intended hierarchy of the graph:

```text
topic
  → subthemes
      → related verses
```

### Showing More Scripture

> if I search fear I want it to show all the verses that mention fear, like all 365 or whatever

This influenced the idea of retrieving a larger set of matching passages while keeping the initial graph readable.

### Centering and Layout

> will it still be centered

> for now just change the front end to fix some of those, they werent stacked till we adjusted the centering

These prompts led to changes in the Cytoscape layout so the searched node remains centered in the viewport while the rest of the graph uses a more natural force-directed layout.

### Relationship Types

> its still like this and also why have dotted lines if theyre all the same and not distinguished

> the ideas and verses arent correlated how do i fix this, and how do i either get rid of the dots reference to RELATIONSHIPS CROSS REFERENCE CONTEXT / REFERENCE TOPIC / SUBTHEME or actually implement it

These prompts led to distinguishing actual relationship types instead of using decorative edge styles.

The intended relationship structure became:

```text
TOPIC / SUBTHEME
CROSS REFERENCE
CONTEXT / REFERENCE
```

with each line style representing a real type of connection.

### Backend Data Structure

> its still like this and the ideas and verses arent correlated how do i fix this

This exposed a backend data-model issue: verses were being connected directly to the center topic instead of being assigned to the subthemes they matched.

That led to the intended backend structure:

```text
topic
  → subtheme
      → matching verse
```

### Backend / OpenAI Debugging

During deployment, I also asked ChatGPT for help debugging the backend when the OpenAI API worked locally but not correctly on Render.

Examples of the issues we worked through included:

> why is the OpenAI connection not working on Render

> what should I put for the environment variables

> give me the whole file to replace it with

This led to changes in the OpenAI request logic, Render environment variables, and backend dependencies.

### Frontend / Backend Integration

I asked for help connecting the deployed frontend to the Render backend and updating the frontend API URL.

The frontend was configured to call:

```javascript
const API_BASE = "https://scripture-graph-backend.onrender.com";
```

and send searches to:

```text
/explore?q=<query>
```

### Portfolio Integration

> now i need you to put this project into my portfolio here is the code for it and the image i want for this project is names scripture.jpeg and its already in the repo

> the explore project button doesnt take you to https://kadiekeslar.github.io/scripture-graph/

These prompts were used to add Scripture Graph to my portfolio, use `scripture.jpeg` as the project image, and connect the project card to the deployed frontend and GitHub repositories.

### Documentation

> there is no read me or prompt log here are the project requirements again

> the prompt log should be actual chats we had

These prompts led to creating the final README and prompt log required for the assignment.

## How I Used AI

I used ChatGPT to help with:

- brainstorming the project idea
- planning the frontend/backend structure
- generating and revising Flask code
- connecting the frontend to the backend
- debugging OpenAI API calls
- configuring Render deployment
- improving the Cytoscape graph layout
- organizing topic/subtheme/verse relationships
- adding the project to my portfolio
- writing project documentation

I tested and revised the generated code throughout development and made decisions about the final project structure, functionality, appearance, and scope.
