import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from parse_for_RAG import parse_for_RAG_with_ollama
import tldextract

from RAG_module.Process_documents.process_document import process_and_store_documents, get_path

visited_urls = set()


def scrape_website(url, max_depth=2, current_depth=0):
    if current_depth > max_depth:
        return

    if url in visited_urls:
        return

    try:
        # Utilise Selenium pour récupérer le contenu HTML dynamique
        html_content = scrape_with_selenium(url)

        if not html_content:
            return  # Si aucune page n'a pu être chargée

        # Extraire le contenu du body
        body_content = extract_body_content(html_content)

        # Nettoyer le contenu
        cleaned_content = clean_body_content(body_content)

        # Découper le contenu
        split_content = split_dom_content(cleaned_content)

        llm_summary = parse_for_RAG_with_ollama(split_content) # ajouter l'enregistrement
        print(f"Content from {url} (Depth: {current_depth}) answer of the LLM:")
        print(llm_summary)  # Limite l'affichage à 500 caractères pour chaque partie

        main_url = get_site_name(url)
        save_path = get_path("Documents/")
        save_name = f"[{main_url}][depth{current_depth}].txt"
        file_path = save_path / save_name
        print(file_path)

        with file_path.open("w") as file:
            file.write(url)
            file.write(llm_summary)
            print("Analyse de la page terminée")
        try:
            process_and_store_documents(str(save_path), save_name, url) # note: on aurait pu vectoriser direct
        except Exception as e:
            print(f"Erreur lors de la vectorisation de {url}")
            print(e)

        time.sleep(1)  # Délai pour éviter la surcharge du serveur

        # Parse l'HTML et continue le scraping récursif
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set(a['href'] for a in soup.find_all('a', href=True))
        for link in links:
            abs_link = urljoin(url, link)
            if abs_link.startswith(url):
                scrape_website(abs_link, max_depth, current_depth + 1)

    except requests.RequestException as e:
        print(f"Failed to request {url}: {e}")


def scrape_with_selenium(website):
    print(f"Launching Firefox browser for {website}...")

    firefox_driver_path = "geckodriver"  # Spécifiez ici le chemin vers GeckoDriver
    options = webdriver.FirefoxOptions()
    options.headless = True  # Lance le navigateur en mode "headless" (sans interface graphique)

    driver = webdriver.Firefox(service=Service(firefox_driver_path), options=options)

    try:
        driver.get(website)
        print("Page loaded...")
        html = driver.page_source
        return html
    finally:
        driver.quit()


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

    cleaned_content = soup.get_text(separator="\n")
    cleaned_content = "\n".join(
        line.strip() for line in cleaned_content.splitlines() if line.strip()
    )

    return cleaned_content


def split_dom_content(dom_content, max_length=6000):
    return [
        dom_content[i: i + max_length] for i in range(0, len(dom_content), max_length)
    ]


def get_site_name(url):
    # Utiliser tldextract pour extraire le domaine principal
    extracted = tldextract.extract(url)
    # Le domaine complet est `domaine + suffixe` (par exemple, chatgpt.com)
    domain_name = f"{extracted.domain}.{extracted.suffix}"
    return domain_name

if __name__ == "__main__":
    # Démarrer le scraping récursif
    starting_url = "https://example.com"
    scrape_website(starting_url, max_depth=2)
