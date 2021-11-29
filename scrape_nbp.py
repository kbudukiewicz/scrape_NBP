"""
Module to scrape data from NBP and convert some courses from xlsx file.
"""
from bs4 import BeautifulSoup
import requests
import pandas as pd
from typing import Dict


def scrape_data(url: str) -> Dict[str, Dict[str, str]]:
    """
    Scrape data from HTML. Find XML in HTML and find average price, converter and key of the stock.
    Create dictionary with important data like key,course and corverter.
    Args:
        url: Name of HTML.

    Return:
        dict_stocks: Dictionary {key : {course, converter}}
    """
    soup = BeautifulSoup(requests.get(url).text, "lxml")

    string = str(soup.find('a', text='Powyższa tabela w formacie .xml'))
    link = string.split('<a href="')[1].split('"')[0]

    xml_link = "https://www.nbp.pl" + link
    soup = BeautifulSoup(requests.get(xml_link).content, "xml")

    dict_stocks = {}

    stocks = list(soup.find_all('pozycja'))
    for stock in stocks:
        dict_stocks[stock.find('kod_waluty').get_text()] = {'kurs_sredni' :stock.find('kurs_sredni').get_text(), 'przelicznik': stock.find('przelicznik').get_text()}

    return dict_stocks


def gpw_biggest_ratio(file: str) -> pd.DataFrame:
    """Find the stock with the biggest 'Ration' from xlsx file.
        Read the xlsx file, calculate ration and check condition.

    Args:
        file: Name xml file

    Return:
        The stock with the biggest 'Ratio' from xlsx file
    """

    gpw = pd.read_excel(file)
    gpw["Ratio"] = gpw["Kurs max"] / gpw["Kurs min"]

    return gpw.loc[(gpw["Ratio"] == max(gpw["Ratio"])) & gpw["Wolumen"] > 0]


def count_value(key_value: str) -> None:
    """Check the name key and to convert price the stock.
        Create new DataFrame to data, check key of the stock and calculate price to good currency.

    Args:
        key_value: Name key value.
    Return:
        Final string of score DataFrame.
    """
    file = "GPW.xlsx"
    url = "https://www.nbp.pl/home.aspx?f=/kursy/kursya.html"

    stocks = scrape_data(url)

    gpw = gpw_biggest_ratio(file)
    new = pd.DataFrame(
        gpw,
        columns=["Kurs otwarcia", "Kurs zamknięcia", "Kurs max", "Kurs min", "Obrót"],
    )

    if key_value in list(stocks.keys()):
        print(float(stocks[key_value]['kurs_sredni'].replace(",", ".")) * new)
    else:
        print('Zly kod waluty!')


if __name__ == "__main__":
    print("Podaj kod waluty:")
    key = input()
    count_value(key)
