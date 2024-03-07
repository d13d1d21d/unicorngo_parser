import csv
from settings import settings


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


# !! Смотреть последние строки в parser_cards.py/parser_products.py
# MAX_ROWS_PER_SHEET = 1048575
# MAX_URLS_PER_SHEET = 65530 
# def split_csv_to_xslx(file: str, output_file: str | None = None) -> None:
#     if not output_file: output_file = file.replace(".csv", ".xlsx")
#     n_sheet = 1
#     start_row = 0

#     df = pd.read_csv(file, encoding="utf-8", sep=settings.csv_del)
#     l_df = len(df)

#     with pd.ExcelWriter(output_file, "auto") as writer:
#         while start_row < l_df:
#             print(n_sheet, start_row)
#             end_row = min(start_row + MAX_ROWS_PER_SHEET, l_df)
#             sheet_df = df.iloc[start_row:end_row]

#             if sheet_df["URL"].count() + sheet_df["Изображения"].apply(lambda x: len(x.split(";"))).sum() >= MAX_URLS_PER_SHEET:
#                 end_row = len(list(1 + len(i["Изображения"].split(";")) for _, i in sheet_df.iterrows()))
#                 sheet_df = sheet_df.iloc[start_row:end_row]

#             sheet_df.to_excel(writer, sheet_name=f"Sheet{n_sheet}")
#             n_sheet += 1
#             start_row = end_row