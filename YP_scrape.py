import requests
from bs4 import BeautifulSoup
import itertools
import csv

# Search criteria
search_terms = ["term1", "term2"]
search_locations = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI', 'ID', 'IL', 'IN', 'IA', 'KS',
                    'KY', 'LA', 'ME', 'MD', 'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY',
                    'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV',
                    'WI', 'WY']

# Structure for Data
answer_list = []
csv_columns = ['Name', 'Phone Number', 'Street Address', 'City', 'State', 'Zip Code', 'Website']


# Turns list of lists into csv file
def write_to_csv(csv_file, csv_columns, answer_list):
    with open(csv_file, 'w') as csvfile:
        writer = csv.writer(csvfile, lineterminator='\n')
        writer.writerow(csv_columns)
        writer.writerows(answer_list)


# Creates url from search criteria and current page
def url(search_term, location, page_number):
    template = 'http://www.yellowpages.com/search?search_terms={search_term}&geo_location_terms={location}&page={page_number}'
    return template.format(search_term=search_term, location=location, page_number=page_number)


# Finds all the contact information for a record
def find_contact_info(record):
    holder_list = []
    name = record.find(attrs={'class': 'business-name'})
    holder_list.append(name.text if name is not None else "")
    phone_number = record.find(attrs={'class': 'phones phone primary'})
    holder_list.append(phone_number.text if phone_number is not None else "")
    street_address = record.find(attrs={'class': 'street-address'})
    holder_list.append(street_address.text if street_address is not None else "")
    city = record.find(attrs={'class': 'locality'})
    holder_list.append(city.text if city is not None else "")
    state = record.find(attrs={'itemprop': 'addressRegion'})
    holder_list.append(state.text if state is not None else "")
    zip_code = record.find(attrs={'itemprop': 'postalCode'})
    holder_list.append(zip_code.text if zip_code is not None else "")
    website = record.find(attrs={'class': 'links'})
    holder_list.append(website.text if website is not None else "")  # todo capture url as opposed to text
    return holder_list


# Main program
def main():
    # todo add file explorer to pre-set folder for csvs
    for search_term, search_location in itertools.product(search_terms, search_locations):
        i = 0
        while True:
            i += 1
            # todo add pause to prevent being blocked by YP?
            url = url(search_term, search_location, i)
            r = requests.get(url)
            soup = BeautifulSoup(r.text, "html.parser")
            main = soup.find(attrs={'class': 'search-results organic'})
            page_nav = soup.find(attrs={'class': 'pagination'})
            records = main.find_all(attrs={'class': 'info'})
            for record in records:
                answer_list.append(find_contact_info(record))
            if not page_nav.find(attrs={'class': 'next ajax-page'}):
                csv_file = "YP_" + search_term + "_" + search_location + ".csv"
                write_to_csv(csv_file, csv_columns, answer_list)  # output data to csv file
                break


# todo create visual interface with a "run" button and an "edit search criteria" button
# todo freeze program as .exe

if __name__ == '__main__':
    main()