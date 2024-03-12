import pandas as pd
import csv
import time
import os
from settings import settings
import warnings

warnings.filterwarnings("ignore")

def dom_color_name(r: int, g: int, b: int) -> str:
    csv_reader = csv.reader(
        open("colors.csv", newline="", encoding="utf-16"),
        delimiter=","
    )
    next(csv_reader)
    color_match = { }

    for row in csv_reader:
        name, rd, gd, bd = row
        color_match[name] = (int(rd) - int(r)) ** 2 + (int(gd) - int(g)) ** 2 + (int(bd) - int(b)) ** 2

    return min(color_match, key=color_match.get)


MAX_ROWS_PER_SHEET = 1048575
MAX_URLS_PER_SHEET = 65530
MAX_SHEETS_PER_BOOK = 255

def split_csv_to_xslx(file: str, output_file: str | None = None) -> None:
    if not output_file: output_file = os.path.join(*os.path.split(file)[:-1], "xlsx_output", os.path.split(file)[-1]).replace(".csv", ".xlsx")

    print(output_file)
    n_file = 1
    n_sheet = 1
    start_row = 0

    df = pd.read_csv(file, encoding="utf-8", sep=settings.csv_del)
    l_df = len(df)

    writer = pd.ExcelWriter(output_file.replace(".xlsx", f"{n_file}.xlsx"), "auto")
    while start_row < l_df:
            end_row = min(start_row + MAX_ROWS_PER_SHEET, l_df)
            sheet_df = df.iloc[start_row:end_row]

            if (n_urls := sheet_df["Изображения"].apply(lambda x: len(x.split(";")) + 1)).sum() >= MAX_URLS_PER_SHEET:
                end_row = start_row + n_urls.cumsum().le(MAX_URLS_PER_SHEET).sum()
                sheet_df = df.iloc[start_row:end_row]

            if n_sheet >= MAX_SHEETS_PER_BOOK:
                writer.save()
                writer = pd.ExcelWriter(output_file.replace(".xlsx", f"{n_file}.xlsx"), engine="openpyxl")
                n_file += 1
                n_sheet = 0

            print(f"{n_sheet} [{start_row}:{end_row}], {n_urls.sum()}")
            sheet_df.to_excel(writer, sheet_name=f"Sheet{n_sheet}", index=False)
            start_row = end_row + 1
            n_sheet += 1
        
    writer.close()
