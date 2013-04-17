import requests
from bs4 import BeautifulSoup

r = requests.get("http://www.starcitygames.com/pages/decklists/")
soup = BeautifulSoup(r.text)

top = soup.find('div', id="dynamicpage_standard_list").findAll('p')[0].a['href']
soup.find('section', id="content").table