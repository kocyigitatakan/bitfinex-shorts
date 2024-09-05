from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pytz
import re

target_url_shorts = "https://blockchainwhispers.com/bitmex-position-calculator"
target_url_price = "https://blockchainwhispers.com/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}

resp_shorts = requests.get(target_url_shorts, headers=headers)
soup_shorts = BeautifulSoup(resp_shorts.text, 'html.parser')

resp_price = requests.get(target_url_price, headers=headers)
soup_price = BeautifulSoup(resp_price.text, 'html.parser')

btc_table = soup_shorts.find_all('div', class_='bcw-calculator-longs-shorts my-3')[0]
btc_shorts = btc_table.find_all('div', class_='card-shorts-value')[0]
btc_short_value = btc_shorts.find('span').get_text()

eth_table = soup_shorts.find_all('div', class_='bcw-calculator-longs-shorts eth my-3')[0]
eth_shorts = eth_table.find_all('div', class_='card-shorts-value')[0]
eth_short_value = eth_shorts.find('span').get_text()

btc_price_selector = 'body > div.container-fluid.main > div.row.no-gutters > div.col-md-5.col-lg-4.right-block.animate__animated > div > div > div.top-coins-block > table > tbody > tr:nth-child(1) > td.coin-details.coin-price'
btc_price = soup_price.select_one(btc_price_selector).get_text()

eth_price_selector = 'body > div.container-fluid.main > div.row.no-gutters > div.col-md-5.col-lg-4.right-block.animate__animated > div > div > div.top-coins-block > table > tbody > tr:nth-child(2) > td.coin-details.coin-price'
eth_price = soup_price.select_one(eth_price_selector).get_text()

timezone_istanbul = pytz.timezone('Europe/Istanbul')
now_istanbul = datetime.now(timezone_istanbul)
formatted_datetime = now_istanbul.strftime('%Y-%m-%d %H:%M %z')
formatted_datetime = formatted_datetime[:-2] + ':' + formatted_datetime[-2:]
log_file_path = "data/short-logs-w-price.md"

old_content = []
try:
    with open(log_file_path, 'r') as log_file:
        header = log_file.readline()
        separator = log_file.readline()
        old_content = log_file.readlines()
except FileNotFoundError:
    header = "| Date & Time | BTC Shorts | BTC Price | ETH Shorts | ETH Price |\n"
    separator = "|-------------|------------|------------|------------|------------|\n"
    old_content = []

last_row = old_content[0] if old_content else None
columns = last_row.split('|')

pattern = r"(\$\s?[\d,]+(?:\.\d+)?)"
def extract_value(span_string):
    match = re.search(pattern, span_string)
    return match.group(1).strip() if match else None

parsed_btc_short_value = extract_value(columns[2])
parsed_btc_price_value = extract_value(columns[3])

parsed_eth_short_value = extract_value(columns[4])
parsed_eth_price_value = extract_value(columns[5])

btc_short_color = "red"
btc_price_color = "red"
eth_short_color = "red"
eth_price_color = "red"

if (int)(parsed_btc_short_value.replace('$', '').replace(',', '')) > (int)(btc_short_value.replace('$', '').replace(',', '')):
    btc_short_color = "green"

if (int)(parsed_btc_price_value.replace('$', '').replace(',', '').split('.')[0].strip()) < (int)(btc_price.replace('$', '').replace(',', '').split('.')[0].strip()):
    btc_price_color = "green"

if (int)(parsed_eth_short_value.replace('$', '').replace(',', '')) > (int)(eth_short_value.replace('$', '').replace(',', '')):
    eth_short_color = "green"

if (int)(parsed_eth_price_value.replace('$', '').replace(',', '').split('.')[0].strip()) < (int)(eth_price.replace('$', '').replace(',', '').split('.')[0].strip()):
    eth_price_color = "green"


formatted_btc_short_value = f"$${{\\color{{{btc_short_color}}}\\\\{btc_short_value}}}$$"
formatted_btc_price_value = f"$${{\\color{{{btc_price_color}}}\\\\{btc_price.strip()}}}$$"
formatted_eth_short_value = f"$${{\\color{{{eth_short_color}}}\\\\{eth_short_value}}}$$"
formatted_eth_price_value = f"$${{\\color{{{eth_price_color}}}\\\\{eth_price.strip()}}}$$"

new_row = f"| {formatted_datetime} | {formatted_btc_short_value} | {formatted_btc_price_value} | {formatted_eth_short_value} | {formatted_eth_price_value} |\n"

new_content = [header, separator, new_row] + old_content

with open(log_file_path, 'w') as log_file:
    log_file.writelines(new_content)
