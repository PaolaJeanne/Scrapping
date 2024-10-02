import requests
from bs4 import BeautifulSoup
import json
import csv
import os
from urllib.parse import urljoin

def extract_category_names_and_urls(url):


    response = requests.get(url)
    html_content = response.text

    soup = BeautifulSoup(html_content, 'html.parser')

    category_list = soup.find('ul', class_='nav nav-list')

    category_links = category_list.find_all('li')

    categories = []
    for link in category_links:
        a_tag = link.find('a')
        if a_tag:
            category_url = 'https://books.toscrape.com/' + a_tag['href']
            category_name = a_tag.get_text(strip=True)  # Get the category name
            if(category_name != 'Books'):
                categories.append((category_name, category_url))  # Store as a tuple

    return categories

def extract_category_page_urls(url):

    page_urls = [url]  # initialisation de l'url de la page index

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
                # Use urljoin to construct the absolute URL
                full_url = urljoin(url, href_url)
                href_urls.append(full_url)

    return href_urls

def get_book_details(book_url, category_name):
    response = requests.get(book_url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    details = {}
    details['Category'] = category_name

    title_tag = soup.select_one('div.col-sm-6.product_main h1')
    details['Title'] = title_tag.get_text(strip=True) if title_tag else 'N/A'

    title_tag = soup.select_one('div.col-sm-6.product_main h1')
    details['Title'] = title_tag.get_text(strip=True) if title_tag else 'N/A'

    price_tag = soup.select_one('p.price_color')
    if price_tag:
        raw_price = price_tag.get_text(strip=True)
        details['Price'] = raw_price.lstrip('£')  # Remove the pound sign
    else:
        details['Price'] = 'N/A'

    stock_tag = soup.select_one('p.instock.availability')
    details['Stock Availability'] = stock_tag.get_text(strip=True) if stock_tag else 'N/A'

    rate_tag = soup.select_one('p.star-rating')
    details['Rate'] = rate_tag['class'][1] if rate_tag and len(rate_tag['class']) > 1 else 'N/A'

    description_tag = soup.select_one('div#product_description + p')
    details['Description'] = description_tag.get_text(strip=True) if description_tag else 'N/A'

    img_tag = soup.select_one('div.item.active img')
    img_src = img_tag['src'] if img_tag else None
    details['Image File'] = None

    if img_src:
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

    
    csv_data = [
        details['Category'],
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
    file_exists = os.path.isfile(filename)
    
    # Debugging: print the data being written to CSV
    # print(f"Writing to CSV: {data}")  # Debugging line
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow([
                "Category",
                "Title", "Price", "Stock Availability", "Rate", 
                "Description", "P.I. - UPC", "P.I. - Product Type", 
                "P.I. - Price (excl. tax)", "P.I. - Price (incl. tax)", 
                "P.I. - Tax", "P.I. - Availability", "P.I. - Number of reviews"
            ])
        
        writer.writerow(data)


url = 'https://books.toscrape.com/index.html'
categories = extract_category_names_and_urls(url)

csv_file = 'categories.csv'

with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Category Name', 'Category URL'])

    for name, url in categories:
        writer.writerow([name, url])

# extraction des 3 premieres categories 
# first_five_categories = categories[:1]      
for name, url in categories:
    current_category_pages = extract_category_page_urls(url)
    for page in current_category_pages:
        book_pages = extract_book_urls_from_a_page(page) 
        for book_page in book_pages:
            book_details = get_book_details(book_page, name)
            save_to_csv(book_details)