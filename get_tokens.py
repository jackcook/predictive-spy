# Read binary data from sp.dat
data = open(
    "/System/Library/LinguisticData/RequiredAssets_en.bundle/AssetData/en.lm/unilm.bundle/sp.dat",
    "rb",
).read()

# Find the <pad> token, which is the first token in the vocab
first_token_offset = data.find(b"<pad>", data.find(b"<pad>") + 1)

if first_token_offset == -1:
    raise Exception(
        "Could not find <pad> token. You may need to update to macOS Sonoma."
    )

# Parse the tokens
tokens = []
current_token = b""

for byte in range(first_token_offset, len(data)):
    # Tokens are split by null bytes
    if data[byte] == 0:
        tokens.append(current_token.decode("utf-8"))
        current_token = b""

        if len(tokens) == 15000:
            break
    else:
        current_token += bytes([data[byte]])

# Write all tokens to vocab.txt
with open("vocab.txt", "w") as f:
    for i, token in enumerate(tokens):
        f.write(token)

        if i != len(tokens) - 1:
            f.write("\n")
