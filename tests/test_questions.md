# Test Questions

Manual regression checklist for `src/agent.py`. Run each instruction via
`uv run python src\agent.py "<instruction>"` and confirm the actual
response matches the expected behavior. Re-run after editing anything
under `data/` or `src/tools/`.

## Knowledge-base Q&A (search_knowledge_base)

| # | Instruction | Expected source(s) | Expected answer (summary) |
|---|---|---|---|
| 1 | What is the cancellation policy? | `policies.md`, `payment_terms.md` | Reservation deposit (2%) fully refundable within the 7-day hold window; after SPA signing, refund of amounts beyond the deposit follows the post-SPA cancellation schedule in `payment_terms.md`. |
| 2 | What is the reservation deposit? | `policies.md`, `payment_terms.md` | 2% of the unit's price, refundable within the 7-day hold window. (Must match between both docs — this was previously inconsistent: see note below.) |
| 3 | What amenities does the building have? | `amenities.md` | Lobby/concierge, gym, rooftop terrace, co-working lounge, residents' lounge, children's play area, pet wash, parking/storage, security. |
| 4 | What is the price of a 2 bedroom unit? | `price_list.csv` | Returns one or more real rows with `unit_type: 2 Bedroom` and a price. |
| 5 | What technical standards does the building meet? | `spec.md` | Structural/MEP/sustainability specifics (fictional). |

## Live status (get_apartment_status) — Firestore is the source of truth

| # | Instruction | Expected behavior |
|---|---|---|
| 6 | What is the status of unit SM-012? | Calls `get_apartment_status`, not `search_knowledge_base` — returns Firestore's current value, which may differ from the original CSV if it was updated since. |
| 7 | What is the status of unit SM-999? | Reports the unit doesn't exist (no such doc in Firestore). |

## Write actions (update_apartment_status, create_task) — require confirmation

| # | Instruction | Expected behavior |
|---|---|---|
| 8 | Update unit SM-012 to sold | Prompts for confirmation before writing; on confirm, `apartments/SM-012.status` becomes `"Sold"` in Firestore. On decline, nothing is written. |
| 9 | Update apartment 12 to sold | Should **not** silently write to a doc called "12" — the agent should either ask for the full unit code (format `SM-0NN`) or fail clearly via `update_apartment_status`'s existence check, since "12" is not a real `unit_code`. |
| 10 | Update unit SM-999 to sold | `update_apartment_status` reports the unit doesn't exist; no doc is created. |
| 11 | Create a task to schedule a handover walkthrough for unit SM-012 | Prompts for confirmation; on confirm, adds a doc to `tasks`. |
| 12 | (Repeat #11 immediately after) | Second call detects the existing open task with the same title + unit_code and reports it as a duplicate instead of creating a second one. |

## Known content caveats

- #2 above was previously inconsistent (`policies.md` said a flat 5,000
  fee, `payment_terms.md` said 2%) — now unified to 2% in both. If you
  see contradicting numbers again, fix the docs, not just one answer.
- `payment_terms.md`'s post-SPA cancellation refund schedule was missing
  entirely (policies.md referenced it but it didn't exist) — now added.
  If an answer about post-SPA cancellation refunds doesn't cite a
  specific percentage, the docs have regressed.
