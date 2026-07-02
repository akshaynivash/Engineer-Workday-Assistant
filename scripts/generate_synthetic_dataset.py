"""Generates data/Partscleaned.csv -- a SYNTHETIC fuse-parts catalog.

The original app expected a proprietary/scraped catalog (data/Partscleaned.csv)
that isn't in this repo and has no public equivalent on Kaggle/Hugging Face
(searched; nothing matches this schema). This script fabricates a plausible
catalog with the exact columns the filtering logic expects, using realistic
real-world fuse rating values (standard current/voltage/breaking-capacity
steps used by actual fuse manufacturers), so the app is runnable end to end.

This is clearly synthetic data, not scraped real distributor data -- fine for
demoing/testing the matching logic, not for real sourcing decisions.
"""

import csv
import random

random.seed(42)

FUSE_TYPES = ["Slow Blow", "Fast Blow", "Time Lag Blow", "PTC", "HRC", "Resettable"]
CURRENT_RATINGS = [0.5, 1, 1.5, 2, 3, 5, 7, 10, 15, 20, 25, 30]
VOLTAGE_AC = [32, 63, 125, 250, 300, 400]
VOLTAGE_DC = [24, 48, 60, 125, 150, 250]
BREAKING_CAPACITY = [35, 50, 100, 200, 1500, 10000]
MOUNTING = ["Surface Mount", "Through Hole", "Cartridge", "Blade", "Panel Mount"]
APPLICATION = ["Automotive", "Industrial", "Consumer Electronics", "Telecom", "Power Supply"]
MANUFACTURERS = ["Indicators PN", "Voltguard", "CircuitSafe", "AmpShield", "ProtecTech"]

ROW_COUNT = 2000

rows = []
for i in range(ROW_COUNT):
    fuse_type = random.choice(FUSE_TYPES)
    current = random.choice(CURRENT_RATINGS)
    voltage_ac = random.choice(VOLTAGE_AC)
    voltage_dc = random.choice(VOLTAGE_DC)
    breaking_capacity = random.choice(BREAKING_CAPACITY)
    mounting = random.choice(MOUNTING)
    application = random.choice(APPLICATION)
    manufacturer = random.choice(MANUFACTURERS)

    part_id = f"A{i + 1:03d}"
    description = (
        f"{manufacturer} Electric Fuse, {fuse_type}, {current}A, "
        f"{voltage_ac}VAC, {voltage_dc}VDC, {breaking_capacity}A (IR), {mounting}"
    )

    rows.append(
        {
            "ID": part_id,
            "DESCRIPTION": description,
            "Attribut1": fuse_type,
            "Rated Current (A)": f"{current}A",
            "Rated Voltage (V)": f"{voltage_ac}V",
            "Rated Voltage (VDC)": f"{voltage_dc}V",
            "Rated Breaking Capacity (A)": f"{breaking_capacity}A",
            "Mounting": mounting,
            "Application": application,
        }
    )

with open("data/Partscleaned.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {len(rows)} rows to data/Partscleaned.csv")
