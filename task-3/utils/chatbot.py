import streamlit as st


@st.cache_resource
def load_model():
    """Lazily loads the Blenderbot model/tokenizer. Only called when the Chatbot
    page is actually opened -- this used to run at import time (`model, tokenizer =
    load_model()` at module scope), which crashed the *entire app* on startup
    whenever the model weights weren't installed (only merges.txt ships in this
    repo -- see model_install.py), not just this one page.
    """
    from transformers import BlenderbotSmallForConditionalGeneration, BlenderbotSmallTokenizer
    import torch

    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_directory = "models/model_blenderbot"
    tokenizer = BlenderbotSmallTokenizer.from_pretrained(model_directory)
    model = BlenderbotSmallForConditionalGeneration.from_pretrained(model_directory)
    model.to(device)
    return model, tokenizer, device


def generate_response(model, tokenizer, device, prompt: str) -> str:
    inputs = tokenizer(prompt, return_tensors="pt").to(device)
    reply_ids = model.generate(**inputs)
    return tokenizer.batch_decode(reply_ids, skip_special_tokens=True)[0]


def chatbot_page():
    st.title("💬 Personal Assistant Chatbot (Offline + CUDA)")

    try:
        model, tokenizer, device = load_model()
    except Exception as e:
        st.error(
            "⚠️ Chatbot is unavailable — the Blenderbot model weights aren't installed "
            "(only the tokenizer files ship in this repo). Run `model_install.py` or download "
            "`facebook/blenderbot-3B` into `models/model_blenderbot`. The rest of the app works "
            "fine without this."
        )
        st.caption(f"Details: {e}")
        return

    if "chat_messages" not in st.session_state:
        st.session_state.chat_messages = []

    for message in st.session_state.chat_messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("What is up?"):
        st.session_state.chat_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        response = generate_response(model, tokenizer, device, prompt)
        with st.chat_message("assistant"):
            st.markdown(response)

        st.session_state.chat_messages.append({"role": "assistant", "content": response})
