# To-Do API — Flask + Docker + Jenkins CI/CD

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-3.0-black?logo=flask&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED?logo=docker&logoColor=white)
![Jenkins](https://img.shields.io/badge/CI%2FCD-Jenkins-D24939?logo=jenkins&logoColor=white)

A small full-stack to-do list application: a Flask REST API backed by in-memory storage, a vanilla JS front end, containerized with Docker, and deployed automatically through a Jenkins CI/CD pipeline on every push to GitHub.

This project was built as a hands-on exercise covering the full path from code → container → automated build → automated deploy.

---

## Table of Contents

- [Overview](#overview)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Project Structure](#project-structure)
- [Running Locally (without Docker)](#running-locally-without-docker)
- [Running with Docker](#running-with-docker)
- [API Endpoints](#api-endpoints)
- [CI/CD with Jenkins](#cicd-with-jenkins)
- [GitHub Webhook Setup](#github-webhook-setup)
- [Live Deployment](#live-deployment)
- [Author](#author)

---

## Overview

The app lets a user create tasks, mark them done, edit their titles, and delete them — a classic CRUD to-do list. What makes this project more than just "a to-do app" is the pipeline around it:

1. Code is pushed to **GitHub**.
2. A **GitHub webhook** notifies **Jenkins** immediately.
3. Jenkins **checks out** the latest code, **builds** a Docker image, and **deploys** it — replacing the previously running container — with zero manual steps.

Data is stored in memory (no database), so it resets whenever the container restarts.

---

## Architecture

```
 ┌──────────┐   git push    ┌──────────┐   webhook    ┌──────────┐
 │ Developer │ ────────────▶ │  GitHub   │ ────────────▶ │ Jenkins   │
 └──────────┘               └──────────┘               └────┬─────┘
                                                              │ checkout, build,
                                                              │ deploy
                                                              ▼
                                                   ┌────────────────────┐
                                                   │  Docker (EC2 host)  │
                                                   │  ┌──────────────┐  │
                                                   │  │ todo-app     │  │
                                                   │  │ container    │  │
                                                   │  │ (Flask API)  │  │
                                                   │  └──────┬───────┘  │
                                                   └─────────┼─────────┘
                                                              │ port 3000
                                                              ▼
                                                        ┌───────────┐
                                                        │  Browser   │
                                                        │  (User)    │
                                                        └───────────┘
```

---

## Tech Stack

| Layer            | Technology                         |
|-------------------|-------------------------------------|
| Backend           | Python 3.12, Flask                  |
| Frontend          | HTML, CSS, vanilla JavaScript (no framework/build step) |
| Containerization  | Docker                              |
| CI/CD             | Jenkins (Pipeline / Jenkinsfile)    |
| Source control    | Git + GitHub                        |
| Trigger           | GitHub Webhook                      |

---

## Prerequisites

To run this project you'll need:

- **Docker** (20.10+) — [installation guide](https://docs.docker.com/engine/install/)
- **Python 3.12+** — only needed if running without Docker
- **Git**
- **Jenkins** (2.4+) with Docker access — only needed to reproduce the CI/CD pipeline

No database, API keys, or `.env` file is required — the app has no external dependencies beyond Flask itself.

---

## Project Structure

```
.
├── app.py                # Flask API — all routes and in-memory task storage
├── static/
│   └── index.html        # Front end (fetch calls to the API, no build step)
├── requirements.txt       # Python dependencies
├── Dockerfile             # Container build definition
├── Jenkinsfile             # Jenkins pipeline: checkout → build → deploy
├── screenshots/            # Screenshots referenced in this README
└── README.md
```

---

## Running Locally (without Docker)

```bash
pip install -r requirements.txt
python3 app.py
```

Set a custom port if needed:
```bash
PORT=5000 python3 app.py
```

Open `http://localhost:3000` in a browser.

---

## Running with Docker

### 1. Build the image

```bash
docker build -t todo-api .
```

![Docker Build](./screenshots/docker-build.png)

### 2. Run the container

```bash
docker run -d --name todo-app-container -p 3000:3000 todo-api
```

![Docker Run](./screenshots/docker-run.png)

### 3. Confirm the container is running

```bash
docker ps
```

![Docker PS](./screenshots/docker-ps.png)

### 4. List available images

```bash
docker images
```

![Docker Images](./screenshots/docker-images.png)

Once running, open `http://<server-ip>:3000` (or `http://localhost:3000` locally) to use the app.

![App Running](./screenshots/app-running.png)

To rebuild after a code change and force a clean build (skip Docker's layer cache):

```bash
docker build --no-cache -t todo-api .
```

---

## API Endpoints

| Method | Path               | Description                                                              |
|--------|--------------------|---------------------------------------------------------------------------|
| GET    | `/`                | Serves the front end (`static/index.html`).                              |
| GET    | `/health`          | Health check → `{"status": "ok", "service": "todo-api"}`                 |
| GET    | `/tasks`           | Returns all tasks as a JSON array.                                       |
| POST   | `/tasks`           | Creates a task. Body: `{"title": "..."}`. Returns `201`, or `400` if title is missing/blank. |
| PATCH  | `/tasks/<id>`      | Updates `title` and/or `done` for a task. Returns `200`, or `404` if not found. |
| PATCH  | `/tasks/<id>/done` | Marks a task done. Returns `200`, or `404` if not found.                 |
| DELETE | `/tasks/<id>`      | Deletes a task. Returns `200` with `{"deleted": <id>}`, or `404`.        |

**Example:**

```bash
curl -X POST http://localhost:3000/tasks \
  -H "Content-Type: application/json" \
  -d '{"title":"Buy milk"}'

curl -X PATCH http://localhost:3000/tasks/1 \
  -H "Content-Type: application/json" \
  -d '{"done": true}'

curl -X DELETE http://localhost:3000/tasks/1
```

---

## CI/CD with Jenkins

The `Jenkinsfile` defines a pipeline with three stages:

1. **Checkout** — pulls the latest code from GitHub.
2. **Build Docker Image** — runs `docker build`, tagging the image with both the Jenkins build number and `latest`.
3. **Deploy** — stops and removes the previous `todo-app-container` (if running), then starts a new container from the freshly built image on port `3000`, with `--restart unless-stopped`.

After every run, dangling (unused) images are pruned so disk usage doesn't grow unbounded over time.

### Pipeline in action

![Jenkins Pipeline](./screenshots/jenkins-pipeline.png)

### Setting it up

1. Install Jenkins on the server and make sure the `jenkins` user has Docker permissions (`sudo usermod -aG docker jenkins && sudo systemctl restart jenkins`).
2. Create a new **Pipeline** job in Jenkins.
3. Under **Pipeline**, choose **"Pipeline script from SCM"** → SCM: **Git** → point it at this repo's URL, branch `main`, script path `Jenkinsfile`.
4. Save, then run **Build Now** to test it manually the first time.

---

## GitHub Webhook Setup

To make Jenkins build and deploy automatically on every `git push`, a webhook connects this GitHub repo to the Jenkins server:

1. In the GitHub repo: **Settings → Webhooks → Add webhook**.
2. **Payload URL:** `http://<jenkins-server-public-ip>:8080/github-webhook/`
3. **Content type:** `application/json`
4. **Which events:** Just the push event.
5. In the Jenkins job config, enable **"GitHub hook trigger for GITScm polling"**.

![GitHub Webhook Configuration](./screenshots/jenkins-webhook.png)

Once configured, every push to `main` triggers Jenkins automatically — no manual "Build Now" needed.

---

## Live Deployment

The app is deployed on an AWS EC2 instance, built and redeployed automatically by Jenkins on every push. The running container serves the app on port `3000`.

---

---

## Author

**Nasir Mehmood**
GitHub: [@nasirbloch323](https://github.com/nasirbloch323)

LinkedIn: [nasir-mehmood-041908205](https://www.linkedin.com/in/nasir-mehmood-041908205)
