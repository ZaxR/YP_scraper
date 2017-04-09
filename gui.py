import collections
import re
import tkinter as tk
from tkinter import ttk

import YP_scrape


class gui(tk.Frame):
    def __init__(self):
        self.root = tk.Tk()
        self.root.geometry()
        self.root.wm_title("YP_scraper")

        tk.Frame.__init__(self, self.root)
        self.create_widgets()

    def create_widgets(self):

        # Widget set-up for Textbox to enter search terms
        self.search_terms_box = tk.Text(self.root)  #, width=30, height=30
        self.search_terms_box.grid(column=0, row=1, columnspan=10, rowspan=10)
        self.search_terms_box.insert('1.0', 'Enter search terms separated by commas here.')

        self.search_terms = tk.Button(self.root, text='Save', command=self.save_search)
        self.search_terms.grid(column=0, row=11)

        # Widget set-up for locations to search
        self.search_locations = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI',
                                 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI',
                                 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC',
                                 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
                                 'VT', 'VA', 'WA', 'WV', 'WI', 'WY']
        self.checkboxes = []
        self.locations = {}
        self.create_locations()
        # todo Have all states toggled on by default

        select_all_locations = tk.Button(self.root, text='All', command=self.select_all)
        select_all_locations.grid(column=11, row=11)

        deselect_all_locations = tk.Button(self.root, text='None', command=self.deselect_all)
        deselect_all_locations.grid(column=12, row=11)

        # Widget set-up for proxies list button
        # loads the .txt (or creates one if there is none?)
        # allows to add (insert)/remove (delete?) proxies from scrollable listbox?


        # Widget set-up for messages from program
        # scrollable listbox?
        # alternatively, current term, location, time elapsed, progressbar

        # Widget set-up for Run button
        run_program = tk.Button(self.root, text='Run', command=self.run_main)
        run_program.grid(column=13, row=11)

        # Widget set-up for Stop button
        # have run button become stop button

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
            self.checkboxes.append(tk.Checkbutton(self.root, text=item, variable=self.var,
                                                  command=lambda item=item, var=self.var: self.get_checkbox_value(item, var)))
            self.checkboxes[index].grid(column=c, row=r)

    def get_checkbox_value(self, state_name , var_value):
        if var_value.get() == 1:
            self.locations[state_name] = var_value.get()
        elif var_value.get() == 0:
            self.locations.pop(state_name,0)

    def select_all(self):
        for location in self.search_locations:
            self.locations[location] = 1
        for checkbox in self.checkboxes:
            checkbox.select()

    def deselect_all(self):
        for location in self.search_locations:
            self.locations.pop(location,0)
        for checkbox in self.checkboxes:
            checkbox.deselect()

    def run_main(self):
        self.locations = collections.OrderedDict(sorted(self.locations.items()))
        print('Searching the following: \n Terms:{0} \n Locations:{1}'.format(self.search_terms,[k for k in self.locations]))
        YP_scrape.main(self.search_terms, self.locations)

    def start(self):
        print('Welcome to YP_scraper!')
        self.root.mainloop()


#if __name__ == "__main__":
gui().start()