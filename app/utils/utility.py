import re

def handle_title(full_text: str) -> str:
    full_text = re.sub(r'(https?|ftp|file)://[-A-Za-z0-9+&@#/%?=~_|!:,.;]+[-A-Za-z0-9+&@#/%=~_|]', '', full_text)
    full_text = re.sub(r'@\S+\s', '', full_text)
    full_text = re.sub(r'\r|\n\r?', ' ', full_text)
    full_text = re.sub(r'[/\\:*?"<>\|]', '', full_text)
    return full_text.strip()