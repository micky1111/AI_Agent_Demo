# Price List — Sunset Meadows Residences

> **SYNTHETIC / FICTIONAL DATA — for demo purposes only.**

Sunset Meadows Residences is a fictional 10-floor residential development
with 40 units across five layout types. The full machine-generated price
list lives in [`data/price_list.csv`](../data/price_list.csv) (produced by
`scripts/generate_price_list.py`). A representative sample is shown below.

| Unit Code | Floor | Type       | Size (sqm) | Price (fictional currency units) | Status    |
|-----------|-------|------------|------------|-----------------------------------|-----------|
| SM-012    | 1     | 1 Bedroom  | 57         | 185,100                           | Reserved  |
| SM-013    | 1     | 2 Bedroom  | 86         | 279,300                           | Sold      |
| SM-014    | 1     | 3 Bedroom  | 116        | 376,800                           | Available |
| SM-011    | 1     | Penthouse  | 173        | 561,900                           | Reserved  |
| SM-022    | 2     | Studio     | 38         | 125,200                           | Sold      |

## Pricing Notes

- Prices are quoted per unit and include the base shell, standard finishes,
  and one parking space (see [Amenities](amenities.md)).
- Prices increase marginally by floor to reflect view and elevation.
- Published prices are indicative and subject to change until a reservation
  agreement is signed — see [Company Policies](company_policies.md).
- VAT/transfer taxes (fictional, jurisdiction-dependent) are **not**
  included in the listed price.
- For payment scheduling, see [Payment Terms](payment_terms.md).

## Regenerating the Price List

```powershell
.\venv\Scripts\python.exe .\scripts\generate_price_list.py
```

This overwrites `data/price_list.csv` with a fresh (seeded, reproducible)
synthetic dataset.
