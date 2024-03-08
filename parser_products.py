from settings import settings
from colorama import Fore, Style, just_fix_windows_console
from proxy_client import *
from webparser import *

import threading
import concurrent.futures
import csv
import platform
import time
import os


csv_writer_lock = threading.Lock()

if platform.system() == "Windows":
    just_fix_windows_console()


print(f"""[{Fore.CYAN + Style.BRIGHT}i{Style.RESET_ALL}] Настройки:
    - {Fore.YELLOW}Режим{Fore.RESET}: Полный парсинг
    - {Fore.YELLOW}Размер чанка{Fore.RESET}: {settings.products.chunk_size}
    - {Fore.YELLOW}В XLSX{Fore.RESET}: {"Да" if settings.to_xlsx else "Нет"}
    - {Fore.YELLOW}Кол-во потоков{Fore.RESET}: {settings.products.threads}""")


time.sleep(3)
os.system("cls")


products = []
proxy_client = ProxyClient(open("proxy_list.txt").read(), ProxyProtocol.HTTP)
parser = WebParser(proxy_client, 0)

with open("output/output_cards.csv", encoding="utf-8") as f:
    n_rows = 1 + sum(1 for row in f)


n = 0
insert_headers = True
csv_reader = csv.reader(open("output/output_cards.csv", "r", encoding="utf-8"))
next(csv_reader)

cards = []
for row in csv_reader:
    cards.append(ProductCard(
        row[0],
        row[1],
        row[2],
        int(row[3]),
        row[4],
        row[5],
        row[6].split(";"),
        True
    ))


print(f"[{Fore.CYAN + Style.BRIGHT}⧖{Style.RESET_ALL}] Запуск потоков...\n")
with concurrent.futures.ThreadPoolExecutor(settings.products.threads) as executor:
    t = time.time()
    for i in executor.map(parser.parse_product, cards):
        if i: 
            products += i
            n += 1

        if len(products) >= settings.products.chunk_size:
            with csv_writer_lock:
                print(f"[{Fore.CYAN + Style.BRIGHT}{n}/{n_rows}{Style.RESET_ALL}] Запись чанка из {Style.BRIGHT + str(len(products)) + Style.RESET_ALL} товаров в CSV", time.time() - t, n)
                pd.DataFrame(form_dataframe(products, "products")).to_csv(
                    "output/output.csv", 
                    sep=settings.csv_del, 
                    index=False, 
                    encoding="utf-8",
                    header=insert_headers, 
                    mode="w" if insert_headers else "a"
                )
                if insert_headers: insert_headers = False

                log_info(n)
                products = []


print(f"[{Fore.GREEN + Style.BRIGHT}✓{Style.RESET_ALL}] Парсинг завершен. Обработано {Style.BRIGHT + str(n) + Style.RESET_ALL} товаров")
pd.DataFrame(form_dataframe(products, "products")).to_csv("output/output.csv", sep=settings.csv_del, index=False, encoding="utf-8", header=insert_headers)
if settings.to_xlsx:
    split_csv_to_xslx("output/output.csv")

