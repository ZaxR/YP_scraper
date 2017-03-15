import csv
import itertools
import random
import sys
import time
import requests
from bs4 import BeautifulSoup

# Turns list of lists into csv file
def write_to_csv(search_term, search_location, answer_list):
    file_name = "YP_" + search_term + "_" + search_location + ".csv"
    csv_columns = ['Name', 'Phone Number', 'Street Address', 'City', 'State', 'Zip Code', 'Website']
    with open(file_name, 'w') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        writer.writerow(csv_columns)
        writer.writerows(answer_list)
    print(search_location + " " + search_term + " " + "complete.")

#Initial loading of proxies from file
def load_proxies(proxies_file): #todo add default value
    """
    proxies_file : string
        path to text file of proxies, one per line
    """
    with open(proxies_file, 'rb') as proxies:
        proxies_list = [proxy.strip() for proxy in proxies.readlines() if proxy]
    return proxies_list

#Pulls new random proxy from the list
def next_proxy(proxies_list):
    return random.choice(proxies_list)

#Initial loading of user agents from file
def load_uas(uas_file): #todo add default value
    """
    user_agents_file : string
        path to text file of user agents, one per line
    """
    with open(uas_file, 'rb') as uaf:
        uas_list = [ua.strip() for ua in uaf.readlines() if ua]
    return uas_list

#Pulls new random user agent from the list
def next_ua(uas_list):
    return random.choice(uas_list)

# Creates url from search criteria and current page
def urls(search_term, location, page_number):
    template = 'http://www.yellowpages.com/search?search_terms={search_term}&geo_location_terms={location}&page={page_number}'
    return template.format(search_term=search_term, location=location, page_number=page_number)

def pull_request(url, proxy, headers):
    for _ in range(5):
        try:
            r = requests.get(url, headers=headers, proxies=proxy, timeout=15)
            if r.status_code != 200:
                raise requests.exceptions.HTTPError
            return r
        except requests.exceptions.HTTPError as h:
            print('Error: ', h.response.status_code, '. Trying again.')
        except requests.exceptions.Timeout as t:
            print('Uh oh: ', t, '. Retrying now.')
        except requests.exceptions.RequestException as e:
            print('Uh oh: ', e)
            sys.exit()

        time.sleep(15)
        proxies_list.remove(proxy["http"])  # todo check that this isn't the last proxy before removing
        proxy = {"http": next_proxy(proxies_list)}  # loads random proxy

    print('Ok, I give up.')
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
def main(proxy, ua):
    for search_term, search_location in itertools.product(search_terms, search_locations):
        answer_list = []
        i = 0
        while True:
            i += 1
            url = urls(search_term, search_location, i)
            proxy = {"http": next_proxy(proxies_list)}  # loads random proxy
            ua = next_ua(uas_list)  # loads random user-agent
            headers = {
                "Connection": "close",  #cover tracks
                "User-Agent": ua} # http://webaim.org/blog/user-agent-string-history/
            print(i, url, proxy, ua)  # to visual progress
            r = pull_request(url, headers, proxy) #runs requests.get
            soup = BeautifulSoup(r.text, "html.parser")
            search_results = soup.find(attrs={'class': 'search-results organic'})
            page_nav = soup.find(attrs={'class': 'pagination'})

            try:
                records = search_results.find_all(attrs={'class': 'info'})
            except:
                write_to_csv(search_term, search_location, answer_list)  # output data to csv file
                print("Last seach had a Nonetype error. Rerun this State later.")
                answer_list = []  # blank list for new term+location combo
                break

            answer_list += [contact_info(record) for record in records]

            if not page_nav.find(attrs={'class': 'next ajax-page'}):
                write_to_csv(search_term, search_location, answer_list)  # output data to csv file
                answer_list = [] #blank list for new term+location combo
                break

if __name__ == '__main__':
    # Search criteria
    user_agents_file = 'user_agents.txt'  # user-agent txt file path as string
    proxies_file = 'proxies.txt'  # proxies txt file path as string
    search_terms = ["Florist", ]
    search_locations = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS',
                        'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY',
                        'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
                        'WI', 'WY']

    #Import proxies and user agents files as lists and select initial proxy and user agent
    proxies_list = load_proxies(proxies_file)
    proxy = {"http": next_proxy(proxies_list)}  # loads random proxy

    uas_list = load_uas(user_agents_file)
    ua = next_ua(uas_list)  # loads random user-agent

    main(proxy, ua)
