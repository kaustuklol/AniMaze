def refresh(text):
    return text.replace(":", "").replace("/", "").replace("!", "").replace("*", "").replace("'", "").replace("-", "").replace("é", "e").replace(",", "").replace(";", "").replace("|", "").replace(".", "").replace("’", "").replace("?", "").replace("[", "").replace("]", "").replace('"', '').lower()
