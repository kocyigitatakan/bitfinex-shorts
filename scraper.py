from bs4 import BeautifulSoup
import requests
from datetime import datetime
import pytz

target_url = "https://blockchainwhispers.com/bitmex-position-calculator"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36"
}

resp = requests.get(target_url, headers=headers)
soup = BeautifulSoup(resp.text, 'html.parser')

btc_table = soup.find_all('div', class_='bcw-calculator-longs-shorts my-3')[0]
btc_shorts = btc_table.find_all('div', class_='card-shorts-value')[0]
btc_short_value = btc_shorts.find('span').get_text()

eth_table = soup.find_all('div', class_='bcw-calculator-longs-shorts eth my-3')[0]
eth_shorts = eth_table.find_all('div', class_='card-shorts-value')[0]
eth_short_value = eth_shorts.find('span').get_text()

timezone_istanbul = pytz.timezone('Europe/Istanbul')
now_istanbul = datetime.now(timezone_istanbul)
formatted_datetime = now_istanbul.strftime('%Y-%m-%d %H:%M %z')
formatted_datetime = formatted_datetime[:-2] + ':' + formatted_datetime[-2:]
log_file_path = "data/short-logs.md"

old_content = []
try:
    with open(log_file_path, 'r') as log_file:
        header = log_file.readline()
        separator = log_file.readline()
        old_content = log_file.readlines()
except FileNotFoundError:
    header = "| Date & Time | BTC Shorts | ETH Shorts |\n"
    separator = "|-------------|------------|------------|\n"
    old_content = []

new_row = f"| {formatted_datetime} | {btc_short_value} | {eth_short_value} |\n"

new_content = [header, separator, new_row] + old_content

with open(log_file_path, 'w') as log_file:
    log_file.writelines(new_content)