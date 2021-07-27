import numpy as np

import os
import sys

from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium import webdriver

from twilio.rest import Client
number = "+16043121279"
fromNumber = "+12104602756"
accountSID = "AC49c954e929d3f6541a0b255098c11f39"
authToken = "c717968e2df864f5e640e06fb6112563"
client = Client(accountSID, authToken)

os.environ['MOZ_HEADLESS'] = '1'

binary = FirefoxBinary('C:/Program Files/Mozilla Firefox/firefox.exe', log_file=sys.stdout)

browser = webdriver.Firefox(executable_path=r'geckodriver', firefox_binary=binary)

browser.get("https://www.tsa.gov/coronavirus/passenger-throughput")

table = browser.find_element_by_xpath("/html/body/div[2]/div/main/div[2]/div/div/div[4]/div/div/div[2]/table")

allRows = table.find_elements_by_tag_name("tr")


def readTable():
    cells = []
    elements = [["Date", "Throughput"]]
    for row in allRows:
        cells = row.find_elements_by_tag_name("td")
        if len(cells):
            if len(cells[1].text) == 0:
                return elements
            # tmp = [cells[0].text, cells[1].text]
            daily_throughput = int(cells[1].text.replace(',', ''))
            elements.append([cells[0].text, daily_throughput])

    return elements


data = readTable()
del data[0]

np.savetxt("throughput.csv", data, delimiter=", ", fmt="% s")

client.messages.create(to=number, from_=fromNumber, body="Updated throughput data")



