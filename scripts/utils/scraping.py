import random
from selenium.webdriver.chrome.options import Options
from fake_useragent import UserAgent
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests
import time
import os
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

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
            print(f"Errore during request: {e}. Removing proxy {proxy['ip']}:{proxy['port']}")
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
                print(f"Link not found 'show wallet addresses' for the mining pool {pool_name}")
        else:
            print(f"Link not found for mining pool {pool_name}")

# Extract the addresses of the mining pools in separate lists 
## single_mining_pool_addresses, mining_pools_addresses, base_url, proxies, ua : Dictionary with the mining pools and their addresses, URL of the page, List containing the proxies, UserAgent object
def extract_mining_pool_addresses(single_mining_pool_addresses, mining_pools_addresses, base_url, proxies, ua):
    for pool_name, link in mining_pools_addresses.items():
        url = base_url + link[0]
        while url:
            print("Request at", url)
            response = get_page_with_proxy(url, proxies, ua)
            soup = BeautifulSoup(response.text, "html.parser")
            addresses = soup.select('td a')
            if not addresses:
                print(f"Address not found {pool_name} at URL: {url}")
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
        if addresses: 
            file_path = os.path.join(output_dir, f"{pool_name}.csv")
            try:
                with open(file_path, "w") as f:
                    for address in addresses:
                        f.write(f"{address}\n")
                print(f"Saved {len(addresses)} addresses for {pool_name} in {file_path}")
            except IOError as e:
                print(f"Error during writing of {file_path}: {e}")
        else:
            print(f"Address not found for {pool_name}. File not created.")
 
# Check if the csv files with the mining pool addresses are already present and not empty
## output_dir, mining_pools : Output directory, List with the mining pools
def check_csv_files(output_dir, mining_pools):
    if not os.path.exists(output_dir):
        return False
    for pool in mining_pools:
        if not os.path.exists(f"{output_dir}/{pool}.csv"): 
            return False
        if os.path.getsize(f"{output_dir}/{pool}.csv") == 0:
            return False
    return True

# Scrape WalletExplorer to get the addresses of the mining pools
## top_4_miners, base_url, wallet_id : DataFrame with the top 4 miners, URL of the page, List with the wallet IDs
def found_miners(top_4_miners, base_url, wallet_id):
    options = Options()
    options.add_argument('--headless=new')
    driver = webdriver.Chrome(options=options)
    wait = WebDriverWait(driver, 10)
    for hash_value in top_4_miners["hash"]:
        driver.get(base_url)
        search_box = wait.until(EC.presence_of_element_located((By.NAME, "q"))) 
        search_box.clear() 
        search_box.send_keys(hash_value) 
        search_box.send_keys(Keys.RETURN)
        try:
            wallet = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "div h2"))).text.split(" ")[1]
            wallet_id[hash_value] = wallet
        except Exception as e:
            print(f"Error: wallet ID not found {hash_value}: {e}")
    driver.quit()

# Get the txid and the hash of the input and output 
## txid, base_url, proxies, ua : Transaction ID, URL of the page, List containing the proxies, UserAgent object
def get_hash_and_transaction(txid, base_url, proxies, ua):
    response = get_page_with_proxy(base_url + txid, proxies, ua)
    soup = BeautifulSoup(response.text, "html.parser")
    output_txids = []
    input_hash = []
    output_hash = []
    input_table = soup.select_one("table.tx > tr > td:nth-of-type(1) > table.empty")
    output_table = soup.select_one("table.tx > tr > td:nth-of-type(2) > table.empty")

    if input_table and output_table:
        input_trs = input_table.select("tr")
        output_trs = output_table.select("tr")
        get_hash(input_trs, input_hash)
        get_hash(output_trs, output_hash)
        get_output_txids(output_trs, output_txids)
    else:
        print("Impossibile trovare le tabelle degli input o degli output.")
    return output_txids, input_hash, output_hash

# Get the hash of the input and output
## trs, list_hash : List of tr elements, List of hashes
def get_hash(trs, list_hash):
    for tr in trs:
        hash = tr.select_one("td a")
        if hash:
            list_hash.append(hash.text.strip())
        else:
            list_hash.append("Coinbase")

# Get the output txids
## trs, output_txids : List of tr elements, List of output txids
def get_output_txids(trs, output_txids):
    for tr in trs:
        hash = tr.select_one("td.small a")
        if hash:
            output_txids.append(hash["href"])
