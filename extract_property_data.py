# extract data from property urls
import requests
from bs4 import BeautifulSoup
import csv

def extract_owner_info(soup, owner_type):
    owner_div = soup.find('div', string=lambda text: text and owner_type in text)
    if owner_div:
        owner_info = ' '.join([div.text.strip() for div in owner_div.find_next_siblings('div') if div.text.strip()])
        return owner_info
    return ''

def extract_address(soup):
    details = []

    for card in soup.find_all('div', class_='card'):
        address_tag = card.find('p', class_='detailsPage')
        if address_tag:
            strong_tag = address_tag.find('strong', string='Address:')
            if strong_tag and strong_tag.next_sibling:
                address = strong_tag.next_sibling.strip()
                details.append(address)

    return ' '.join(details)

def extract_building_info(soup):
    details_paragraphs = soup.find_all('p', class_='detailsPage')
    
    num_buildings = ''
    year_built = ''
    
    for p in details_paragraphs:
        strong_tag = p.find('strong')
        if strong_tag:
            label = strong_tag.text.strip()
            value = p.text.replace(label, '').strip()
            
            if 'Number of buildings:' in label:
                num_buildings = value
                #print(f"Number of Buildings: {num_buildings}")
            elif 'Actual Year Built:' in label:
                year_built = value
                #print(f"Year Built: {year_built}")
    
    if not num_buildings:
        print("Number of buildings not found")
    if not year_built and num_buildings != '0':
        print("Year built not found")
    
    return num_buildings, year_built

def extract_table(soup):
    # Find the sale information card
    sale_info_card = None
    for card in soup.find_all('div', class_='card'):
        header = card.find('div', class_='card-header')
        if header and 'Sale Information' in header.text:
            sale_info_card = card
            break

    if not sale_info_card:
        #print("Sale information card not found")
        return ''

    table = sale_info_card.find('table', class_='table table-striped')

    if not table:
        #print("Sale information table not found")
        return ''

    sales_data = []

    for row in table.find('tbody').find_all('tr'):
        row_data = [td.get_text(strip=True) for td in row.find_all('td')]
        sales_data.append(row_data)

    flattened_data = [item for sublist in sales_data for item in sublist]
    single_row_data = ', '.join(flattened_data)

    #print(single_row_data)

    return single_row_data

def extract_data(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        january_1_owner = extract_owner_info(soup, 'January 1 Owner')
        current_owner = extract_owner_info(soup, 'Current Owner')
        address = extract_address(soup)
        num_buildings, year_built = extract_building_info(soup)
        sales = extract_table(soup)

        return {
            'URL': url,
            'January 1 Owner': january_1_owner,
            'Current Owner': current_owner,
            'Address': address,
            'Number of buildings': num_buildings,
            'Actual Year Built': year_built,
            'Sales': sales
        }
    except requests.RequestException as e:
        print(f"Error fetching {url}: {e}")
        return None

def read_urls_from_csv(file_path):
    ids_and_urls = []
    with open(file_path, mode='r', newline='') as file:
        reader = csv.reader(file)
        for row in reader:
            ids_and_urls.append((row[0], row[1]))
    return ids_and_urls

def process_urls(ids_and_urls, output_file):
    fieldnames = ['ID', 'URL', 'January 1 Owner', 'Current Owner', 'Address', 'Number of buildings', 'Actual Year Built', 'Sales']

    with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()

        for id_, url in ids_and_urls:
            data = extract_data(url)
            if data:
                data['ID'] = id_
                writer.writerow(data)
                #print(f"Processed: {url}")

if __name__ == "__main__":
    #csv_file_path = 'urls.csv'
    #csv_file_path = 'urls_RB.csv'
    csv_file_path = 'urls_nobuilds.csv'
    ids_and_urls = read_urls_from_csv(csv_file_path)
    output_file = "property_data.csv"
    #output_file = "property_dataRB.csv"
    process_urls(ids_and_urls, output_file)
    print(f"Data has been extracted and written to {output_file}")
