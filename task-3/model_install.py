"""Downloads the model weights the app expects locally, into models/.

Only tokenizer files ship in this repo (models/phi-1.5/merges.txt) -- run
this once to get the actual weights. Quick Chat no longer needs a local
download here -- it talks to a locally running Ollama instead (see
backend/app/services/chatbot.py, `ollama pull <model>`).
"""

from transformers import AutoModelForCausalLM, AutoTokenizer

PHI_MODEL = "microsoft/phi-1_5"
PHI_DIR = "models/phi-1.5"


def download_phi():
    tokenizer = AutoTokenizer.from_pretrained(PHI_MODEL)
    model = AutoModelForCausalLM.from_pretrained(PHI_MODEL)
    tokenizer.save_pretrained(PHI_DIR)
    model.save_pretrained(PHI_DIR)
    print(f"Phi-1.5 saved to {PHI_DIR}")


if __name__ == "__main__":
    download_phi()
