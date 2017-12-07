# -*- coding: utf-8 -*-
import requests, json
from bs4 import BeautifulSoup
import unicodecsv as csv

# Page to start scraping from
START_URL = "https://delhi.ngosindia.com/delhi-ngos/"

def scrape_ngo_list(page_url, page_no=1):

    # Opening the first page
    # We will iterate to next page after this
    page = requests.get(page_url)

    # Get the BS instance
    soup = BeautifulSoup(page.content, "html.parser")

    # Finding all the links on the page
    ngo_links = soup.find(id="lcp_instance_0").findAll("a")
    ngo_links = [link.get("href") for link in ngo_links]
    print "Found {0} links on page number {1}.".format(len(ngo_links), page_no)

    # Writing the links to a file
    links = "\n".join(ngo_links)
    links = "\n" + links
    links_file = open("ngoindia_links.txt", "a")
    links_file.write(links)
    links_file.close()

    # Finding the next page link
    current_page_li = soup.findAll("li", {'class': 'lcp_currentpage'})[0]
    next_page_li = current_page_li.find_next()
    if next_page_li.name != 'li':
        print "We are done with the scraping."
        next_page_link = None
    else:
        next_page_link = next_page_li.find("a").get("href")
        print next_page_link
        page_no = page_no + 1
        scrape_ngo_list(next_page_link, page_no)

def scrape_ngo_details(ngo_link):

    try:
        print "Scraping {0}".format(ngo_link)

        # Opening the NGO link
        page = requests.get(ngo_link)

        # get the BS instance
        soup = BeautifulSoup(page.content, "html.parser")

        # Getting the details from the page
        details_el = soup.select("h1 .ngo-postheader,.entry-title")[0].find_next()
        details_text = details_el.text

        # get the name of the organisation
        name = soup.select("h1 .ngo-postheader,.entry-title")[0]
        name = name.text
        name = name.split(',')[0]

        # iterating and getting every detail
        details_dict = {'name': name}
        current_key = None
        current_value = None
        for line in details_text.split("\n"):
            splitted = line.split(":")
            if len(splitted) > 1:
                current_key = splitted[0].strip()
                if 'website' in current_key.lower():
                    details_dict[current_key] = ':'.join(splitted[1:])
                else:
                    details_dict[current_key] = splitted[1]
            else:
                details_dict[current_key] = details_dict[current_key] + "\n" + splitted[0]
        return details_dict
    except Exception as e:
        return None


def scrape_all_links():

    # open the file with links
    links_file = open("ngoindia_links.txt", "r")
    links = links_file.read().split("\n")[:-2]

    ngo_details = []
    for link in links:
        # scrape the details
        details = scrape_ngo_details(link)
        if details:
            ngo_details.append(details)    
    return ngo_details


def get_final_csv():

    # load from json
    json_file = open("ngo.json")
    details = json.loads(json_file.read())

    # keys of the csv file
    keys = set()
    for detail in details:
        for key in detail.keys():
            keys.add(key)
    keys = list(keys)

    # writing to a file
    with open('ngosindia.csv', 'wb') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(rows)
    
    print "Done"