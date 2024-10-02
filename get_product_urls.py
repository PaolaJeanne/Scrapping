import requests
from bs4 import BeautifulSoup

# definition d'une fonction qui recupere les urls des livres d'une page
def extract_book_urls_from_a_page(url): 
    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')
    href_urls = []

    product_pods = soup.find_all('article', class_='product_pod')

    for product_pod in product_pods:
        h3_tag = product_pod.find('h3')
        if h3_tag:
            a_tag = h3_tag.find('a')
            if a_tag:
                href_url = a_tag['href']
                href_urls.append(href_url)

    return href_urls

url = 'https://books.toscrape.com/index.html'
href_urls = extract_book_urls_from_a_page(url)

for url in href_urls:
    print(url)