import streamlit as st
import pandas as pd
from utils.find_alternative_parts_balanced import find_alternative_parts_balanced
from transformers import AutoModelForCausalLM, AutoTokenizer  # For Phi-1.5 integration
import torch


device= "cuda" 
# Load Product Data
@st.cache_resource
def load_data():
    df = pd.read_csv("data/Partscleaned.csv")
    df.columns = df.columns.str.strip()  # Remove unwanted spaces
    return df

df = load_data()

# Load Phi-1.5 model and tokenizer
@st.cache_resource
def load_phi_model():
    model_path = "models/phi-1.5"  # Path to your downloaded Phi-1.5 model
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    model = AutoModelForCausalLM.from_pretrained(model_path)
    return tokenizer, model

tokenizer, model = load_phi_model()

def generate_ai_explanation(prompt):
    """
    Generate an AI-based explanation using Phi-1.5.
    """
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(
        inputs.input_ids,
        max_length=200,  # Limit response length
        num_return_sequences=1,
        temperature=0.7,  # Control creativity
        top_p=0.9,  # Nucleus sampling
        do_sample=True,
    )
    response = tokenizer.decode(outputs[0], skip_special_tokens=True)
    return response

def alternative_part_page():
    st.title("🔍 Alternative Part Finder with AI Insights")

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

        # Generate AI-based Physics-Based Explanation
        st.write(f"🔬 **Physics-Based Explanation (AI-Generated):**")
        physics_prompt = f"Explain the physics behind a {fuse_type} fuse with a rated current of {rated_current}A, rated voltage of {rated_voltage}V, and breaking capacity of {breaking_capacity}A. It is used in {application} applications."
        physics_explanation = generate_ai_explanation(physics_prompt)
        st.write(physics_explanation)

        st.write(f"⚡ **Rated Current:** {rated_current}A, **Rated Voltage:** {rated_voltage}V")
        st.write(f"🔥 **Breaking Capacity:** {breaking_capacity}A, **Mounting:** {mounting}")

        # Progressive relaxation logic
        relaxation_tiers = ["Tier 1", "Tier 2", "Tier 3", "Tier 4", "Tier 5"]
        alternatives = pd.DataFrame()

        for tier in relaxation_tiers:
            if alternatives.empty:  # Only proceed if no alternatives found yet
                st.session_state.relaxation_tier = tier
                alternatives = find_alternative_parts_balanced(selected_part, df, relaxation_tier=tier)

        if alternatives.empty:
            st.warning("⚠️ No suitable alternatives found even after relaxing all constraints.")
        else:
            st.subheader("✅ Alternative Products & Justification (AI-Generated):")
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

                # Generate AI-based justification for the alternative
                justification_prompt = (
                    f"Explain why this alternative part with a {alt_fuse_type} fuse type, rated current of {alt_rated_current}A, "
                    f"rated voltage of {alt_rated_voltage}V, and breaking capacity of {alt_breaking_capacity}A is a suitable replacement "
                    f"for the original part with a {fuse_type} fuse type, rated current of {rated_current}A, rated voltage of {rated_voltage}V, "
                    f"and breaking capacity of {breaking_capacity}A. The mounting type is {alt_mounting}."
                )
                justification = generate_ai_explanation(justification_prompt)
                st.write(f"💡 **Why?** {justification}")

            # Justification for Relaxations in Filtering
            st.subheader("⚖️ Why Are Some Relaxations Allowed?")
            st.write("➡️ In some cases, exact matches are **not available**, so the following relaxations are considered:")
            st.write("✔️ **Voltage Relaxation (±10%)** → Allows alternatives within an acceptable range to function safely.")
            st.write("✔️ **Breaking Capacity Tolerance** → Small deviations are permitted if they don't impact circuit safety.")
            st.write("✔️ **Mechanical Fitment Adjustments** → If functionally compatible, slight variations in mounting style may be acceptable.")

# Run the app
alternative_part_page()