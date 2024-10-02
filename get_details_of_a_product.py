import requests
from bs4 import BeautifulSoup
import json
import csv
import os

def get_book_details(book_url):
    response = requests.get(book_url)
    
    if response.status_code != 200:
        print(f"Failed to retrieve the page. Status code: {response.status_code}")
        return None

    soup = BeautifulSoup(response.content, 'html.parser')

    details = {}

    # Titre 
    title_tag = soup.select_one('div.col-sm-6.product_main h1')
    details['Title'] = title_tag.get_text(strip=True) if title_tag else 'N/A'

    # Prix
    price_tag = soup.select_one('p.price_color')
    details['Price'] = price_tag.get_text(strip=True) if price_tag else 'N/A'

    # Stocke
    stock_tag = soup.select_one('p.instock.availability')
    details['Stock Availability'] = stock_tag.get_text(strip=True) if stock_tag else 'N/A'

    # Rate
    rate_tag = soup.select_one('p.star-rating')
    details['Rate'] = rate_tag['class'][1] if rate_tag and len(rate_tag['class']) > 1 else 'N/A'

    # Description
    description_tag = soup.select_one('div#product_description + p')
    details['Description'] = description_tag.get_text(strip=True) if description_tag else 'N/A'

    # Information sur les produits
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
        details['Title'],
        details['Price'],
        details['Stock Availability'],
        details['Rate'],
        details['Description'],
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
    
    with open(filename, mode='a', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        
        if not file_exists:
            writer.writerow([
                "Title", "Price", "Stock Availability", "Rate", 
                "Description", "P.I. - UPC", "P.I. - Product Type", 
                "P.I. - Price (excl. tax)", "P.I. - Price (incl. tax)", 
                "P.I. - Tax", "P.I. - Availability", "P.I. - Number of reviews"
            ])
        
        writer.writerow(data)

book_url = 'https://books.toscrape.com/catalogue/a-paris-apartment_612/index.html'
book_details = get_book_details(book_url)

if book_details:
    save_to_csv(book_details)

print("Book details have been saved to books_scraped.csv")