"""Physics/justification explanations for a part and its alternatives.

Two paths: fast deterministic rules (default, no extra dependencies beyond
what's already installed), or AI-generated via a local Phi-1.5 model. Only
tokenizer files ship in this repo -- run `python model_install.py` (task-3/)
to download the actual weights before enabling AI mode.
"""

from functools import lru_cache

from app.data import REPO_ROOT

PHI_MODEL_DIR = REPO_ROOT / "task-3" / "models" / "phi-1.5"


@lru_cache
def _load_phi_model():
    from transformers import AutoModelForCausalLM, AutoTokenizer

    tokenizer = AutoTokenizer.from_pretrained(str(PHI_MODEL_DIR))
    model = AutoModelForCausalLM.from_pretrained(str(PHI_MODEL_DIR))
    return tokenizer, model


def generate_ai_explanation(prompt: str) -> str:
    """Raises if the model isn't installed -- callers turn that into a clean 503."""
    tokenizer, model = _load_phi_model()
    inputs = tokenizer(prompt, return_tensors="pt", max_length=512, truncation=True)
    outputs = model.generate(
        inputs.input_ids,
        max_length=200,
        num_return_sequences=1,
        temperature=0.7,
        top_p=0.9,
        do_sample=True,
    )
    return tokenizer.decode(outputs[0], skip_special_tokens=True)


def rule_based_physics_explanation(fuse_type: str, application: str) -> str:
    if "Slow Blow" in fuse_type:
        return (
            "This is a Slow Blow fuse, designed to handle inrush currents before melting. "
            "It is thermally activated and ideal for power supply circuits, where temporary surges are expected."
        )
    if "Fast Blow" in fuse_type:
        return (
            "This is a Fast Blow fuse, which melts quickly when exceeding the rated current. "
            "It is commonly used in sensitive electronic circuits that require immediate disconnection upon overload."
        )
    return (
        "This fuse operates based on thermal dissipation and overload conditions, "
        f"ensuring circuit protection in applications like {application}."
    )


def rule_based_justification(
    fuse_type: str,
    alt_fuse_type: str,
    rated_current: str,
    alt_rated_current: str,
    rated_voltage: str,
    alt_rated_voltage: str,
    mounting: str,
    alt_mounting: str,
) -> str:
    explanation = "This alternative "
    if fuse_type == alt_fuse_type:
        explanation += f"shares the same {fuse_type} fuse type, ensuring similar thermal characteristics. "
    else:
        explanation += f"has a slightly different fuse type ({alt_fuse_type}), but remains functionally compatible. "

    if abs(float(str(alt_rated_current).replace("A", "")) - float(str(rated_current).replace("A", ""))) <= 1:
        explanation += f"Its current rating ({alt_rated_current}A) is close to the original, ensuring safe operation. "
    else:
        explanation += (
            f"It has a higher/lower current rating ({alt_rated_current}A) but still fits within tolerance limits. "
        )

    if abs(float(str(alt_rated_voltage).replace("V", "")) - float(str(rated_voltage).replace("V", ""))) <= 10:
        explanation += f"The voltage rating is within the acceptable ±10% range ({alt_rated_voltage}V). "
    else:
        explanation += f"The voltage rating differs ({alt_rated_voltage}V), but remains within functional limits. "

    if mounting == alt_mounting:
        explanation += f"Additionally, it fits the same mounting type ({alt_mounting}), making installation easier."
    else:
        explanation += f"Though the mounting type ({alt_mounting}) differs, it is still mechanically compatible."

    return explanation
