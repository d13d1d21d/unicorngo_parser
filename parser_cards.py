from settings import settings
from colorama import Fore, Style, just_fix_windows_console
from proxy_client import *
from webparser import *

import platform
import time
import os


if platform.system() == "Windows":
    just_fix_windows_console()


print(f"""[{Fore.CYAN + Style.BRIGHT}i{Style.RESET_ALL}] Настройки:
    - {Fore.YELLOW}Режим{Fore.RESET}: Карточки товаров
    - {Fore.YELLOW}Товаров за страницу{Fore.RESET}: {settings.cards.per_page}
    - {Fore.YELLOW}В XLSX{Fore.RESET}: {"Да" if settings.to_xlsx else "Нет"}""")

time.sleep(3)
os.system("cls")

proxy_client = ProxyClient(open("proxy_list.txt").read(), ProxyProtocol.HTTP)
parser = WebParser(proxy_client, settings.cards.per_page)

page = 1
cards = []
p_cards = True

for size in settings.sizes:
    print(f"\n[{Fore.CYAN + Style.BRIGHT}⧖{Style.RESET_ALL}] Парсинг {Style.BRIGHT + str(size) + Style.RESET_ALL} размера...")
    for brand in settings.brands:
        print(f"\n  > [{Fore.CYAN + Style.BRIGHT}⧖{Style.RESET_ALL}] Парсинг {Style.BRIGHT + brand + Style.RESET_ALL}...")
        p_cards = True

        while p_cards:
            print(f"      > [{Fore.CYAN + Style.BRIGHT}⧖{Style.RESET_ALL}] Получение товаров на странице {Style.BRIGHT + str(page) + Style.RESET_ALL}")
            if p_cards := parser.parse_cards(page, size, brand):
                if p_cards != -1:
                    print(f"      > [{Fore.GREEN + Style.BRIGHT}✓{Style.RESET_ALL}] Обработано {Style.BRIGHT + str(len(p_cards)) + Style.RESET_ALL} товаров")
                    cards += p_cards
                else:
                    print(f"      > [{Fore.RED + Style.BRIGHT}X{Style.RESET_ALL}] Ошибка парсинга страницы {page}. Информация занесена в parser_logs.log")

                page += 1
        
        page = 1

print(f"[{Fore.GREEN + Style.BRIGHT}✓{Style.RESET_ALL}] Парсинг завершен. Обработано {Style.BRIGHT + str(len(cards)) + Style.RESET_ALL} карточек")
pd.DataFrame(form_dataframe(cards, "cards")).to_csv("output/output_cards.csv", sep=settings.csv_del, index=False, encoding="utf-8")
if settings.to_xlsx:
    split_csv_to_xslx("output/output_cards.csv")
