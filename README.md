# AI Agent Demo — Fictional Real Estate Project

> ⚠️ **SYNTHETIC / FICTIONAL DATA.** Every document, number, name, and policy in
> this repository is invented for demonstration purposes. No real company,
> property, development, price, or person is represented. Do not use any of
> this content for actual real estate transactions.

## Project Objective

This repository demonstrates a complete, reproducible local-development
scaffold for an AI agent application — a git repository, a Python virtual
environment with installed dependencies, a set of fictional Markdown
knowledge-base documents, and the application skeleton (ingestion, agent
logic, tools, permissions, logging) that will eventually answer questions
over those documents — using a fictional real estate development
("Sunset Meadows Residences") as the subject matter. The `src/` modules
are currently placeholders (see **Status** below); the goal right now is
to show the end-to-end project layout rather than a working agent.

## Repository Structure

```
.
├── README.md                      # this file
├── requirements.txt                # Python dependencies (Faker, pandas)
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
│   ├── ingest.py                   # loads data/*.md into a search index (TODO)
│   ├── agent.py                    # core agent loop (TODO)
│   ├── tools/
│   │   ├── search_docs.py          # doc search tool (TODO)
│   │   └── firebase_ops.py         # Firebase read/write tool (TODO)
│   ├── permissions.py              # access control (TODO)
│   ├── logging_setup.py            # logging configuration (TODO)
│   └── app.py                      # application entrypoint (TODO)
└── tests/
    └── test_questions.md           # sample Q&A test cases (TODO)
```

## Status

`data/`, `requirements.txt`, and `scripts/generate_price_list.py` are
fully built out. Everything under `src/` and `tests/` is currently a
placeholder stub (purpose comment + `TODO`) establishing the project
layout; the actual ingestion/agent/tool/permission/logging logic will be
implemented in a later stage.

## Setup

1. **Create the virtual environment** (already done in this repo under `venv/`,
   which is git-ignored — recreate it if cloning fresh):
   ```powershell
   py -3 -m venv venv
   ```

2. **Activate it**:
   ```powershell
   .\venv\Scripts\Activate.ps1
   ```

3. **Install dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

4. **Generate the synthetic price list**:
   ```powershell
   python scripts\generate_price_list.py
   ```
   This writes `data/price_list.csv`, which `data/pricing.md` summarizes.

## Dependencies

- [`Faker`](https://faker.readthedocs.io/) — generates plausible but fake
  names/labels used in the synthetic data.
- [`pandas`](https://pandas.pydata.org/) — builds and exports the tabular
  price list data.

## Disclaimer

All content under `data/` is fictional and generated for this demo. Any
resemblance to real developments, companies, prices, or people is
coincidental.
