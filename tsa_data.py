from selenium import webdriver
import numpy as np

import os
import sys

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary


os.environ['MOZ_HEADLESS'] = '1'

binary = FirefoxBinary('C:/Program Files/Mozilla Firefox/firefox.exe', log_file=sys.stdout)

browser = webdriver.Firefox(executable_path=r'C:/Users/grady/Downloads/geckodriver-v0.29.0-win64/geckodriver', firefox_binary=binary)

browser.get("https://www.tsa.gov/coronavirus/passenger-throughput")

table = browser.find_element_by_xpath("/html/body/div[2]/div/main/div[2]/div/div/div[4]/div/div/div[2]/table")

allRows = table.find_elements_by_tag_name("tr")


def readTable():
    cells = []
    elements = np.array([2, 3])
    for row in allRows:
        cells = row.find_elements_by_tag_name("td")
        if len(cells):
            if len(cells[1].text) == 0:
                return elements
            tmp = np.array([cells[0].text, cells[1].text])
            elements = np.vstack((elements, tmp))
    return elements


data = readTable()
print(data)
