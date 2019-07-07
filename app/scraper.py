"""Test."""
import csv
import os
import random
import time
from io import StringIO, BytesIO

import requests
from lxml import html

from app import app, db, models

# Initial loading of proxies from file


def load_proxies(proxies_file):  # todo add default value
    """
    proxies_file : string
        path to text file of proxies, one per line
    """
    with open(proxies_file, 'rb') as proxies:
        return [proxy.strip() for proxy in proxies.readlines() if proxy]


# Pulls new random proxy from the list
def next_proxy(proxies_list):  # todo improve to ensure the same IP isn't used twice in a row; do not run list in order
    return random.choice(proxies_list)


# Initial loading of user agents from file
def load_uas(user_agents_file):  # todo add default value
    """
    user_agents_file : string
        path to text file of user agents, one per line
    """
    with open(user_agents_file, 'rb') as uaf:
        return [ua.strip() for ua in uaf.readlines() if ua]


# Pulls new random user agent from the list
def next_ua(uas_list):
    return random.choice(uas_list)


# Creates url from search criteria and current page
def build_url(search_term, location, page_number):
    template = (
        'http://www.yellowpages.com/search?search_terms={search_term}&geo_location_terms={location}&page={page_number}')
    return template.format(search_term=search_term, location=location, page_number=page_number)


def get_page(url, proxy, header, proxies_list):
    for _ in range(5):
        try:
            r = requests.get(url, headers=header, proxies=proxy, timeout=15)
            if r.status_code == 200:
                return r
            # retry any other code, because various status codes are actually honeypots.
            print('Last attempt failed, with status code: {}. Trying again.'.format(r.status_code))
        except requests.exceptions.HTTPError as h:
            print('Error: ', h.response.status_code, '. Trying again.')
        except requests.exceptions.Timeout as t:
            print('Uh oh: ', t, '. Retrying now.')
        except requests.exceptions.RequestException as e:
            print('Uh oh: ', e)
            return

        time.sleep(15)
        # todo fix proxy = {"http": next_proxy(proxies_list)}  to load random proxy
#       # todo load random user-agent

    print('Ok, I give up.')
    return


def parse_contact_info(result):
    """Parse all the contact information from a result.

    Note:
        YellowPages.com use multiple XPath templates, seemingly to mess with scrapers,
        which is pretty rediculous since they don't even offer a paid API alternative.

    """
    def contact_detail(detail_xpath):
        detail = result.xpath(detail_xpath)
        return detail[0].strip(" ") if detail != [] else ""  # Will be [] if the xpath is bad

    business_name = ".//a[@class='business-name']//text()"
    primary_phone = ".//*[@class='phones phone primary']//text()"
    street_address = ".//*[@class='street-address']//text()"
    locality = ".//*[@class='locality']//text()"
    # TODO: Fix that sometimes region is avail and not parsed, but zipcode fills in the region
    region = ".//*[@class='adr']/span[3]//text()"
    postal_code = ".//*[@class='adr']/span[4]//text()"
    website = ".//*[@class='links']//a[contains(@class,'website')]/@href"

    # TODO: Use k:v pairs to prevent record ordering issues
    elements = [business_name, primary_phone, street_address, locality, region, postal_code, website]

    contact_details = [contact_detail(detail_xpath) for detail_xpath in elements]

    # Remove trailing ",\xa0" after city name when only city is in locality
    # Unconfirmed if this can happen when region and postal code fields are blank
    contact_details[3] = contact_details[3].split(",")[0]

    # If we can't get region and postal_code, that info might be in locality
    if not contact_details[4] and not contact_details[5]:
        try:
            contact_details[3], contact_details[4], contact_details[5] = [
                i.rstrip(",") for i in contact_details[3].rsplit(" ", 2)]
        except ValueError:
            pass

    return models.Records(*contact_details)


# Main program
def run_scrape(search_term, search_location):
    # locate user agents and proxies files
    resource_path = os.path.join(app.root_path, 'static')

    # Import proxies and user agents files as lists and select initial proxy and user agent
    proxies_list = load_proxies(os.path.join(resource_path, 'proxies.txt'))
    uas_list = load_uas(os.path.join(resource_path, 'user_agents.txt'))

    scraped_results = []
    i = 0
    while True:
        i += 1
        url = build_url(search_term, search_location, i)
        proxy = {"http": next_proxy(proxies_list)}  # loads random proxy
        ua = next_ua(uas_list)  # loads random user-agent
        print(i, url, proxy, ua)  # to visual progress for back-end logs
        header = {
            "Connection": "close",  # cover tracks
            "User-Agent": ua}  # http://webaim.org/blog/user-agent-string-history/
        response = get_page(url, header, proxy, proxies_list)
        if response:
            parser = html.fromstring(response.text)
            parser.make_links_absolute(url)
            search_results_xpath = "//div[@class='search-results organic']//div[@class='v-card']"
            search_results = parser.xpath(search_results_xpath)
            next_page = parser.xpath(".//a[@class='next ajax-page']/@href")
        else:
            search_results = None

        if search_results:
            scraped_results += [parse_contact_info(result) for result in search_results]
        elif i == 1:
            print("No results found.")
            break
        else:
            db.session.bulk_save_objects(scraped_results)
            db.session.commit()
            print("Unable to find any more records. Either:\n"
                  "  1) there were genuinely no search results, or\n"
                  "  1) there were genuinely no more search results, or\n"
                  "  2) the webpage failed to load additional records. \n\n"
                  "If you believe there should have been more results, please rerun this State later.")
            break

        if not next_page:
            db.session.bulk_save_objects(scraped_results)
            db.session.commit()
            break


def get_results():
    query_all = [[getattr(curr, column.name)
                  for column in models.Records.__mapper__.columns]
                 for curr in models.Records.query.all()]
    if query_all:
        # csv.write requires StringIO
        file_like = StringIO()
        csv.writer(file_like).writerow(["Id", "Name", "Phone Number",
                                        "Address", "City", "State", "Zip Code", "Website"])
        csv.writer(file_like).writerows(query_all)

        # send_file requires BytesIO()
        output_csv = BytesIO()
        output_csv.write(file_like.getvalue().encode('ascii', 'ignore'))  # utf-8 leaves in Â
        output_csv.seek(0)
        file_like.close()

        return output_csv
    else:
        return 'No results found'
