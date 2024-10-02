import requests
from bs4 import BeautifulSoup
import csv
import os

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
            category_name = a_tag.get_text(strip=True)  
            categories.append((category_name, category_url)) 

    return categories

url = 'https://books.toscrape.com/index.html'
categories = extract_category_names_and_urls(url)

csv_file = 'categories.csv'

with open(csv_file, mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Category Name', 'Category URL'])
    

    for name, url in categories:
        writer.writerow([name, url])

for name, url in categories:
    print(f'Category: {name}, URL: {url}')