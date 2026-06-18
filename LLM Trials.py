from transformers import AutoTokenizer

tokenizer = AutoTokenizer.from_pretrained("unsloth/Llama-3.2-1B")

text = "This is a test. The first of many, and not the only."

token_ids = tokenizer.encode(text)
print("Token IDs:", token_ids)

tokens = tokenizer.convert_ids_to_tokens(token_ids)
print("Tokens:", tokens)

for tid, tok in zip(token_ids, tokens):
    print(f"{tid:>8}  {tok}")