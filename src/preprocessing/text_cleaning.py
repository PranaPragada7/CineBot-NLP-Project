def remove_punctuation(text):
    import string

    return text.translate(str.maketrans("", "", string.punctuation))


def lowercase_text(text):
    return text.lower()


def remove_stopwords(text, stopwords):
    return " ".join([word for word in text.split() if word not in stopwords])
