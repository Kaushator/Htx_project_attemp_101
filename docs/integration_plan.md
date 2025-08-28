# HTX Project OpenAI Integration Plan

## Overview

This document outlines the integration of OpenAI Responses API (JSON mode), Batch API, Embeddings API and Function Calling into the HTX trading analytics project. The goal is to automate experiment generation, improve data cleaning and labeling, enable semantic search over logs and trade histories, implement automated evaluation of signal quality and orchestrate long‑running tasks via function calls.

### Key objectives

* **Experiment planning (AutoML)** – support automatic generation of machine‑learning experiment configurations. Use JSON‑mode of the Responses API with a strict schema so the model returns a validated configuration (model type, hyperparameters, feature list, backtest parameters). Pass the config through a Pydantic validator and feed it into the training/backtesting pipeline.
* **Massive data cleaning and labeling** – use OpenAI Batch API to process large CSV files offline for weak labeling, deduplication and normalization of text fields (e.g. order‑cancellation reasons or API error messages). Batch jobs run on a separate quota and are cheaper than online calls.
* **Semantic search over logs, trades and tickets** – use embeddings (e.g. `text‑embedding‑3‑small`) to convert event descriptions into vectors and store them in a `pgvector` table. Provide a kNN search endpoint to find similar incidents and tasks across the project history.
* **LLM‑as‑judge and A/B evaluation** – implement automated evaluation of signals or handler outputs using structured prompts and scoring rubrics. Use the Responses API to produce ranked feedback and summary metrics for A/B tests.
* **Function calling for orchestration** – expose internal functions such as `start_training(config)`, `run_backtest(params)` or `fetch_htx(symbol, tf)` via the OpenAI function‑calling interface. The assistant can call these functions directly to orchestrate workflows.
* **Confidentiality** – ensure sensitive data (API keys, secrets, personally identifiable information) is never sent to OpenAI. Only send hashed or truncated values when necessary. Use environment variables to store secrets and load them server‑side.

## Architecture additions

### New modules

* `backend/app/services/openai_client.py` – wrapper functions for the OpenAI APIs:
  * `json_mode(task: dict, schema: dict) -> dict` – calls the Responses API in JSON‑mode to generate experiment configs and validates the result.
  * `batch_label(records: list[str], prompts: dict) -> list[str]` – submits CSV rows to the Batch API for labeling/cleaning and returns results when the job completes.
  * `embed_texts(texts: list[str]) -> numpy.ndarray` – calls the embeddings API to produce vectors for semantic search.
* `backend/app/services/embedding_indexer.py` – maintains a `pgvector` index of embeddings, updates vectors for new events and implements kNN search queries.
* `backend/app/services/experiment_service.py` – orchestrates experiment planning and training/backtesting using configurations produced by `openai_client.json_mode`.
* API endpoints under `backend/app/api/v1/endpoints/`:
  * `/ml/plan` – accepts a machine‑learning task description and constraints, calls `json_mode` to generate a config and schedules training/backtesting.
  * `/ml/batch_label` – accepts an uploaded CSV and triggers a Batch API job via a background worker for labeling/cleaning.
  * `/search/similar` – accepts a query (text or event ID) and returns the most similar events based on embeddings.
  * `/eval` (optional) – triggers an LLM‑as‑judge evaluation of candidate signals or outputs and returns metrics.
* `backend/app/workers/openai_worker.py` – background worker functions for processing batch jobs, indexing embeddings and evaluating outputs. To be run via Celery or RQ.
* New SQLAlchemy models in `backend/app/models/`:
  * `experiment.py` – stores experiment configurations and their statuses.
  * `embedding.py` – stores embedding vectors with `pgvector` type, associated item IDs and metadata.
  * `batch_job.py` – tracks Batch API jobs and results.

### Configuration

* Extend `backend/app/core/config.py` with new variables such as `OPENAI_API_KEY`, `EMBEDDING_MODEL`, `JSON_MODE_MODEL` and limits for batch size and concurrent jobs.
* Update `.env.example` with placeholders for these variables and describe their usage in the README.
* Ensure file paths are Linux‑style to support the WSL environment. Use `/home/user/...` paths for uploads and temporary data.

### Docker/WSL

* Update `docker-compose.yml` to include:
  * A Postgres service configured with the `pgvector` extension (if not already present).
  * A new `openai-worker` service that runs the background worker (`openai_worker.py`) and shares the code volume with the FastAPI container.
* Add the required Python packages (openai, numpy, pgvector, pydantic) to `requirements.txt`.
* Provide a bash script for WSL users to start both the API and worker containers.

### Semantic search and embeddings

1. Add an `embeddings` table with columns `id`, `item_id`, `source`, `vector` (pgvector type) and `metadata`. Items can represent trades, logs or support tickets.
2. Implement a service to compute embeddings for new events (e.g. on file import or API sync) and upsert them into the database.
3. Provide a kNN search method using Postgres `vector <=>` operator to retrieve the top‐k similar items.

### Experiment scheduling

1. Define a Pydantic schema for experiment configurations. Include fields for `model` (e.g. "xgboost", "lgbm", "catboost"), `features` (list of strings), `hyperparams` (dictionary), and `backtest` (object with start/end dates, metrics and trading fees).
2. Implement the `/ml/plan` endpoint to accept a JSON body describing the prediction task (symbols, timeframe, lookback window, constraints). It will call `openai_client.json_mode` with a system prompt and user message and a JSON schema. The returned configuration is validated and stored in the `experiments` table.
3. Use background tasks to launch training and backtesting. The service returns quickly with a job ID and a link to check status.

### Batch labeling pipeline

1. Provide an endpoint to upload a CSV file for labeling. Save the file and create a `batch_job` record.
2. The `openai-worker` reads the file, constructs prompt templates for each row and submits them to the Batch API. It polls until completion and writes the results to a new CSV or directly into the database.
3. Expose job status via `/ml/batch_label/{job_id}` and allow downloading the labeled file once complete.

### Evaluation (LLM‑as‑judge and A/B tests)

1. Define evaluation prompts and structured scoring rubrics for the relevant tasks (e.g. signal quality, order handling). Use the Responses API to obtain scores and qualitative feedback.
2. Use A/B testing by running two configurations and comparing their evaluation results. Store metrics in a new table and provide endpoints to retrieve them.

### Function calling integration

1. Define function signatures that the assistant can call, such as `start_training(config: dict)`, `run_backtest(params: dict)`, and `fetch_htx(symbol: str, tf: str)`. Implement these functions in the backend and register them with the OpenAI client.
2. When calling the Responses API, include the function definitions in the request so the model can orchestrate tasks. The model will return a JSON with the function name and arguments when appropriate.

## Implementation steps

1. Create a new branch `feature/openai-integration` based off `main`.
2. Scaffold the new service modules (`openai_client.py`, `embedding_indexer.py`, `experiment_service.py`) and add placeholders with docstrings.
3. Add new SQLAlchemy models and their Alembic migrations for experiments, embeddings and batch jobs.
4. Implement API endpoints and worker functions with asynchronous operations and proper error handling.
5. Update configuration files and `.env.example`; add new dependencies to `requirements.txt`.
6. Extend `docker-compose.yml` to include Postgres with `pgvector` and an `openai-worker` service. Provide a Bash script for WSL to run both services.
7. Write tests for the new modules and endpoints, including JSON schema validation and embedding search.
8. Document the usage of new features in `docs/` and provide examples of prompt design, API requests and expected outputs.
9. Open a pull request for review once the branch is ready.

## WSL considerations

The project runs in a WSL (Linux) environment. Ensure that all file paths and Docker volumes use Linux conventions (e.g. `/home/user/data`) and that any shell scripts are written in Bash rather than PowerShell. Install required system packages (e.g. `postgresql-server-dev`) in WSL before building the Docker images. Test the new functionality in WSL to avoid path issues or permission errors.
