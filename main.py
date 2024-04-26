import concurrent.futures
import platform

from utils import *
from colorama import Fore, Style, just_fix_windows_console
from proxy_client import *
from webparser import *
from settings.settings import settings


PREFIX = "UNG-"
if platform.system() == "Windows":
    just_fix_windows_console()

proxy_client = ProxyClient(
    map_proxies("http", open("proxy_list.txt").read().split("\n")),
    retries=5
)
parser = Parser(proxy_client)
insert_headers = [True, True]
executor = concurrent.futures.ThreadPoolExecutor(50)
ns = 0

logger.log_new_run()

for size in settings.sizes:
    ns += 1
    for brand in settings.brands:
        v = []
        n = 0
        print(f"\n[{Fore.CYAN + Style.BRIGHT}⧖{Style.RESET_ALL}] Получение товаров для {brand} - {size} [{Fore.CYAN}{ns}/{len(settings.sizes)}{Style.RESET_ALL}]")

        spus = True
        brand_spus = []
        page = 1

        while spus:
            if spus := parser.get_spus(page, size, brand):
                brand_spus += list(
                    [i, brand] for i in spus
                )
                page += 1

        if brand_spus:
            logger.log(LogType.INFO, f"Получено {len(brand_spus)} товаров для {brand} - {size}")
            print(f"[{Fore.GREEN + Style.BRIGHT}✓{Style.RESET_ALL}] Получено товаров: {len(brand_spus)}. Обработка:")

            for vs in executor.map(parser.get_product_data, brand_spus):
                if vs: 
                    v += vs
                    n += 1
                    if n % 100 == 0:
                        print(f"    > [{Fore.CYAN + Style.BRIGHT}{n}/{len(brand_spus)}{Style.RESET_ALL}] Обработано {len(v)} вариаций")
                        logger.log(LogType.INFO, f"Обработано {len(v)} вариаций для {brand} - {size}")

            if len(brand_spus) % 10 != 0: 
                print(f"    > [{Fore.CYAN + Style.BRIGHT}{n}/{len(brand_spus)}{Style.RESET_ALL}] Обработано {len(v)} вариаций")
                logger.log(LogType.INFO, f"Обработано {len(v)} вариаций для {brand} - {size}")

            create_df(v, False, PREFIX).to_csv(
                "output/unicorngo-products.csv",
                sep=";",
                index=False,
                encoding="utf-8",
                header=insert_headers[0], 
                mode="w" if insert_headers[0] else "a"
            )
            if insert_headers[0]: insert_headers[0] = False
            
            create_df(v, True, PREFIX).to_csv(
                "output/unicorngo.csv",
                sep=";",
                index=False,
                encoding="utf-8",
                header=insert_headers[1], 
                mode="w" if insert_headers[1] else "a"
            )
            if insert_headers[1]: insert_headers[1] = False
            logger.log(LogType.INFO, f"Записан чанк из {len(v)} линий. Обработано {n}/{len(brand_spus)} товаров")

        else:
            logger.log(LogType.INFO, f"Товары для {brand} - {size} не найдены")
            print(f"[{Fore.RED + Style.BRIGHT}X{Style.RESET_ALL}] Товары не найдены")
