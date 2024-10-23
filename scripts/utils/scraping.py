import random
from fake_useragent import UserAgent
from urllib.request import Request, urlopen
from bs4 import BeautifulSoup
import requests
import time
import os

# Funzione per generare proxy da sslproxies.org
def generate_proxies(proxies, ua):
    proxies.clear() # Svuoto la lista dei proxy (nel caso la funzione venga chiamata più volte non si vogliono avere duplicati)
    proxies_req = Request('https://www.sslproxies.org/')
    proxies_req.add_header('User-Agent', ua.random)
    proxies_doc = urlopen(proxies_req).read().decode('utf8')
    soup = BeautifulSoup(proxies_doc, 'html.parser')
    proxies_table = soup.find('table', class_='table table-striped table-bordered')
    # Salvo i proxy nella lista proxies
    for row in proxies_table.tbody.find_all('tr'):
        td = row.find_all('td')
        proxies.append({
            'ip':   td[0].string,
            'port': td[1].string
        })

def get_page_with_proxy(url, proxies, ua):
    while True:
        if not proxies:
            print("Nessun proxy disponibile. Interruzione.")
            raise StopIteration
        proxy = random.choice(proxies)  # Scelta dinamica del proxy
        headers = {'User-Agent': ua.random}
        try:
            print(f"Usando proxy: {proxy['ip']}:{proxy['port']}")
            response = requests.get(url, headers=headers, proxies=proxy, timeout=20)
            response.raise_for_status()  # Alza un'eccezione per codici di stato 4xx/5xx
            time.sleep(2)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Errore durante la richiesta: {e}. Rimuovo proxy {proxy['ip']}:{proxy['port']}")
            proxies.remove(proxy)  # Rimuovo il proxy che ha fallito
            time.sleep(2)  # Pausa prima di ritentare con un altro proxy

def check_next_page(soup):
    next_page = soup.find("a", string="Next…")
    last_page = soup.find("a", string="Last")
    if next_page:
        return next_page["href"]
    elif last_page:
        return last_page["href"]
    else:
        return None
    
def get_address_page_link(mining_pools_addresses, base_url, proxies, ua):
    for pool_name in mining_pools_addresses:  # Uso pool_name per chiarezza
        if mining_pools_addresses[pool_name]:
            link = mining_pools_addresses[pool_name][0]  # Prendo il link alla pagina degli indirizzi
            response = get_page_with_proxy(base_url + link, proxies, ua)
            soup = BeautifulSoup(response.text, "html.parser")
            # Trovo il link per gli indirizzi del wallet
            wallet_address = soup.find("a", string="show wallet addresses")
            if wallet_address:
                mining_pools_addresses[pool_name][0] = wallet_address["href"]  # Salvo il link alla pagina degli indirizzi
            else:
                print(f"Non è stato trovato il link 'show wallet addresses' per la mining pool {pool_name}")
        else:
            print(f"Nessun link trovato per la mining pool {pool_name}")

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

def get_mining_pool_page_link(mining_pools, mining_pools_addresses, base_url, proxies, ua):
    response = get_page_with_proxy(base_url, proxies, ua)
    soup = BeautifulSoup(response.text, "html.parser")
    for pool in mining_pools:
        link = soup.find("a", string=pool) 
        if link:
            mining_pools_addresses[pool].append(link["href"])

def scrape_wallet_explorer(mining_pools, proxies, ua, base_url, output_dir):
    mining_pools_addresses = {pool: [] for pool in mining_pools}  # Dizionario per le mining pool e relativi indirizzi
    # 1. Ricerca dei link delle mining pool su WalletExplorer
    get_mining_pool_page_link(mining_pools, mining_pools_addresses, base_url, proxies, ua)
    # 2. Itera sulle mining pool per ottenere il link alle pagine degli indirizzi
    get_address_page_link(mining_pools_addresses, base_url, proxies, ua)
    # 3. Estrazione degli indirizzi delle mining pool in liste separate
    single_mining_pool_addresses = {pool: [] for pool in mining_pools} 
    extract_mining_pool_addresses(single_mining_pool_addresses, mining_pools_addresses, base_url, proxies, ua)

    # Salvo i dati dentro dei file csv in una cartella
    os.makedirs(output_dir, exist_ok=True) 
    for pool_name, addresses in single_mining_pool_addresses.items():
        with open(f"{output_dir}/{pool_name}.csv", "w") as f:
            for address in addresses:
                f.write(f"{address}\n")

def check_csv_files(output_dir, mining_pools):
    # controllo se i 4 file sono già presenti e se sono non vuoti. 
    # Se sono presenti e non vuoti ritorno True, altrimenti False
    for pool in mining_pools:
        if not os.path.exists(f"{output_dir}/{pool}.csv"): 
            return False
        if os.path.getsize(f"{output_dir}/{pool}.csv") == 0:
            return False
    return True



proxies = []  # Lista dei proxy
ua = UserAgent()  # Generatore di User-Agent casuali
generate_proxies(proxies, ua)
base_url = "https://www.walletexplorer.com/"
output_dir = "indirizzi_wallet_explorer"
mining_pools = ["DeepBit.net", "Eligius.st", "BTCGuild.com", "BitMinter.com"]

if not check_csv_files(output_dir, mining_pools):
    print("ERRORE")
    scrape_wallet_explorer(mining_pools, proxies, ua, base_url, output_dir)
else:
    print("I file csv con gli indirizzi delle mining pool sono già presenti e non vuoti")   

# voglio leggere i file csv e metterli dentro un dizionario con chiave il nome della mining pool e valore la lista degli indirizzi
mining_pools_addresses = {}
for pool in mining_pools:
    with open(f"{output_dir}/{pool}.csv", "r") as f:
        mining_pools_addresses[pool] = f.read().splitlines()











# 4. Deanonimizzazione degli indirizzi delle mining pool
# TODO implementare la deanonimizzazione degli indirizzi delle mining pool
# confrontare le transazioni coinbase con gli indirizzi delle mining pool e assegnare la mining pool corrispondente all'indirizzo coinbase 

