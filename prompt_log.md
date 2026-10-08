# Project 2 prompt log — Scripture Graph

## Project background

P2 builds on the HW4 Scripture Graph. The 15 prompts below record the comparison, notebook, performance, interface, and project-learning work.

## Which tool for which job

- **OpenAI Codex, GPT-6.1 Sol, medium reasoning:** the student identified this model in the conversation. Used for rubric review and planning, repository inspection, code generation, iterative fixes, tests, deployment checks, and documentation. Keeping one agent with the repository context made changes across Flask, JavaScript, and the notebook easier to coordinate. No separate brainstorming/debugging model is evidenced here.
- **Computer-use browser tools:** exercised the rendered interface and real network results, including connection clicks, counts, folder navigation, notes after refresh, exports, and restore. These reveal interface problems that a code-only review misses.
- **Node's test runner and Python unittest:** deterministic checks for graph identity, evidence membership, ranges, corpus format, safe errors, and cache behavior. Chosen to check behavior independently of changing AI responses.
- **Git and HTTPS requests:** inspected the named public repositories, kept a commit history, and checked actual deployed endpoints rather than assuming a push worked. Only the two project repositories were accessed.
- **Prettier and Black:** formatters for readable JavaScript/HTML/CSS and Python. They change presentation, not intended behavior.
- **Runtime OpenAI API:** used by the app for interpreting free-form searches and comparing/explaining retrieved Scripture. This model is selected by `OPENAI_MODEL`, separately from Codex. The source default is `gpt-5.6-luna`; the actual deployed setting was not inspected. Bible retrieval uses public Bible data, not invented AI quotations.

## Development process and actual prompts

These are the original app-development prompts, with spelling preserved.

### 1. Initial P2 review

> here is the project prompt for p2, i am going to build off my hw4 which you can find here [**kadiekeslar.github.io**](https://github.com/kadiekeslar/kadiekeslar.github.io/tree/main)
>
> # scripture-graph this is the front end and here is the back end[kadiekeslar](https://github.com/kadiekeslar)
>
> 1. [**scripture-graph-backend**](https://github.com/kadiekeslar/scripture-graph-backend)**&#xA0;&#x20;**[https://kadiekeslar.github.io/](https://kadiekeslar.github.io/) you can find it here in scripture graph and the frontend and backend code is all there as well, let me know what i should add to it to make it full credit for p2

### 2. Implementation and scope

> okay i dont care about the mobile part but do everything else and tell me what code to change and where

### 3. Apply the edits

> are you able to edit the files for me

### 4. Repository access and permissions

> do you only have access to those or do you have access to my whole github even my private stuff

### 5. Compare meaning

> instead of only crossing reference if they share an exact passage, make it more clear on the similarites and difeerences not just make the user read through all of them and add anything to the app that you thing would be super cool and useful

### 6. Search performance

> also why is it so slow every search

### 7. Loading feedback

> while similarites are loading add loading instead of just nothing found

### 8. Wrong Jesus/God result

> ext-based preview · AI comparison is unavailable right now. You can still explore and save this study.
>
> Compare 1 passages from A with 12 from B. The preview below highlights shared language and differences in these retrieved selections; the AI explanation can also connect ideas expressed with different words.
>
> ### Similarities
>
> No supported connection identified in this selection yet.
>
> ### Differences in emphasis
>
> #### Different passages to begin with
>
> **A · Jesus:&#x20;**“Jesus, who is called Justus, also sends greetings. These are the only Jews among my fellow workers for the kingdom of God, and they have been a comfort to me.”
>
> **B · God:&#x20;**“[1] In the beginning God created the heavens and the earth. [2] Now the earth was formless and void, and darkness was over the surface of the deep. And the Spirit of God was hovering over the surface of the wat…”
>
> A · Colossians 4:11
>
> B · Genesis 1:1-12
>
> Highlight supporting passages
>
> Questions for your study
>
> 1.
> 2.
> 3.
>
> Fit graphReset viewStudy notebook this is what is says

### 9. Counts, clutter, and explanations

> right now the left side doesnt date, there were 3 connections like yellow lines but tit still says 0 also there is a lot of info its overwelming also when i click on the yellow line i dont understand why theyre connected i just see that theyre connected and can read both passages

### 10. Remove sidebar clutter

> Shared passages only
> Choose a yellow connection to see why the passages relate. get rid of this 0 identical passages and this

### 11. Notebook folders

> redo the notebook section it should be more clear where its at and the folders in them and stuff like that

### 12. Delete and save destinations

> how do you delete notebooks and make it easier to know what youre savinf and to where

### 13. Explain the personal code contribution

> We want to see evidence of meaningful learning and that you engaged with the code yourself. It doesn't have to be clever: editing content, reorganizing a section, or pointing the code at a different file all count, as long as they show you understood the structure well enough to know where to go and why.
>
> What part of the code did you most substantially write or edit yourself?  (e.g. "I wrote a function in my backend that returns a list of currently registered users. All of that code was written by me" or "I modified the HTML for my app to align all the images in a grid instead of in the less-readable column arrangement I got from AI.")

### 14. Record original prompts

> and it says it should be an ai summary but the actual prompts

### 15. Notebook code readability

>  this code is also not super readable or student like help me make those changes and seperate them with comments and use good dtyle then also make the notebook section especially student like and add lots of comments

## One place AI got it wrong

The AI-assisted implementation was reported as working after earlier successful tests, but the student then tried Jesus versus God and found the app had selected Jesus called Justus: the A result contained only Colossians 4:11. Earlier comparison tests had not covered this ambiguous person name. The student identified the bad result and pasted it into the chat. Codex reproduced it against the public API, inspected the separate Jesus and Jesus Christ dataset entries, changed plain Jesus to resolve to Jesus Christ, retained an explicit Justus query, added a regression check, and verified the deployed comparison. The lesson is to test ordinary ambiguous names and inspect the actual retrieved evidence, rather than treating a successful unrelated demo as proof that all searches work.

Other real findings: the full-Bible reader expected chapter content at the wrong nesting level, leaving its topic corpus empty; the reader and a regression test were corrected. A temporary script's mismatched heredoc terminator caused edits not to apply, and failing checks exposed the mistake. A browser click using an outdated numeric index opened the wrong control; testing switched to named controls and checked the returned state.
