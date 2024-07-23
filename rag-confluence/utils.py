from bs4 import BeautifulSoup
from dotenv import load_dotenv
from pathlib import Path
import re
import re
import os
import json


def get_property(key):
    secrets_path = os.path.join(os.path.dirname(__file__), '.secrets')
    load_dotenv(secrets_path)
    value = os.getenv(key)
    return value


def write_file(text, file):
    Path(file).parent.mkdir(parents=True, exist_ok=True)
    with open(file, 'w') as f:
        f.write(text.strip())


def get_links(html):
    soup = BeautifulSoup(html, 'html.parser')
    external_links = soup.find_all('a', href=re.compile(r'http[s]?://'))
    links = []
    for link in external_links:
        link_data = {
            "ref": link['href'],
            "text": link.get_text(strip=True)
        }
        links.append(json.dumps(link_data))
    return "\n".join(links)


def get_directories(root_dir):
    directories = []
    with os.scandir(root_dir) as entries:
        for entry in entries:
            if entry.is_dir():
                directories.append(entry.path)
    return directories
