import pandas as pd

def tokenize_protein(seq:str, vocab, max_seq_len):
    tokens = [char for char in seq]
    tokens += [vocab[0]] * (max_seq_len - len(tokens))
    tokens.insert(0,vocab[1])
    tokens.append(vocab[2])
    ids = []
    for token in tokens:
        ids.append(vocab.index(token))
    return pd.Series([tokens, ids])

