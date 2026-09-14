# Todo API (Python)

## What is this?

Imagine you keep a small paper notebook where you write down things you need to do — "buy milk", "finish homework" — and when you're done with something, you tick it off. This project is that same simple notebook, except instead of paper, it lives inside a small web server that anyone (or any other app) can talk to over the internet.

That's it. That's the whole idea. You can:
1. **Add** a new to-do
2. **See** all your to-dos
3. **Tick one off** as done

No fancy database, no login system, no extra features — just the notebook, built as a small API, wrapped in a container so it can run anywhere, with a robot (GitHub Actions) that checks the build every time we save new changes.

## What's inside, and why

- **`app.py`** — the actual notebook logic, written in Python using a tiny web framework called Flask.
- **The notebook itself lives in memory** — meaning it's just stored in a Python list while the server is running. Close the server, and the notebook is empty again. This is intentional — the task didn't ask for a permanent database, so we kept it simple.
- **`Dockerfile`** — a recipe that tells a computer "here's exactly how to set this project up and run it," so it works the same way on any machine, not just mine.
- **`Jenkinsfile`** — an automatic checker. Every time this repo is built by Jenkins, it tries to build the Docker recipe and tells us if something's broken, before a human even has to check.

## How to run it

### Easiest way — just Python

```bash
pip install -r requirements.txt
python3 app.py
```

The notebook is now open at `http://localhost:3000`.

### The "works on any computer" way — Docker

```bash
docker build -t todo-api .
docker run -p 3000:3000 todo-api
```

Same result, just packaged neatly so it doesn't matter what's installed on your machine.

## What each endpoint does

Think of these as four different things you can ask the notebook to do:

| What you want to do            | Method | Address              | What you send it                     |
|---------------------------------|--------|------------------------|----------------------------------------|
| "Are you awake?" (health check) | GET    | `/`                    | nothing                                |
| "Show me everything on my list" | GET    | `/tasks`               | nothing                                |
| "Add something to my list"      | POST   | `/tasks`               | `{ "title": "Buy milk" }`             |
| "Tick this one off as done"     | PATCH  | `/tasks/<id>/done`     | nothing (id is in the address itself)  |

### Try it yourself

Add something to the list:
```bash
curl -X POST localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Buy milk"}'
```

See the whole list:
```bash
curl localhost:3000/tasks
```

Mark task #1 as done:
```bash
curl -X PATCH localhost:3000/tasks/1/done
```

## What happens automatically (CI)

This repo includes a `Jenkinsfile` that defines a simple pipeline: check out the code, then build the Docker image. Every time Jenkins runs a build for this repo, it's basically double-checking "does this still work?" without anyone needing to do it by hand. It doesn't publish or deploy the app anywhere, it just proves the recipe (the Dockerfile) still works, and cleans up the built image afterward so it doesn't pile up on the Jenkins agent.

### Setting this up in Jenkins

1. Create a new **Pipeline** job in Jenkins (or a Multibranch Pipeline if you want every branch built automatically).
2. Point it at this repo's URL.
3. Set "Pipeline script from SCM" and point it to the `Jenkinsfile` in the repo root.
4. Make sure the Jenkins agent running the job has Docker installed and the Jenkins user has permission to run `docker` commands.
5. Trigger a build — it will check out the code and run `docker build`.

## Reflection

**Trickiest part:** Not the to-do logic itself — that part is genuinely small. The more thoughtful decisions were around packaging: making sure `requirements.txt` was installed *before* copying the rest of the code into the Docker image (so Docker doesn't reinstall Flask on every single code change), and keeping the `.dockerignore` clean so junk like `__pycache__` doesn't sneak into the image.

**Why these choices:** The task description explicitly said no real database was needed, so I kept storage in memory rather than adding complexity that wasn't asked for. I chose Flask because it's minimal — there's no unnecessary boilerplate between "here's a route" and "here's what it does," which keeps the code easy to read and explain. For CI, I used a Jenkins pipeline with a single build stage, matching exactly what was requested, instead of adding deployment steps that weren't needed.

**If I had another day, I'd:**
- Add real automated tests (using `pytest`) and run them as a stage in the Jenkins pipeline before the Docker build stage
- Swap the in-memory list for a lightweight file-based or SQLite database, so the to-do list survives a restart
- Add a `DELETE /tasks/<id>` endpoint to actually remove tasks, not just mark them done
- Push the built Docker image to a registry (Docker Hub / GHCR / private registry) as a second Jenkins stage, using Jenkins credentials for auth
- Add basic error handling for malformed JSON requests

> **Note:** This reflection is a starting point. Since you'll be walking through the repo live and making a change together, reread the code and put this in your own words before submitting — you should be able to explain every line out loud.
