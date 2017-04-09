import collections
import csv
import itertools
import random
import re
import sys
import time
import tkinter as tk
from tkinter import ttk


import requests
from bs4 import BeautifulSoup


class GUI(tk.Frame):
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry()
        self.root.wm_title("YP_scraper")

        tk.Frame.__init__(self, self.root)
        self.create_widgets()

    def create_widgets(self):

        # Widget set-up for Textbox to enter search terms
        self.searchframe = ttk.Labelframe(self.root, padding=(6, 8, 12, 12), text='Locations')
        self.searchframe.grid(column=0, columnspan=10, row=0, rowspan=10, sticky='nsew')

        self.search_terms_box = tk.Text(self.searchframe, width=30, height=15, wrap="word")
        self.search_terms_box.grid(column=0, row=0, columnspan=10)
        self.search_terms_box.insert('1.0', 'Enter search terms separated by commas here.')

        self.search_terms = tk.Button(self.root, text='Save', width=30, command=self.save_search)
        self.search_terms.grid(column=0, row=11, columnspan=10)

        # Widget set-up for locations to search
        self.search_locations = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI',
                                 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI',
                                 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC',
                                 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
                                 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
        self.checkboxes = []
        self.locations = {}

        self.locationframe = ttk.Labelframe(self.root, padding=(6, 6, 12, 12), text='Locations')
        self.locationframe.grid(column=11, columnspan=5, row=0, rowspan=10, sticky='nsew')

        self.create_locations()
        # todo Have all states toggled on by default

        select_all_locations = tk.Button(self.root, text='All', width=10, command=self.select_all)
        select_all_locations.grid(column=12, row=11)

        deselect_all_locations = tk.Button(self.root, text='None', width=10, command=self.deselect_all)
        deselect_all_locations.grid(column=14, row=11)

        # Widget set-up for proxies list button
        # todo loads the .txt (or creates one if there is none?)
        # todo allows to add (insert)/remove (delete?) proxies from scrollable listbox?


        # Widget set-up for messages from program
        # todo set up scrollable listbox?
        # todo alternatively, current term, location, time elapsed, progressbar

        # Widget set-up for Run button
        run_program = tk.Button(self.root, text='Run', height=8, width=20, bg='green', command=self.run_main)
        run_program.grid(column=16, row=3)

        # Widget set-up for Stop button
        # todo have run button become stop button
        stop_program = tk.Button(self.root, text='Stop', height=8, width=20, bg='dark red', command=self.stop_main)
        stop_program.grid(column=17, row=3)

        # Widget set-up for Progress section
        self.progressframe = ttk.Labelframe(self.root, padding=(6, 6, 12, 12), text='Progress')
        self.progressframe.grid(column=16, columnspan=2, row=5, rowspan=5, sticky='nsew')

        info = (u"Current Keyword", u"Current Location", u"Records Scraped",
                u"Time Elapsed", u"Percentage Complete")
        for i, item in enumerate(info):
            ttk.Label(self.progressframe, text=u"{0}: ".format(item)).grid(in_=self.progressframe, column=0, row=i, sticky='w')
        self.progressbar = ttk.Progressbar(self.progressframe, orient="horizontal", length=200, mode="indeterminate").grid(column=1, row=4)

    def save_search(self):  # todo if no search term is saved, TypeError: Can't convert 'int' object to str implicitly
        raw_search_terms = self.search_terms_box.get('1.0', 'end-1c')
        self.search_terms = re.split(",[ ]*", re.sub("\n", '', re.sub(' +', ' ', raw_search_terms)))
        print('Search terms set to: {0}'.format(self.search_terms))
        return self.search_terms

    def create_locations(self, c=10, r=0):
        for index, item in enumerate(self.search_locations):
            r += 1
            if index > 0 and index % 10 == 0:
                c += 1
                r -= 10
            self.var = tk.IntVar()
            self.checkboxes.append(tk.Checkbutton(self.locationframe, text=item, variable=self.var,
                                                  command=lambda item=item, var=self.var: self.get_checkbox_value(item, var)))
            self.checkboxes[index].grid(column=c, row=r)

    def get_checkbox_value(self, state_name, var_value):
        if var_value.get() == 1:
            self.locations[state_name] = var_value.get()
        elif var_value.get() == 0:
            self.locations.pop(state_name, 0)

    def select_all(self):
        for location in self.search_locations:
            self.locations[location] = 1
        for checkbox in self.checkboxes:
            checkbox.select()

    def deselect_all(self):
        for location in self.search_locations:
            self.locations.pop(location, 0)
        for checkbox in self.checkboxes:
            checkbox.deselect()

    def run_main(self):
        if not isinstance(self.search_terms, (tuple,list)):
            print('Please enter search term(s) and click "save" before running.')
            return
        self.locations = collections.OrderedDict(sorted(self.locations.items()))
        print('Searching the following: \n'
              'Terms:{0} \nLocations:{1}'.format(self.search_terms,[k for k in self.locations]))
        Scraper(self.search_terms, self.locations)

    def stop_main(self):
        pass

    def start(self):
        print('Welcome to YP_scraper!')
        self.root.mainloop()


class Scraper:
    def __init__(self, search_terms, locations):
        self.search_terms = search_terms
        self.locations = locations

        # Search criteria
        self.user_agents_file = 'user_agents.txt'  # user-agent txt file path as string
        self.proxies_file = 'proxies.txt'  # proxies txt file path as string

        self.main(self.search_terms, self.locations)

    # Turns list of lists into csv file
    def write_to_csv(self, search_term, search_location, answer_list):  # todo handle PermissionError when file locked
        file_name = "YP_" + search_term + "_" + search_location + ".csv"
        csv_columns = ['Name', 'Phone Number', 'Street Address', 'City', 'State', 'Zip Code', 'Website']
        with open(file_name, 'w') as csv_file:
            writer = csv.writer(csv_file, lineterminator='\n')
            writer.writerow(csv_columns)
            writer.writerows(answer_list)
        print(search_location + " " + search_term + " " + "complete.")

    # Initial loading of proxies from file
    def load_proxies(self, proxies_file):  # todo add default value
        """
        proxies_file : string
            path to text file of proxies, one per line
        """
        with open(proxies_file, 'rb') as proxies:
            return [proxy.strip() for proxy in proxies.readlines() if proxy]

    # Pulls new random proxy from the list
    def next_proxy(self, proxies_list):  # todo improve to ensure the same IP isn't used twice in a row; do not run list in order
        return random.choice(proxies_list)

    # Initial loading of user agents from file
    def load_uas(self, user_agents_file):  # todo add default value
        """
        user_agents_file : string
            path to text file of user agents, one per line
        """
        with open(user_agents_file, 'rb') as uaf:
            return [ua.strip() for ua in uaf.readlines() if ua]

    # Pulls new random user agent from the list
    def next_ua(self, uas_list):
        return random.choice(uas_list)

    # Creates url from search criteria and current page
    def urls(self, search_term, location, page_number):
        template = (
            'http://www.yellowpages.com/search?search_terms={search_term}&geo_location_terms={location}&page={page_number}')
        return template.format(search_term=search_term, location=location, page_number=page_number)

    def pull_request(self, url, proxy, header, proxies_list):
        for _ in range(5):
            try:
                r = requests.get(url, headers=header, proxies=proxy, timeout=15)
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
            proxy = {"http": self.next_proxy(proxies_list)}  # loads random proxy
    #       # todo load random user-agent

        print('Ok, I give up.')
        sys.exit()

    # Finds all the contact information for a record
    def contact_info(self, record):
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
    def main(self, search_terms, search_locations):
        # Import proxies and user agents files as lists and select initial proxy and user agent
        proxies_list = self.load_proxies(self.proxies_file)
        uas_list = self.load_uas(self.user_agents_file)

        for search_term, search_location in itertools.product(search_terms, search_locations):
            answer_list = []
            i = 0
            while True:
                i += 1
                url = self.urls(search_term, search_location, i)
                proxy = {"http": self.next_proxy(proxies_list)}  # loads random proxy
                ua = self.next_ua(uas_list)  # loads random user-agent
                print(i, url, proxy, ua)  # to visual progress
                header = {
                    "Connection": "close",  # cover tracks
                    "User-Agent": ua}  # http://webaim.org/blog/user-agent-string-history/
                r = self.pull_request(url, header, proxy, proxies_list)  # runs requests.get
                soup = BeautifulSoup(r.text, "html.parser")
                search_results = soup.find(attrs={'class': 'search-results organic'})
                page_nav = soup.find(attrs={'class': 'pagination'})

                try:
                    records = search_results.find_all(attrs={'class': 'info'})
                except:  # todo narrow scope of exception
                    self.write_to_csv(search_term, search_location, answer_list)  # output data to csv file
                    print("Unable to find any more records. Either:\n"
                          "  1) there were geniunely no search results, or\n"
                          "  2) the webpage failed to load additional records. \n\n"
                          "If you believe there should have been more results, please rerun this State later.")

                answer_list += [self.contact_info(record) for record in records]

                if not page_nav.find(attrs={'class': 'next ajax-page'}):
                    self.write_to_csv(search_term, search_location, answer_list)  # output data to csv file
                    break

        print('\nSearches completed. You may now run another search or exit.')

if __name__ == '__main__':
    GUI().start()