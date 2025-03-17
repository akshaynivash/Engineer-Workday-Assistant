# from transformers import BlenderbotSmallTokenizer, BlenderbotSmallForConditionalGeneration

# # Specify the model name
# model_name = "facebook/blenderbot_small-90M"

# # Download and save the tokenizer and model locally
# tokenizer = BlenderbotSmallTokenizer.from_pretrained(model_name)
# model = BlenderbotSmallForConditionalGeneration.from_pretrained(model_name)

# # Save the model and tokenizer to a local directory
# save_directory = "model"
# tokenizer.save_pretrained(save_directory)
# model.save_pretrained(save_directory)

# print(f"Model and tokenizer saved to {save_directory}")


from transformers import AutoTokenizer, AutoModelForCausalLM

# Specify the Phi-1.5 model
model_name = "microsoft/phi-1_5"

# Download and cache the model and tokenizer
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForCausalLM.from_pretrained(model_name)

# Save the model and tokenizer to a local directory (optional)
save_directory = "models/phi-1.5"
tokenizer.save_pretrained(save_directory)
model.save_pretrained(save_directory)

print(f"Model and tokenizer saved to {save_directory}")

