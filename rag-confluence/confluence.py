from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
import time
from utils import *
import requests
import argparse

driver = webdriver.Chrome()


def login():
    url = f"{get_property("confluence")}/wiki/login.action"
    username = get_property("user")
    password = get_property("psswd")
    driver.get(url)
    driver.find_element(By.ID, "os_username").send_keys(username)
    driver.find_element(By.ID, "os_password").send_keys(password)
    driver.find_element(By.ID, "os_password").send_keys(Keys.RETURN)
    time.sleep(5)


def get_childs(page_id):
    confluenceBaseUrl = get_property("confluence")
    pageId = page_id
    username = get_property("user")
    password = get_property("psswd")
    children_url = '{confluenceBaseUrl}/rest/api/content/search?cql=parent={pageId}'.format(
        confluenceBaseUrl=confluenceBaseUrl, pageId=pageId)
    reponse_childs = requests.get(
        children_url, auth=(
            username, password)).json()
    children_ids = []
    if 'results' in reponse_childs:
        for item in reponse_childs['results']:
            print('ParentId: {parent_id}, ChildId:{page_id}, Tittle: {tittle}'.format(
                parent_id=pageId, page_id=item["id"], tittle=item["title"]))
            children_ids.append(item["id"])
    else:
        print("La clave 'results' no se encuentra en los datos.")
    return children_ids


def get_all_childs(page_id):
    all_childs = []

    def fetch_childs(parent_id):
        childs = get_childs(parent_id)
        for child in childs:
            all_childs.append({
                "parent": parent_id,
                "child": child
            })
            fetch_childs(child)
    fetch_childs(page_id)
    return all_childs


def getContent(page_id, parent_id=None):
    print("Getting info from", page_id)
    driver.get(f"{get_property("confluence")}/pages/viewpage.action?pageId={page_id}")
    page_html = driver.page_source
    if parent_id is None:
        links = get_links(page_html)
    else:
        links = get_links(page_html) + f'\n{{"parent": {parent_id}}}'
    write_file(page_html, f"output/{page_id}/content.html")
    write_file(links, f"output/{page_id}/links.txt")


def get_pages(parent):
    login()
    pages = get_all_childs(parent)
    getContent(page_id=parent)
    for page in pages:
        getContent(page_id=page["child"], parent_id=page["parent"])
    driver.quit()


def main(page_id):
    get_pages(page_id)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Get information from Confluence given a page_id.")
    parser.add_argument('page_id', nargs='?', help='Page ID from Confluence.')
    args = parser.parse_args()
    main(args.page_id)
