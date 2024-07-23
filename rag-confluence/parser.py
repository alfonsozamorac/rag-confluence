from bs4 import BeautifulSoup
from langchain_core.documents import Document
from utils import get_directories
import ollama
import re
from langchain.text_splitter import TokenTextSplitter
from utils import write_file
import os


def clean_text(text):
    CLEANR_V2 = re.compile('<.*?>|&([a-z0-9]+|#[0-9]{1,6}|#x[0-9a-f]{1,6});')
    clean_content = re.sub(CLEANR_V2, '', text)
    clean_content = re.sub(r'[%"\xa0]', '', clean_content)
    clean_content = re.sub(r'[%"\xa0]', '', clean_content)
    clean_content = re.sub(r'true\w+', '', clean_content)
    clean_content = re.sub(r'→', '', clean_content)
    clean_content = re.sub(r'\s+', ' ', clean_content)
    clean_content = re.sub(r'^\d+\s*\d*\s*', '', clean_content)
    clean_content = re.sub(r'\\u00e1', 'á', clean_content)
    clean_content = re.sub(r'\\u00e9', 'é', clean_content)
    clean_content = re.sub(r'\\u00ed', 'í', clean_content)
    clean_content = re.sub(r'\\u00f3', 'ó', clean_content)
    clean_content = re.sub(r'\\u00fa', 'ú', clean_content)
    clean_content = clean_content.replace(
        '\\u00a0',
        ' ').replace(
        '\\u00bf',
        '¿').replace(
            '\\u2192',
        '->').strip()
    return clean_content


def create_docs(file):
    soup = BeautifulSoup(
        open(
            f"{file}/content.html",
            "r").read(),
        features="html.parser")
    file_translated = f"{file}/translated.txt"
    translated = ""
    page_id = file.split("/")[2]
    if os.path.exists(file_translated):
        with open(file_translated, 'r') as file:
            translated = file.read()
    else:
        for span in soup.find_all('span'):
            span.insert_before(' ')
            span.insert_after(' ')
        cleaned_content = soup.find(id='main-content').text
        cleaned_content = clean_text(cleaned_content)
        response = ollama.chat(
            model='llama3:8b',
            messages=[
                {
                    'role': 'user',
                    'content': f"""Translate from Spanish to English the following: Start: '''{
                        soup.title.text}\n{cleaned_content}'''.
            Provide only the translation without introduction and maintain the original structure of the text, do not put something
            like 'Here is the translation:' it is not required""",
                },
            ])
        translated = f"{response['message']['content']}"
        write_file(translated, f"output/{page_id}/translated.txt")
    doc_eng = Document(
        page_content=translated,
        metadata={
            "source": soup.title.text,
            "page_id": page_id})
    return [doc_eng]


def get_chunks():
    directories = get_directories("./output")
    docs = []
    total = len(directories)
    for file in directories:
        print("Documents left:", total)
        total = total - 1
        docs.extend(create_docs(file))
    text_splitter = TokenTextSplitter(chunk_size=512, chunk_overlap=24)
    chunks = text_splitter.split_documents(docs)
    return chunks
