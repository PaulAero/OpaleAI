import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import time
from selenium import webdriver
from selenium.webdriver.firefox.service import Service
from web_module.parse_for_RAG import parse_for_RAG_with_ollama
import tldextract
import os
import re

from RAG_module.Process_documents.process_document import process_and_store_documents, get_path

visited_urls = set()

def scrape_arborescence_website(url, max_depth=2, current_depth=0, starting_netloc=None):
    if current_depth > max_depth:
        return

    if url in visited_urls:
        return

    if starting_netloc is None:
        starting_netloc = urlparse(url).netloc

    try:
        # Add the URL to the visited set
        visited_urls.add(url)

        # Use Selenium to get the dynamic HTML content
        html_content = scrape_with_selenium(url)

        if not html_content:
            return  # If no page could be loaded

        # Extract the body content
        body_content = extract_body_content(html_content)

        # Clean the content
        cleaned_content = clean_body_content(body_content)

        # Split the content
        split_content = split_dom_content(cleaned_content)

        llm_summary = parse_for_RAG_with_ollama(split_content)
        print(f"Content from {url} (Depth: {current_depth}) answer of the LLM:")
        print(llm_summary)

        save_path = get_path("Documents/")
        save_url = re.sub(r'[\/:*?"<>|]', '_', url)
        save_name = f"[{save_url}][depth{current_depth}].txt"
        file_path = save_path / save_name
        print(file_path)

        with file_path.open("w") as file:
            file.write(url)
            file.write('\n')
            file.write(llm_summary)
            print("Page analysis completed")

        try:
            process_and_store_documents(str(save_path), save_name, url)
        except Exception as e:
            print(f"Error during vectorization of {url}")
            print(e)

        time.sleep(1)  # Delay to avoid overloading the server

        # Parse the HTML and continue the recursive scraping
        soup = BeautifulSoup(html_content, 'html.parser')
        links = set(a['href'] for a in soup.find_all('a', href=True))
        for link in links:
            abs_link = urljoin(url, link)
            abs_netloc = urlparse(abs_link).netloc
            if abs_netloc == starting_netloc and abs_link not in visited_urls:
                print(f"Following URL: {abs_link}")
                scrape_arborescence_website(abs_link, max_depth, current_depth + 1, starting_netloc)

    except requests.RequestException as e:
        print(f"Failed to request {url}: {e}")

def scrape_with_selenium(website):
    print(f"Launching Firefox browser for {website}...")

    firefox_driver_path = "geckodriver"  # Specify the path to GeckoDriver here
    options = webdriver.FirefoxOptions()
    options.headless = True  # Run the browser in headless mode

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
    extracted = tldextract.extract(url)
    domain_name = f"{extracted.domain}.{extracted.suffix}"
    return domain_name

if __name__ == "__main__":
    # Start the recursive scraping
    starting_url = "https://gestionnaires.actifforum.com/f26-ople"
    scrape_arborescence_website(starting_url, max_depth=2)
