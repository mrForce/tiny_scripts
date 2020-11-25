import requests
from lxml import html
import csv

base_url = 'https://gis.vgsi.com/stamfordct/Streets.aspx?Letter='
output = 'scrape.tsv'
urls = [base_url + chr(x) for x in range(65, 91)]
r = [requests.get(url).text for url in urls]
street_links = []
for x in r:
    tree = html.fromstring(x)
    for street in tree.xpath('//*[@id="list"]/li'):
        elements = street.xpath('a')
        assert(len(elements) == 1)
        street_link = 'https://gis.vgsi.com/stamfordct/' + elements[0].attrib['href']
        street_links.append(street_link)
print('street links')
print(street_links)
property_links = []        
for street_link in street_links:
    r = requests.get(street_link).text
    tree = html.fromstring(r)
    properties = tree.xpath('//*[@id="list"]/li')
    for p in properties:
        elements = p.xpath('a')
        assert(len(elements) == 1)
        property_link = 'https://gis.vgsi.com/stamfordct/' + elements[0].attrib['href']
        property_links.append(property_link)
print('property links')
print(property_links)
        
properties = []
property_attr_xpath = {'location': '//*[@id="MainContent_lblLocation"]', 'acct': '//*[@id="MainContent_lblAcctNum"]', 'assessment': '//*[@id="MainContent_lblGenAssessment"]', 'pid': '//*[@id="MainContent_lblPid"]', 'mblu': '//*[@id="MainContent_lblMblu"]', 'owner': '//*[@id="MainContent_lblGenOwner"]', 'appraisal':  '//*[@id="MainContent_lblGenAppraisal"]', 'buildingCount': '//*[@id="MainContent_lblBldCount"]'}
for p_link in property_links:
    print('requesting property')
    r = requests.get(p_link).text
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
    properties.append(p)

with open(output, 'w') as f:
    w = csv.DictWriter(f, delimiter='\t', fieldnames=property_attr_xpath.keys())
    w.writeheader()
    w.writerows(properties)
