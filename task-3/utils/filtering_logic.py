import pandas as pd

def find_alternative_parts_balanced(selected_part, df, min_alternatives=5):
    """
    Find alternative parts using a tiered filtering approach while ensuring at least `min_alternatives` results.
    First, strict filtering applies, prioritizing fuses based on the selected part's type (Fast Blow, Slow Blow, HRC, PTC, etc.).
    If strict filtering does not yield 5 alternatives, constraints are relaxed step-by-step.
    """
    # Extract key attributes of the selected part
    selected_current = selected_part["Rated Current (A)"]
    selected_voltage = selected_part["Rated Voltage (V)"]
    selected_breaking_capacity = selected_part["Rated Breaking Capacity (A)"]
    selected_mounting = selected_part["Mounting"]
    selected_application = selected_part["Application"]
    selected_fuse_type = selected_part["Attribut1"].strip().lower() if pd.notna(selected_part["Attribut1"]) else ""

    # Determine fuse type dynamically from dataset
    fuse_types = df["Attribut1"].dropna().str.lower().unique()
    fuse_filter = next((f for f in fuse_types if f in selected_fuse_type), "")

    # Tier 1: Strict Filtering (Match Fuse Type + Exact Electrical & Mechanical Match)
    strict_alternatives = df[
        (df["Rated Current (A)"] == selected_current) &
        (df["Rated Voltage (V)"] == selected_voltage) &
        (df["Rated Breaking Capacity (A)"] == selected_breaking_capacity) &
        (df["Mounting"] == selected_mounting) &
        (df["Attribut1"].str.lower().str.contains(fuse_filter, na=False) if fuse_filter else True)  # Match Fuse Type
    ]
    strict_alternatives = strict_alternatives[strict_alternatives["ID"] != selected_part["ID"]]  # Exclude itself

    if len(strict_alternatives) >= min_alternatives:
        return strict_alternatives.head(min_alternatives)

    # Tier 2: Relax Mechanical Constraints (Allow Similar Mounting/Size, Maintain Fuse Type Priority)
    relaxed_alternatives = df[
        (df["Rated Current (A)"] == selected_current) &
        (df["Rated Voltage (V)"] == selected_voltage) &
        (df["Rated Breaking Capacity (A)"] == selected_breaking_capacity) &
        (df["Attribut1"].str.lower().str.contains(fuse_filter, na=False) if fuse_filter else True)
    ]
    relaxed_alternatives = relaxed_alternatives[relaxed_alternatives["ID"] != selected_part["ID"]]

    if len(relaxed_alternatives) >= min_alternatives:
        return relaxed_alternatives.head(min_alternatives)

    # Tier 3: Allow Small Variations in Voltage & Breaking Capacity (±10% tolerance, Keep Fuse Type Priority)
    voltage_tolerance = 0.1  # Allow ±10% variation in voltage
    voltage_numeric = float(str(selected_voltage).replace("V", ""))
    breaking_capacity_numeric = float(str(selected_breaking_capacity).replace("A", "")) if pd.notna(selected_breaking_capacity) else None

    tolerated_alternatives = df[
        (df["Rated Current (A)"] == selected_current) &
        (df["Rated Voltage (V)"].str.replace("V", "").astype(float).between(
            voltage_numeric * (1 - voltage_tolerance), voltage_numeric * (1 + voltage_tolerance), inclusive="both"
        ))
    ]
    tolerated_alternatives = tolerated_alternatives[tolerated_alternatives["ID"] != selected_part["ID"]]

    if breaking_capacity_numeric:
        tolerated_alternatives = tolerated_alternatives[
            tolerated_alternatives["Rated Breaking Capacity (A)"].str.replace("A", "").astype(float).between(
                breaking_capacity_numeric * 0.9, breaking_capacity_numeric * 1.1, inclusive="both"
            )
        ]

    if len(tolerated_alternatives) >= min_alternatives:
        return tolerated_alternatives.head(min_alternatives)

    # Tier 4: Functionally Similar Parts (Last Resort - Same Application Category)
    application_alternatives = df[df["Application"] == selected_application]
    application_alternatives = application_alternatives[application_alternatives["ID"] != selected_part["ID"]]

    return application_alternatives.head(min_alternatives)
