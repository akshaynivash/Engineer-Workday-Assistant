import streamlit as st


def home_page():
    st.title("🔧 Alternative Part Finder — Engineer's Assistant")
    st.write(
        "This app grew out of one core tool — **finding a replacement electronic part when your "
        "first choice is out of stock or doesn't quite fit** — and now bundles two more assistant "
        "tools alongside it, for convenience. Here's what each one is actually for, and when to reach "
        "for it."
    )

    st.divider()

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🔍 Alternative Part Finder")
        st.write(
            "**The main tool.** You have a fuse's part ID and it's unavailable, discontinued, or "
            "doesn't quite meet spec — find a suitable replacement."
        )
        st.markdown(
            "- Enter a part **ID** (e.g. `A001`)\n"
            "- See its specs and a physics-based explanation\n"
            "- Get ranked alternatives, loosest-to-strictest match\n"
            "- Not sure which ID to try? The page has a **browse/search** panel."
        )

    with col2:
        st.subheader("💬 Chatbot")
        st.write(
            "**General conversation**, unrelated to part-finding — for quick questions or just "
            "talking through something while you work. Runs fully offline (Blenderbot), no internet "
            "or API key needed once the model is downloaded."
        )
        st.markdown("- Casual chat\n- Offline-friendly\n- Not for part lookups — use Part Finder for that")

    with col3:
        st.subheader("🦙 Personal Assistant")
        st.write(
            "**A bonus sidekick** for the rest of your workday: keep track of your schedule, plan "
            "meals, and get study help on material you've indexed. Understands natural phrasing, not "
            "just exact keywords."
        )
        st.markdown(
            "- *\"What's my Monday schedule?\"*\n"
            "- *\"Plan my meals for this week\"*\n"
            "- *\"Explain today's topic from the PDF\"*\n"
            "- Also tracks daily check-in tasks"
        )

    st.divider()
    st.caption(
        "Pick a page from the sidebar. Chatbot and Personal Assistant need extra models/services set up "
        "locally (see README) — if they're not available, you'll see a friendly note instead of a crash, "
        "and the rest of the app keeps working."
    )
