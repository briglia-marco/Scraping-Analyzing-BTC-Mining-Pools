import random
from fake_useragent import UserAgent
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests
import time
import os

# Generate Proxies from sslproxies.org and store them in a list 
## proxies, ua : List containing the proxies, UserAgent object
def generate_proxies(proxies, ua):
    proxies.clear() 
    proxies_req = Request('https://www.sslproxies.org/')
    proxies_req.add_header('User-Agent', ua.random)
    proxies_doc = urlopen(proxies_req).read().decode('utf8')
    soup = BeautifulSoup(proxies_doc, 'html.parser')
    proxies_table = soup.find('table', class_='table table-striped table-bordered')

    for row in proxies_table.tbody.find_all('tr'):
        td = row.find_all('td')
        proxies.append({
            'ip':   td[0].string,
            'port': td[1].string
        })

# Get a page with a random proxy from the list
## url, proxies, ua : URL of the page, List containing the proxies, UserAgent object
def get_page_with_proxy(url, proxies, ua):
    while True:
        if not proxies:
            print("Nessun proxy disponibile. Interruzione.")
            raise StopIteration
        proxy = random.choice(proxies)
        headers = {'User-Agent': ua.random}
        try:
            print(f"Usando proxy: {proxy['ip']}:{proxy['port']}")
            response = requests.get(url, headers=headers, proxies=proxy, timeout=20)
            response.raise_for_status()  # Exeption for status code 4xx/5xx
            time.sleep(2) # 2 seconds for not overloading the server
            return response
        except requests.exceptions.RequestException as e:
            print(f"Errore durante la richiesta: {e}. Rimuovo proxy {proxy['ip']}:{proxy['port']}")
            proxies.remove(proxy)
            time.sleep(2)

# Check if there is a next page in the pagination of walletexplorer.com
## soup : BeautifulSoup object of a walletexplorer.com page
def check_next_page(soup):
    next_page = soup.find("a", string="Next…")
    last_page = soup.find("a", string="Last")
    if next_page:
        return next_page["href"]
    elif last_page:
        return last_page["href"]
    else:
        return None

# Get the link to the page with the addresses of the mining pools
## mining_pools_addresses, base_url, proxies, ua : Dictionary with the mining pools and their addresses, URL of the page, List containing the proxies, UserAgent object
def get_address_page_link(mining_pools_addresses, base_url, proxies, ua):
    for pool_name in mining_pools_addresses: 
        if mining_pools_addresses[pool_name]:
            link = mining_pools_addresses[pool_name][0] 
            response = get_page_with_proxy(base_url + link, proxies, ua)
            soup = BeautifulSoup(response.text, "html.parser")
            wallet_address = soup.find("a", string="show wallet addresses")
            if wallet_address:
                mining_pools_addresses[pool_name][0] = wallet_address["href"]
            else:
                print(f"Non è stato trovato il link 'show wallet addresses' per la mining pool {pool_name}")
        else:
            print(f"Nessun link trovato per la mining pool {pool_name}")

# Extract the addresses of the mining pools in separate lists 
## single_mining_pool_addresses, mining_pools_addresses, base_url, proxies, ua : Dictionary with the mining pools and their addresses, URL of the page, List containing the proxies, UserAgent object
def extract_mining_pool_addresses(single_mining_pool_addresses, mining_pools_addresses, base_url, proxies, ua):
    for pool_name, link in mining_pools_addresses.items():
        url = base_url + link[0]
        while url:
            print("Richiesta a", url)
            response = get_page_with_proxy(url, proxies, ua)
            soup = BeautifulSoup(response.text, "html.parser")
            addresses = soup.select('td a')
            if not addresses:
                print(f"Nessun indirizzo trovato per {pool_name} alla URL: {url}")
            for address in addresses:
                single_mining_pool_addresses[pool_name].append(address.text)
            url = check_next_page(soup)
            if url:
                url = base_url + url
            else:
                print("Fine pagine")
                url = None

# Get the link to the page of the mining pool on WalletExplorer
## mining_pools, mining_pools_addresses, base_url, proxies, ua : List with the mining pools, Dictionary with the mining pools and their addresses, URL of the page, List containing the proxies, UserAgent object
def get_mining_pool_page_link(mining_pools, mining_pools_addresses, base_url, proxies, ua):
    response = get_page_with_proxy(base_url, proxies, ua)
    soup = BeautifulSoup(response.text, "html.parser")
    for pool in mining_pools:
        link = soup.find("a", string=pool) 
        if link:
            mining_pools_addresses[pool].append(link["href"])

# Scrape WalletExplorer to get the addresses of the mining pools
## mining_pools, proxies, ua, base_url, output_dir : List with the mining pools, List containing the proxies, UserAgent object, URL of the page, Output directory
def scrape_wallet_explorer(mining_pools, proxies, ua, base_url, output_dir):
    mining_pools_addresses = {pool: [] for pool in mining_pools}
    get_mining_pool_page_link(mining_pools, mining_pools_addresses, base_url, proxies, ua)
    get_address_page_link(mining_pools_addresses, base_url, proxies, ua)
    single_mining_pool_addresses = {pool: [] for pool in mining_pools} 
    extract_mining_pool_addresses(single_mining_pool_addresses, mining_pools_addresses, base_url, proxies, ua)
    os.makedirs(output_dir, exist_ok=True) 
    for pool_name, addresses in single_mining_pool_addresses.items():
        with open(f"{output_dir}/{pool_name}.csv", "w") as f:
            for address in addresses:
                f.write(f"{address}\n")
 
# Check if the csv files with the mining pool addresses are already present and not empty
## output_dir, mining_pools : Output directory, List with the mining pools
def check_csv_files(output_dir, mining_pools):
    for pool in mining_pools:
        if not os.path.exists(f"{output_dir}/{pool}.csv"): 
            return False
        if os.path.getsize(f"{output_dir}/{pool}.csv") == 0:
            return False
    return True
