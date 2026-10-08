# AI Agent Demo — Fictional Real Estate Project

> ⚠️ **SYNTHETIC / FICTIONAL DATA.** Every document, number, name, and policy in
> this repository is invented for demonstration purposes. No real company,
> property, development, price, or person is represented. Do not use any of
> this content for actual real estate transactions.

## Project Objective

This repository demonstrates a complete, reproducible local-development
scaffold for an AI agent application — a git repository, a `uv`-managed
Python environment with installed dependencies, a set of fictional Markdown
knowledge-base documents, and an agent (ingestion, retrieval, and
Firestore-backed write tools) that answers questions and performs actions
over that knowledge base — using a fictional real estate development
("Sunset Meadows Residences") as the subject matter. Some `src/` modules
are still placeholders (see **Status** below).

## Repository Structure

```
.
├── README.md                      # this file
├── pyproject.toml                  # project metadata + dependencies (uv)
├── uv.lock                         # locked dependency versions (uv)
├── .python-version                 # pinned Python version (3.13)
├── scripts/
│   └── generate_price_list.py      # generates synthetic unit price data
├── data/
│   ├── price_list.csv              # generated synthetic unit price list
│   ├── pricing.md                  # narrative price list overview
│   ├── spec.md                     # building/unit technical specs
│   ├── policies.md                 # fictional developer policies
│   ├── faq.md                      # frequently asked questions
│   ├── amenities.md                # building amenities
│   ├── payment_terms.md            # payment milestone schedule
│   ├── sales_process.md            # step-by-step purchase process
│   ├── floor_plans.md              # unit type/layout descriptions
│   └── legal_disclaimer.md         # fictional-content legal disclaimer
├── src/
│   ├── ingest.py                   # loads data/ + builds the Chroma index
│   ├── agent.py                    # tool-calling agent loop
│   ├── tools/
│   │   ├── search_docs.py          # semantic search over the Chroma index
│   │   └── firebase_ops.py         # Firestore tools: update_apartment_status, get_apartment_status, create_task
│   ├── permissions.py              # access control (TODO)
│   ├── logging_setup.py            # logging configuration (TODO)
│   └── app.py                      # application entrypoint (TODO)
├── chroma_db/                      # persisted Chroma vector store (generated, gitignored)
├── secrets/
│   ├── README.md                   # how to provision the Firebase service-account key (tracked)
│   └── firebase-service-account.json  # (you provide this; gitignored)
└── tests/
    └── test_questions.md           # manual regression checklist
```

## Status

`data/`, `pyproject.toml`, `scripts/generate_price_list.py`, the RAG
ingestion + retrieval pair, and the tool-calling agent (`src/agent.py`,
`src/tools/firebase_ops.py`) are built and working — a single query
returns relevant excerpts from the documents, and an instruction like
"Update unit SM-012 to sold" (after confirmation) triggers a real
Firestore write (see **Run the Agent** below). `permissions.py`,
`logging_setup.py`, and `app.py` are still placeholder stubs (purpose
comment + `TODO`).

## Setup

This project uses [`uv`](https://docs.astral.sh/uv/) for Python
environment and dependency management — no manual venv activation needed.

1. **Install dependencies** (creates `.venv/` and `uv.lock` automatically):
   ```powershell
   uv sync
   ```

2. **Generate the synthetic price list**:
   ```powershell
   uv run python scripts\generate_price_list.py
   ```
   This writes `data/price_list.csv`, which `data/pricing.md` summarizes.

3. **Add a new dependency** (updates `pyproject.toml` + `uv.lock`):
   ```powershell
   uv add <package-name>
   ```

## Build & Query the RAG Index

Requires an `OPENAI_API_KEY` set in your environment (used for
embeddings; no `.env` file needed if it's already a system/user env var).

1. **Build the index** — loads `data/*.md` + `data/price_list.csv`,
   chunks, embeds, and persists to `chroma_db/`. Safe to re-run any
   time: it resets the Chroma collection first, so repeated runs don't
   accumulate duplicate chunks. It also idempotently seeds Firestore's
   `apartments` collection from the CSV (skipped with a warning if no
   Firebase credentials are set up yet — see **Run the Agent** below;
   existing docs, e.g. ones already updated live, are left untouched):
   ```powershell
   uv run python src\ingest.py
   ```

2. **Query it**:
   ```powershell
   uv run python src\tools\search_docs.py "What is the cancellation policy?"
   ```
   Prints the top matching excerpts with their source document.

## Run the Agent

`src/agent.py` is a tool-calling agent that can answer questions (via
`search_knowledge_base`), look up a unit's live status (via
`get_apartment_status`), and take real write actions against Firestore
(`update_apartment_status`, `create_task`).

Apartments are identified by `unit_code` everywhere — the same format
used in `data/price_list.csv` (e.g. `"SM-012"`), not a bare number. This
is deliberate: `update_apartment_status` checks the unit exists in
Firestore before writing anything, so a bare/invalid code fails loudly
instead of silently creating a bogus record.

Write actions (`update_apartment_status`, `create_task`) print the
proposed call and ask for `[y/N]` confirmation before executing — pass
`--yes`/`-y` to skip the prompt (e.g. for scripted/non-interactive runs).

1. **Provision a demo Firebase project** (not a real client's) — see
   [`secrets/README.md`](secrets/README.md) for the exact console steps.
   Save the downloaded key as `secrets/firebase-service-account.json`
   (gitignored), or point `FIREBASE_SERVICE_ACCOUNT_PATH` at it instead.
2. **Seed Firestore** (if you haven't already) by running the index
   build above — it populates `apartments` from the CSV.
3. **Run an instruction**:
   ```powershell
   uv run python src\agent.py "Update unit SM-012 to sold"
   ```
   This calls `update_apartment_status("SM-012", "Sold")`, which updates
   the existing `apartments/SM-012` doc (after you confirm). Other
   examples:
   ```powershell
   uv run python src\agent.py "What is the status of unit SM-012?"
   uv run python src\agent.py "Create a task to schedule a handover walkthrough for unit SM-012" --yes
   uv run python src\agent.py "What amenities does the building have?"
   ```
   The agent picks the right tool (or none, for pure Q&A) automatically.

## Dependencies

- [`Faker`](https://faker.readthedocs.io/) — generates plausible but fake
  names/labels used in the synthetic data.
- [`pandas`](https://pandas.pydata.org/) — builds and exports the tabular
  price list data.
- [`langchain-core`](https://python.langchain.com/) /
  [`langchain-text-splitters`](https://python.langchain.com/) — document
  and chunking abstractions used by `src/ingest.py`.
- [`langchain-openai`](https://python.langchain.com/docs/integrations/platforms/openai/)
  — OpenAI embeddings (`text-embedding-3-small`).
- [`langchain-chroma`](https://python.langchain.com/docs/integrations/vectorstores/chroma/)
  — persists/queries the local [Chroma](https://www.trychroma.com/)
  vector store.
- [`firebase-admin`](https://firebase.google.com/docs/admin/setup) —
  server-side Firestore reads/writes used by `src/tools/firebase_ops.py`.

## Disclaimer

All content under `data/` is fictional and generated for this demo. Any
resemblance to real developments, companies, prices, or people is
coincidental.
