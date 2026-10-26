#!/usr/bin/env python3
"""Payment reconciliation.

Reads payments.jsonl and works out how much money we actually collected.
Run:  python3 reconcile.py
"""
import json
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

events_by_txn = {}
data_dir = Path(__file__).resolve().parent

with (data_dir / "payments.jsonl").open("rb") as f:
    for line in f:
        try:
            event = json.loads(line)
        except (json.JSONDecodeError, UnicodeDecodeError):
            continue

        txn_id = event.get("txn_id")
        if not txn_id:
            continue

        previous = events_by_txn.get(txn_id)
        if previous is None or event["ts"] > previous["ts"]:
            events_by_txn[txn_id] = event

successful_events = [
    event for event in events_by_txn.values() if event["status"] == "success"
]
count = len(successful_events)
total = sum(
    (Decimal(str(event["amount"]).replace(",", "")) for event in successful_events),
    Decimal(0),
)

with (data_dir / "expected.txt").open(encoding="utf-8") as f:
    expected = int(f.read().strip())

if count != expected:
    print(f"Check failed: counted {count} successful payments, expected {expected}.")
    print("Something in the data isn't being handled the way the README describes.")
else:
    print(f"Check passed: {count} successful payments.")
    rounded_total = total.quantize(Decimal("1"), rounding=ROUND_HALF_UP)
    print(f"Your code: KOYA-{rounded_total}")
