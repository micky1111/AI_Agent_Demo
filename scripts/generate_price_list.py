"""
generate_price_list.py

Generates a SYNTHETIC unit price list for the fictional development
"Sunset Meadows Residences" and writes it to data/price_list.csv.

This script exists purely to demonstrate the venv + dependency-install
workflow (Faker for fake-but-plausible labels, pandas for tabular data).
None of the output represents a real property, price, or person.
"""

from pathlib import Path

import pandas as pd
from faker import Faker

fake = Faker()
Faker.seed(42)  # reproducible output for the demo

UNIT_TYPES = ["Studio", "1 Bedroom", "2 Bedroom", "3 Bedroom", "Penthouse"]
STATUSES = ["Available", "Reserved", "Sold"]

BASE_PRICE_PER_SQM = 3200  # fictional currency units, e.g. USD-equivalent


def make_unit(unit_id: int) -> dict:
    floor = (unit_id - 1) // 4 + 1
    unit_type = UNIT_TYPES[unit_id % len(UNIT_TYPES)]
    size_sqm = {
        "Studio": 38,
        "1 Bedroom": 55,
        "2 Bedroom": 82,
        "3 Bedroom": 110,
        "Penthouse": 165,
    }[unit_type]
    # Small deterministic variation so not every unit of a type is identical.
    size_sqm += (unit_id % 5) * 2
    price = round(size_sqm * BASE_PRICE_PER_SQM * (1 + 0.015 * floor), -2)
    status = STATUSES[unit_id % len(STATUSES)]

    return {
        "unit_code": f"SM-{floor:02d}{unit_id % 4 + 1:01d}",
        "floor": floor,
        "unit_type": unit_type,
        "size_sqm": size_sqm,
        "price": int(price),
        "status": status,
        "listing_agent": fake.name(),
    }


def main() -> None:
    units = [make_unit(i) for i in range(1, 41)]  # 40 fictional units
    df = pd.DataFrame(units)

    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "price_list.csv"
    df.to_csv(out_path, index=False)

    print(f"Wrote {len(df)} synthetic units to {out_path}")
    print(df.head())


if __name__ == "__main__":
    main()
