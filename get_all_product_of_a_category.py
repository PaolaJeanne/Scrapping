import requests
from bs4 import BeautifulSoup
import json
import csv
import os
from urllib.parse import urljoin

def extract_category_urls(url):

    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    category_list = soup.find('ul', class_='nav nav-list')

    category_links = category_list.find_all('li')

    category_urls = []
    for link in category_links:
        a_tag = link.find('a')
        if a_tag:
            category_url = a_tag['href']
            category_urls.append(category_url)

    return category_urls

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
                full_url = urljoin(url, href_url)
                href_urls.append(full_url)

    return href_urls

def get_book_details(book_url):
    response = requests.get(book_url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract book details
    details = {}

    # Titre
    title_tag = soup.select_one('div.col-sm-6.product_main h1')
    details['Title'] = title_tag.get_text(strip=True) if title_tag else 'N/A'

    # Prix
    price_tag = soup.select_one('p.price_color')
    details['Price'] = price_tag.get_text(strip=True) if price_tag else 'N/A'

    # Stocke disponible
    stock_tag = soup.select_one('p.instock.availability')
    details['Stock Availability'] = stock_tag.get_text(strip=True) if stock_tag else 'N/A'

    # Rate
    rate_tag = soup.select_one('p.star-rating')
    details['Rate'] = rate_tag['class'][1] if rate_tag and len(rate_tag['class']) > 1 else 'N/A'

    # Description
    description_tag = soup.select_one('div#product_description + p')
    details['Description'] = description_tag.get_text(strip=True) if description_tag else 'N/A'

    # Image
    img_tag = soup.select_one('div.item.active img')
    img_src = img_tag['src'] if img_tag else None
    details['Image File'] = None

    if img_src:
        # telechargement et sauvgarde d'image
        image_folder = 'images'
        if not os.path.exists(image_folder):
            os.makedirs(image_folder)

        image_file_name = os.path.basename(img_src)
        image_file_path = os.path.join(image_folder, image_file_name)

        img_response = requests.get(urljoin(book_url, img_src))
        if img_response.status_code == 200:
            with open(image_file_path, 'wb') as img_file:
                img_file.write(img_response.content)
            details['Image File'] = image_file_path

    # Information 
    product_info_table = soup.select_one('table.table.table-striped')
    product_info = {}
    
    if product_info_table:
        rows = product_info_table.find_all('tr')
        for row in rows:
            th = row.find('th')
            td = row.find('td')
            if th and td:
                key = th.get_text(strip=True)
                value = td.get_text(strip=True)
                product_info[key] = value

    details['Product Information'] = product_info

    # Prepare data for CSV
    csv_data = [
        details['Title'],
        details['Price'],
        details['Stock Availability'],
        details['Rate'],
        details['Description'],
        details['Image File'] if details['Image File'] else '',
        product_info.get('UPC', 'N/A'),
        product_info.get('Product Type', 'N/A'),
        product_info.get('Price (excl. tax)', 'N/A'),
        product_info.get('Price (incl. tax)', 'N/A'),
        product_info.get('Tax', 'N/A'),
        product_info.get('Availability', 'N/A'),
        product_info.get('Number of reviews', 'N/A')
    ]
    
    return csv_data

def save_to_csv(data, filename='books_scraped.csv'):
    # Check if the file exists
    file_exists = os.path.isfile(filename)
    
    # Open the CSV file in append mode
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        # Write the header if the file did not exist
        if not file_exists:
            writer.writerow([
                "Title", "Price", "Stock Availability", "Rate", 
                "Description", "P.I. - UPC", "P.I. - Product Type", 
                "P.I. - Price (excl. tax)", "P.I. - Price (incl. tax)", 
                "P.I. - Tax", "P.I. - Availability", "P.I. - Number of reviews"
            ])
        
        # Write the data
        writer.writerow(data)


category_url = 'https://books.toscrape.com/catalogue/category/books/historical-fiction_4/index.html'  # Replace with your actual category URL
all_page_urls = extract_category_page_urls(category_url)

for page in all_page_urls:
    book_urls = extract_book_urls_from_a_page(page)
    print(f'Book URLs on page {page}:')
    for book_url in book_urls:
        book_details = get_book_details(book_url)
        print(book_url)

        # Save details to CSV if they were successfully retrieved
        if book_details:
            save_to_csv(book_details)