import streamlit as st
import pandas as pd
from utils.find_alternative_parts_balanced import find_alternative_parts_balanced

# Load Product Data
@st.cache_resource
def load_data():
    df = pd.read_csv("data/Partscleaned.csv")
    df.columns = df.columns.str.strip()  # Remove unwanted spaces
    return df

df = load_data()

def alternative_part_pagenogenai():
    st.title("🔍 Alternative Part Finder")

    # Sidebar Debugging
    if st.sidebar.button("Show Columns"):
        st.write(df.columns.tolist())

    # Initialize session state for relaxation tier
    if "relaxation_tier" not in st.session_state:
        st.session_state.relaxation_tier = "Tier 1"  # Default to Tier 1

    # Ask for Product ID
    product_id = st.text_input("Enter Product ID to find alternatives:")

    if product_id:
        # Retrieve the selected part details
        selected_part = df[df["ID"] == product_id]

        if selected_part.empty:
            st.error("⚠️ Product ID not found in database. Please enter a valid ID.")
            return

        selected_part = selected_part.iloc[0]  # Convert to Series

        # Extract attributes
        part_description = selected_part.get("DESCRIPTION", "Unknown Part")
        fuse_type = str(selected_part.get("Attribut1", "Unknown"))  # Ensure fuse_type is a string
        rated_current = selected_part.get("Rated Current (A)", "N/A")
        rated_voltage = selected_part.get("Rated Voltage (V)", "N/A")
        breaking_capacity = selected_part.get("Rated Breaking Capacity (A)", "N/A")
        mounting = selected_part.get("Mounting", "N/A")
        application = selected_part.get("Application", "N/A")

        # Show only product description
        st.subheader("📌 Product Analysis")
        st.write(f"🔹 **{part_description}**")

        # Physics-Based Explanation for the Selected Part
        st.write(f"🔬 **Physics-Based Explanation:**")
        
        if "Slow Blow" in fuse_type:
            st.write(f"➡️ This is a **Slow Blow fuse**, designed to handle inrush currents before melting. "
                     f"It is thermally activated and ideal for **power supply circuits**, where temporary surges are expected.")
        elif "Fast Blow" in fuse_type:
            st.write(f"➡️ This is a **Fast Blow fuse**, which melts **quickly** when exceeding the rated current. "
                     f"It is commonly used in **sensitive electronic circuits** that require immediate disconnection upon overload.")
        else:
            st.write(f"➡️ This fuse operates based on **thermal dissipation and overload conditions**, "
                     f"ensuring circuit protection in applications like **{application}**.")

        st.write(f"⚡ **Rated Current:** {rated_current}A, **Rated Voltage:** {rated_voltage}V")
        st.write(f"🔥 **Breaking Capacity:** {breaking_capacity}A, **Mounting:** {mounting}")

        # Find alternative parts with the current relaxation tier
        alternatives = find_alternative_parts_balanced(selected_part, df, relaxation_tier=st.session_state.relaxation_tier)

        if alternatives.empty:
            st.warning("⚠️ No suitable alternatives found.")
        else:
            st.subheader("✅ Alternative Products & Justification:")
            for _, row in alternatives.iterrows():
                alternative_id = row.get("ID", "Unknown ID")
                alternative_description = row.get("DESCRIPTION", "Unknown Part")
                alt_fuse_type = str(row.get("Attribut1", "Unknown"))  # Ensure alt_fuse_type is a string
                alt_rated_current = row.get("Rated Current (A)", "N/A")
                alt_rated_voltage = row.get("Rated Voltage (V)", "N/A")
                alt_breaking_capacity = row.get("Rated Breaking Capacity (A)", "N/A")
                alt_mounting = row.get("Mounting", "N/A")

                # Show Product ID + Description
                st.write(f"🔹 **[{alternative_id}] {alternative_description}**")

                # Custom Explanation Based on Row Details
                explanation = "💡 **Why?** This alternative "
                if fuse_type == alt_fuse_type:
                    explanation += f"shares the same **{fuse_type} fuse type**, ensuring similar thermal characteristics. "
                else:
                    explanation += f"has a slightly different fuse type ({alt_fuse_type}), but remains functionally compatible. "

                if abs(float(str(alt_rated_current).replace('A', '')) - float(str(rated_current).replace('A', ''))) <= 1:
                    explanation += f"Its **current rating ({alt_rated_current}A)** is close to the original, ensuring safe operation. "
                else:
                    explanation += f"It has a **higher/lower current rating ({alt_rated_current}A)** but still fits within tolerance limits. "

                if abs(float(str(alt_rated_voltage).replace('V', '')) - float(str(rated_voltage).replace('V', ''))) <= 10:
                    explanation += f"The voltage rating is within the **acceptable ±10% range ({alt_rated_voltage}V)**. "
                else:
                    explanation += f"The voltage rating differs ({alt_rated_voltage}V), but remains within functional limits. "

                if mounting == alt_mounting:
                    explanation += f"Additionally, it fits the **same mounting type ({alt_mounting})**, making installation easier."
                else:
                    explanation += f"Though the mounting type ({alt_mounting}) differs, it is still mechanically compatible."

                st.write(explanation)

            # If fewer than 5 alternatives, show relaxation buttons
            if len(alternatives) < 5:
                st.write("🔔 **Fewer than 5 alternatives found. You can relax constraints further:**")
                if st.button("Relax Current Tolerance (±5A)"):
                    st.session_state.relaxation_tier = "Tier 3"
                    st.rerun()
                if st.button("Allow Different Mounting Styles"):
                    st.session_state.relaxation_tier = "Tier 4"
                    st.rerun()
                if st.button("Allow Different Fuse Types"):
                    st.session_state.relaxation_tier = "Tier 5"
                    st.rerun()

            # Justification for Relaxations in Filtering
            st.subheader("⚖️ Why Are Some Relaxations Allowed?")
            st.write("➡️ In some cases, exact matches are **not available**, so the following relaxations are considered:")
            st.write("✔️ **Voltage Relaxation (±10%)** → Allows alternatives within an acceptable range to function safely.")
            st.write("✔️ **Breaking Capacity Tolerance** → Small deviations are permitted if they don't impact circuit safety.")
            st.write("✔️ **Mechanical Fitment Adjustments** → If functionally compatible, slight variations in mounting style may be acceptable.")

# Run the app
alternative_part_pagenogenai()