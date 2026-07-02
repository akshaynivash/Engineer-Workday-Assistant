import pandas as pd

def find_alternative_parts_balanced(selected_part, df, min_alternatives=5, relaxation_tier="Tier 1"):
    """
    Find alternative parts using a tiered filtering approach while ensuring at least `min_alternatives` results.
    Prioritizes fuse type, electrical characteristics, and mounting style before relaxing constraints.
    """

    # Extract key attributes of the selected part
    selected_current = float(str(selected_part["Rated Current (A)"]).replace("A", "").strip())
    selected_voltage_ac = selected_part["Rated Voltage (V)"]  # AC voltage
    selected_voltage_dc = selected_part["Rated Voltage (VDC)"] if "Rated Voltage (VDC)" in selected_part else None
    selected_breaking_capacity = selected_part["Rated Breaking Capacity (A)"]
    selected_mounting = selected_part["Mounting"]
    selected_application = selected_part["Application"]
    selected_fuse_type = selected_part["Attribut1"].strip().lower() if pd.notna(selected_part["Attribut1"]) else None

    # Remove rows with missing fuse types
    df = df.dropna(subset=["Attribut1"]).copy()

    # Convert numerical columns safely
    df["Rated Current (A)"] = pd.to_numeric(df["Rated Current (A)"].astype(str).str.replace("A", ""), errors='coerce')
    df["Rated Voltage (V)"] = pd.to_numeric(df["Rated Voltage (V)"].astype(str).str.replace("V", ""), errors='coerce')
    if "Rated Voltage (VDC)" in df.columns:
        df["Rated Voltage (VDC)"] = pd.to_numeric(df["Rated Voltage (VDC)"].astype(str).str.replace("V", ""), errors='coerce')
    
    df["Rated Breaking Capacity (A)"] = pd.to_numeric(df["Rated Breaking Capacity (A)"].astype(str).str.replace("A", ""), errors='coerce')

    # Fill missing numerical values with the median
    df["Rated Voltage (V)"] = df["Rated Voltage (V)"].fillna(df["Rated Voltage (V)"].median())
    if "Rated Voltage (VDC)" in df.columns:
        df["Rated Voltage (VDC)"] = df["Rated Voltage (VDC)"].fillna(df["Rated Voltage (VDC)"].median())

    df["Rated Breaking Capacity (A)"] = df["Rated Breaking Capacity (A)"].fillna(df["Rated Breaking Capacity (A)"].median())

    # Convert selected values to float safely
    selected_voltage_ac = pd.to_numeric(str(selected_voltage_ac).replace("V", ""), errors='coerce')
    selected_voltage_dc = pd.to_numeric(str(selected_voltage_dc).replace("V", ""), errors='coerce') if selected_voltage_dc else None
    selected_breaking_capacity = pd.to_numeric(str(selected_breaking_capacity).replace("A", ""), errors='coerce')

    # Use median if selected values are missing
    if pd.isna(selected_voltage_ac):
        selected_voltage_ac = df["Rated Voltage (V)"].median()
    
    if selected_voltage_dc is not None and pd.isna(selected_voltage_dc):
        selected_voltage_dc = df["Rated Voltage (VDC)"].median()

    if pd.isna(selected_breaking_capacity):
        selected_breaking_capacity = df["Rated Breaking Capacity (A)"].median()

    # Ensure voltage filtering is correct for both AC and DC
    df = df[df["Rated Voltage (V)"] >= selected_voltage_ac]  # Ensure only equal or higher AC voltage
    if "Rated Voltage (VDC)" in df.columns and selected_voltage_dc is not None:
        df = df[df["Rated Voltage (VDC)"] >= selected_voltage_dc]  # Ensure only equal or higher DC voltage

    # Fuse type is required to match for every tier EXCEPT Tier 5, which explicitly
    # allows different fuse types. (Previously this filter ran unconditionally before
    # any tier logic, so "Tier 5: Allow Different Fuse Types" could never actually
    # relax it -- it behaved identically to Tier 3/4.)
    if relaxation_tier != "Tier 5":
        df = df[df["Attribut1"].str.lower() == selected_fuse_type]

    # 🛠 **Tier 1: Strict Matching (Fuse Type + Exact Electrical & Mechanical Match)**
    if relaxation_tier == "Tier 1":
        alternatives = df[
            (df["Rated Current (A)"].between(selected_current - 2, selected_current + 2)) &  # Allow ±2A range
            (df["Rated Breaking Capacity (A)"].between(selected_breaking_capacity * 0.9, selected_breaking_capacity * 1.1)) &
            (df["Mounting"] == selected_mounting)
        ]
    # 🛠 **Tier 2: Allow Minor Breaking Capacity Variations (mounting no longer required)**
    elif relaxation_tier == "Tier 2":
        alternatives = df[
            (df["Rated Current (A)"].between(selected_current - 2, selected_current + 2)) &
            (df["Rated Breaking Capacity (A)"].between(selected_breaking_capacity * 0.8, selected_breaking_capacity * 1.2))
        ]
    # 🛠 **Tier 3/4: Relax Current Tolerance Further (±5A).** Tier 4's "different mounting"
    # framing is already true from Tier 2 onward -- there's no further mounting constraint
    # left to drop, so these two tiers are intentionally identical rather than duplicated
    # by accident.
    elif relaxation_tier in ("Tier 3", "Tier 4"):
        alternatives = df[
            (df["Rated Current (A)"].between(selected_current - 5, selected_current + 5)) &
            (df["Rated Breaking Capacity (A)"].between(selected_breaking_capacity * 0.8, selected_breaking_capacity * 1.2))
        ]
    # 🛠 **Tier 5: Allow Different Fuse Types** -- same numeric tolerances as Tier 3/4, but
    # `df` here was never filtered down to a single fuse type above.
    elif relaxation_tier == "Tier 5":
        alternatives = df[
            (df["Rated Current (A)"].between(selected_current - 5, selected_current + 5)) &
            (df["Rated Breaking Capacity (A)"].between(selected_breaking_capacity * 0.8, selected_breaking_capacity * 1.2))
        ]
    else:
        alternatives = pd.DataFrame()  # Default to empty DataFrame

    alternatives = alternatives[alternatives["ID"] != selected_part["ID"]]
    return alternatives.head(min_alternatives)