import requests
from bs4 import BeautifulSoup

def extract_category_page_urls(url):

    page_urls = [url]  

    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    pagination_element = soup.find('li', class_='current')

    if pagination_element:
        page_text = pagination_element.text.strip()
        total_pages = int(page_text.split()[-1]) 

        for page_number in range(2, total_pages + 1):
            page_url = url.replace('index.html', f'page-{page_number}.html')
            page_urls.append(page_url)

    return page_urls

category_url = 'https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html'  # Replace with your actual category URL
all_page_urls = extract_category_page_urls(category_url)

for url in all_page_urls:
    print(url)