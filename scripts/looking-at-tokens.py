import os
import sys 
from rich.panel import Panel
from rich import print as rprint

from transformers import AutoTokenizer, AutoModelForCausalLM

prompt = "Who are you?"

tokenizer = AutoTokenizer.from_pretrained("Qwen/Qwen3-8B")
model = AutoModelForCausalLM.from_pretrained("Qwen/Qwen3-8B")
messages = [
    {"role": "user", "content": prompt},
]
inputs = tokenizer.apply_chat_template(
	messages,
	add_generation_prompt=True,
	tokenize=True,
	return_dict=True,
	return_tensors="pt",
).to(model.device)

print(f"Prompt: {prompt}")
print(f"Input Dictionary -- after chat-template applied")
for k,v in inputs.items(): 
    print(f"{k} --> {v}")
print(f"Decoded Input: {tokenizer.decode(inputs.input_ids[0])}")

outputs = model.generate(**inputs, max_new_tokens=40)
print(tokenizer.decode(outputs[0][inputs["input_ids"].shape[-1]:]))
