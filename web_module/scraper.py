from selenium.webdriver import Remote, FirefoxOptions
from selenium import webdriver
from selenium.webdriver.firefox.service import Service  # Importation du service pour Firefox
from bs4 import BeautifulSoup
from parse import parse_with_ollama
import os

def scrape_website(website):
    print("Launching Firefox browser...")

    firefox_driver_path = "geckodriver"  # Spécifiez ici le chemin vers GeckoDriver pour Firefox
    options = webdriver.FirefoxOptions()

    # Lancer Firefox avec le service GeckoDriver
    driver = webdriver.Firefox(service=Service(firefox_driver_path), options=options)

    try:
        driver.get(website)  # Ouvrir l'URL spécifiée
        print("Page loaded...")
        html = driver.page_source  # Récupérer le code source de la page
        with open("html_page_source.txt", 'w') as file:
            file.write(html)
            print("Page HTML brute enrgistrée (html_page_source.txt)")
        return html
    finally:
        driver.quit()  # Fermer le navigateur une fois terminé


def extract_body_content(html_content):
    soup = BeautifulSoup(html_content, "html.parser")
    body_content = soup.body
    if body_content:
        return str(body_content)
    return ""


def clean_body_content(body_content):
    soup = BeautifulSoup(body_content, "html.parser")

    for script_or_style in soup(["script", "style"]):
        script_or_style.extract()

    # Get text or further process the content
    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    with open("cleaned_content.txt", "w") as file:
        file.write(cleaned_content)
        print("Page HTML nettoyée enregistrée (cleaned_content.txt)")

    return cleaned_content


def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i : i + max_length] for i in range(0, len(dom_content), max_length)
    ]

if __name__ == "__main__":
    # Scrape the website
    url = "https://example.com"
    dom_content = scrape_website(url)
    body_content = extract_body_content(dom_content)
    cleaned_content = clean_body_content(body_content)

    dom_chunks = split_dom_content(cleaned_content)
    parse_description = "Quel est le sujet de la page ?"
    print(f"Question pour le LLM: {parse_description}")

    parsed_result = parse_with_ollama(dom_chunks, parse_description, store_interaction=True)
    print("LLM interaction store in txt file.")
    print(parsed_result)