def preprocess_aa_sequence(sequence, tokenizer, masker=None, labels=None):
    inputs = tokenizer(sequence)
    if masker:
        outputs = masker(inputs)
        features = {
            "token_ids": outputs["token_ids"],
            "mask_positions": outputs["mask_positions"],
        }
        labels = outputs["mask_ids"]
        weights = outputs["mask_weights"]
        return features, labels, weights
    elif labels:
        return tokenizer(sequence), labels
    else:
        return tokenizer(sequence)

def standardize_data(data,mean,std):
    return (data-mean)/std

def destandardize_data(data,mean,std):
    return data*std+mean
