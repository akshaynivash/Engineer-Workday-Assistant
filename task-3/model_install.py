"""Downloads the model weights the app expects locally, into models/.

Only tokenizer files ship in this repo (models/model_blenderbot/merges.txt,
models/phi-1.5/merges.txt) -- run this once to get the actual weights.
"""

from transformers import (
    AutoModelForCausalLM,
    AutoTokenizer,
    BlenderbotSmallForConditionalGeneration,
    BlenderbotSmallTokenizer,
)

# chatbot.py loads this with BlenderbotSmallTokenizer/BlenderbotSmallForConditionalGeneration --
# those classes are for the "small" variant specifically. "facebook/blenderbot-3B" (the large
# model, mentioned in the original README) uses a different class entirely (BlenderbotTokenizer/
# BlenderbotForConditionalGeneration, no "Small") and would not load correctly here.
BLENDERBOT_MODEL = "facebook/blenderbot_small-90M"
BLENDERBOT_DIR = "models/model_blenderbot"

PHI_MODEL = "microsoft/phi-1_5"
PHI_DIR = "models/phi-1.5"


def download_blenderbot():
    tokenizer = BlenderbotSmallTokenizer.from_pretrained(BLENDERBOT_MODEL)
    model = BlenderbotSmallForConditionalGeneration.from_pretrained(BLENDERBOT_MODEL)
    tokenizer.save_pretrained(BLENDERBOT_DIR)
    model.save_pretrained(BLENDERBOT_DIR)
    print(f"Blenderbot saved to {BLENDERBOT_DIR}")


def download_phi():
    tokenizer = AutoTokenizer.from_pretrained(PHI_MODEL)
    model = AutoModelForCausalLM.from_pretrained(PHI_MODEL)
    tokenizer.save_pretrained(PHI_DIR)
    model.save_pretrained(PHI_DIR)
    print(f"Phi-1.5 saved to {PHI_DIR}")


if __name__ == "__main__":
    download_blenderbot()
    download_phi()
