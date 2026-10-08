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


> I want people to be able to search anything like fear, Moses, John 3:16, or what does Jesus say about fear?

> I want the searched entity centered, then subthemes around it, then verses correlated with each subtheme.


> if I search fear I want it to show all the verses that mention fear


> for now just change the front end to fix some of those, they werent stacked till we adjusted the centering


> its still like this and also why have dotted lines if theyre all the same and not distinguished

> the ideas and verses arent correlated how do i fix this, and how do i either get rid of the dots reference to RELATIONSHIPS CROSS REFERENCE CONTEXT / REFERENCE TOPIC / SUBTHEME or actually implement it

> its still like this and the ideas and verses arent correlated how do i fix this

> why is the OpenAI connection not working on Render

> what should I put for the environment variables

> give me the whole file to replace it with

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

## Project 2 continuation (AI-generated factual record)

The original log above describes the earlier project. The P2 implementation/application requests and new development record are in the [separate P2 prompt log](https://github.com/kadiekeslar/kadiekeslar.github.io/blob/main/scripture-graph/prompt_log.md). Codex modified app.py, bible_data.py, and services.py for safe errors, full ranges, lexical boundaries, data caching, optional lookup resilience, and empty-result handling. Student-written changes and actual focused work time must still be recorded by the student.

## Jesus identity and comparison repair

A plain Jesus search resolves to Jesus Christ; “Jesus called Justus” explicitly selects the other person. Entity evidence samples across available references instead of only the first twelve. Invalid AI comparisons retry once against the original evidence, preserving citation checks. Blank study questions are rejected.
