import csv
import itertools
import random
import sys
import time
import requests
from bs4 import BeautifulSoup

# Search criteria
user_agents_file = 'user_agents.txt' #user-agent txt file path as string
proxies_file = 'proxies.txt' #proxies txt file path as string
search_terms = ["Edible+Arrangements",]
search_locations = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS',
                    'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY',
                    'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
                    'WI', 'WY']

# Structure for Data
answer_list = [] #todo change to database
csv_columns = ['Name', 'Phone Number', 'Street Address', 'City', 'State', 'Zip Code', 'Website']

# Turns list of lists into csv file
def write_to_csv(csv_file, csv_columns, answer_list):
    with open(csv_file, 'w') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        writer.writerow(csv_columns)
        writer.writerows(answer_list)

#load the user agents
def load_user_agents(user_agents_file):
    """
    user_agents_file : string
        path to text file of user agents, one per line
    """
    with open(user_agents_file, 'rb') as uaf:
        uas = [ua.strip() for ua in uaf.readlines() if ua]
    return random.choice(uas)

#load proxies
def load_proxies(proxies_file):
    """
    proxies_file : string
        path to text file of proxies, one per line
    """
    with open(proxies_file, 'rb') as proxies:
        proxy_list = [proxy.strip() for proxy in proxies.readlines() if proxy]
    return random.choice(proxy_list)

# Creates url from search criteria and current page
def urls(search_term, location, page_number):
    template = 'http://www.yellowpages.com/search?search_terms={search_term}&geo_location_terms={location}&page={page_number}'
    return template.format(search_term=search_term, location=location, page_number=page_number)

def pull_request(url, proxy, headers):
    try:
        r = requests.get(url, headers=headers, proxies=proxy, timeout=15)
        status = r.status_code
        count = 0
        while status != 200:
            count += 1
            if count >= 5:
                print('Ok, I give up: ', status)
                sys.exit()
            print('Error: ', r.status_code, '. Trying again.')
            time.sleep(31)
            r = requests.get(url, headers=headers, proxies=proxy, timeout=5)
            status = r.status_code
        return r
    except requests.exceptions.Timeout as t:
        print('Uh oh: ', t)
        sys.exit()
    except requests.exceptions.RequestException as e:
        print('Uh oh: ', e)
        sys.exit()

# Finds all the contact information for a record
def contact_info(record):
    def contact_detail(attrs):
        detail = record.find(attrs=attrs)
        return detail.text if detail is not None else ""

    elements = [
        {'class': 'business-name'},
        {'class': 'phones phone primary'},
        {'class': 'street-address'},
        {'class': 'locality'},
        {'itemprop': 'addressRegion'},
        {'itemprop': 'postalCode'},
        {'class': 'links'},
    ]

    return [contact_detail(attrs) for attrs in elements]

# Main program
def main(answer_list):
    for search_term, search_location in itertools.product(search_terms, search_locations):
        i = 0
        while True:
            i += 1
            url = urls(search_term, search_location, i)
            print (i, url) #to visual progress
            proxy = {"http":load_proxies(proxies_file)} # loads proxies and selects random proxy
            ua = load_user_agents(user_agents_file)  # loads user-agents and selects a random user agent
            headers = {
                "Connection": "close",  #cover tracks
                "User-Agent": ua} # http://webaim.org/blog/user-agent-string-history/
            r = pull_request(url, headers, proxy) #runs requests.get
            soup = BeautifulSoup(r.text, "html.parser")
            main = soup.find(attrs={'class': 'search-results organic'})
            page_nav = soup.find(attrs={'class': 'pagination'})

            try:
                records = main.find_all(attrs={'class': 'info'})
            except:
                csv_file = "YP_" + search_term + "_" + search_location + ".csv"
                write_to_csv(csv_file, csv_columns, answer_list)  # output data to csv file
                print(search_location + " " + search_term + " " + "complete, but had a Nonetype error. Rerun this state later.")
                answer_list = []  # blank list for new term+location combo
                break

            answer_list += [contact_info(record) for record in records]

            if not page_nav.find(attrs={'class': 'next ajax-page'}):
                csv_file = "YP_" + search_term + "_" + search_location + ".csv"
                write_to_csv(csv_file, csv_columns, answer_list)  # output data to csv file
                print(search_location + " " + search_term + " " + "complete.")
                answer_list = [] #blank list for new term+location combo
                break

if __name__ == '__main__':
    main(answer_list)
