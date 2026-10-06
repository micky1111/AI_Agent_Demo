# AI Agent Demo — Fictional Real Estate Project

> ⚠️ **SYNTHETIC / FICTIONAL DATA.** Every document, number, name, and policy in
> this repository is invented for demonstration purposes. No real company,
> property, development, price, or person is represented. Do not use any of
> this content for actual real estate transactions.

## Project Objective

This repository demonstrates a complete, reproducible local-development
scaffold — a git repository, a Python virtual environment with installed
dependencies, and a structured set of Markdown content documents — using a
fictional real estate development ("Sunset Meadows Residences") as the
subject matter. The goal is to show the end-to-end workflow (environment
setup → dependency installation → synthetic data generation → document
authoring) rather than to produce any real-world property listing or
business content.

## Repository Structure

```
.
├── README.md                      # this file
├── requirements.txt                # Python dependencies (Faker, pandas)
├── scripts/
│   └── generate_price_list.py      # generates synthetic unit price data
├── data/
│   └── price_list.csv              # generated synthetic unit price list
└── docs/
    ├── price_list.md               # narrative price list overview
    ├── technical_specifications.md # building/unit technical specs
    ├── company_policies.md         # fictional developer policies
    ├── faq.md                      # frequently asked questions
    ├── amenities.md                # building amenities
    ├── payment_terms.md            # payment milestone schedule
    ├── sales_process.md            # step-by-step purchase process
    ├── floor_plans.md              # unit type/layout descriptions
    └── legal_disclaimer.md         # fictional-content legal disclaimer
```

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
   This writes `data/price_list.csv`, which `docs/price_list.md` summarizes.

## Dependencies

- [`Faker`](https://faker.readthedocs.io/) — generates plausible but fake
  names/labels used in the synthetic data.
- [`pandas`](https://pandas.pydata.org/) — builds and exports the tabular
  price list data.

## Disclaimer

All content under `docs/` and `data/` is fictional and generated for this
demo. Any resemblance to real developments, companies, prices, or people is
coincidental.
