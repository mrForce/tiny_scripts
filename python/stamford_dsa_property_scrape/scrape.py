import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from lxml import html
import csv
import os
import time


retry_strat = Retry(total=5, backoff_factor=2, status_forcelist=[429, 500, 502, 503, 504])
adapter=HTTPAdapter(max_retries=retry_strat)

session = requests.Session()
session.mount('https://', adapter)
session.mount('http://', adapter)

output = 'scrape.tsv'

base_url = 'https://gis.vgsi.com/stamfordct/Streets.aspx?Letter='
urls = [base_url + x for x in ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U', 'V', 'W', 'Y', 'Z']]
street_links = []
for url in urls:
    print('url')
    print(url)
    x = session.get(url).text
    print(x)
    tree = html.fromstring(x)
    for street in tree.xpath('//*[@id="list"]/li'):
        elements = street.xpath('a')
        if len(elements) != 1:
            print('elements')
            print(elements)    
        assert(len(elements) == 1)
        print('street name: ' + street.text_content())
        street_link = 'https://gis.vgsi.com/stamfordct/' + elements[0].attrib['href']
        street_links.append((street.text_content(), street_link))
print('street links')
print(street_links)
property_links = []        
for street_name, street_link in street_links:
    print('street link: ' + street_link)
    r = session.get(street_link).text
    tree = html.fromstring(r)
    properties = tree.xpath('//*[@id="list"]/li')
    for p in properties:
        elements = p.xpath('a')
        assert(len(elements) == 1)
        property_link = 'https://gis.vgsi.com/stamfordct/' + elements[0].attrib['href']
        property_links.append((street_name, property_link))
        
print('property links')
print(property_links)

with open('properties.txt', 'w') as f:
    for street_name, p_link in property_links:
        f.write(street_name + '\t' + p_link + '\n')
print('done writing property links to properties.txt')


completed_property_links = set()
if os.path.isfile(output):
    with open(output, 'r') as f:
        reader = csv.DictReader(f, delimiter='\t')
        for row in reader:
            link = row['link']
            completed_property_links.add(link)
property_links = []
with open('properties.txt', 'r') as f:
    for line in f:
        if len(line) > 0:
            parts = [x.strip() for x in line.split('\t')]
            print(parts)
            assert(len(parts) == 2)
            if parts[1] not in completed_property_links:
                property_links.append(parts)

            
property_attr_xpath = {'location': '//*[@id="MainContent_lblLocation"]', 'acct': '//*[@id="MainContent_lblAcctNum"]', 'assessment': '//*[@id="MainContent_lblGenAssessment"]', 'pid': '//*[@id="MainContent_lblPid"]', 'mblu': '//*[@id="MainContent_lblMblu"]', 'owner': '//*[@id="MainContent_lblGenOwner"]', 'appraisal':  '//*[@id="MainContent_lblGenAppraisal"]', 'buildingCount': '//*[@id="MainContent_lblBldCount"]'}


f = open(output, 'a')
w = csv.DictWriter(f, delimiter='\t', fieldnames=list(property_attr_xpath.keys()) + ['street', 'link'])
w.writeheader()
for street_name, p_link in property_links:
    print('requesting property')
    r = session.get(p_link).text
    tree = html.fromstring(r)
    print('tree')
    print(tree)
    p = {}
    for k,v in property_attr_xpath.items():
        x = tree.xpath(v)
        value = 'NULL'
        if len(x) > 0:
            value = x[0].text
        else:
            print('Link ' + p_link + ' missing property: ' + k)
        p[k] = value
    p['street'] = street_name
    p['link'] = p_link
    w.writerow(p)
    

f.close()
