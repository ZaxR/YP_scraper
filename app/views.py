import csv
import os
import random
import re
import requests
import time
from bs4 import BeautifulSoup
from datetime import date
from flask import flash, render_template, request, send_file, url_for
from flask_login import login_required
from io import StringIO, BytesIO


from app import app, db, models
from app.forms import ScrapeForm


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ScrapeForm(request.form)
    if form.validate_on_submit():
        models.Records.__table__.drop(db.session.bind, checkfirst=True)
        models.Records.__table__.create(db.session.bind, checkfirst=True)

        # takes comma separated terms and semicolon separated bunches (separated by commas) of locations
        search_terms, search_locations = scrub_parameters(form.search_terms.data, form.search_locations.data)
        for term, loc_list in zip(search_terms, search_locations):
            for loc in loc_list:
                # add search to search history
                db.session.add(models.SearchHistory(date.today(), term, loc, 'Anonymous'))  # todo update 'Anonymous to username if logged it
                db.session.commit()

                run_scrape(term, loc)

        # csv.write requires StringIO
        query_all = [[getattr(curr, column.name)
                      for column in models.Records.__mapper__.columns]
                     for curr in models.Records.query.all()]
        if query_all:
            file_like = StringIO()
            csv.writer(file_like).writerow(["Id", "Name", "Phone Number", "Address", "City", "State", "Zip Code", "Website"])
            csv.writer(file_like).writerows(query_all)

            # send_file requires BytesIO()
            output_csv = BytesIO()
            output_csv.write(file_like.getvalue().encode('ascii', 'ignore'))  # utf-8 leaves in Â
            output_csv.seek(0)
            file_like.close()

            fn_term = 'various_terms' if len(search_terms) > 1 else str(search_terms[0])
            fn_loc = 'various_locations' if len(search_locations) > 1 or len(search_locations[0]) > 1 else str(search_locations[0][0])

            return send_file(output_csv, attachment_filename="YP_" + fn_term + "_" + fn_loc + ".csv",
                             as_attachment=True, mimetype='text/csv')

        else:
            flash('No results found', category='info')

    elif request.method == 'POST':
        flash('All fields are required. Please try again.', category='danger')

    return render_template('index.html', form=form)


def scrub_parameters(search_terms, search_locations):
    search_terms = re.split('[, ]+', re.sub('[^a-zA-Z0-9, ]', '', search_terms))
    search_locations = [[re.sub('[^a-zA-Z0-9]', '', j) for j in i.split(',')] for i in search_locations.split(';')]
    for c, loc_list in enumerate(search_locations):
        for c2, loc in enumerate(loc_list):
            if loc == 'ALL':
                search_locations[c2] = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI',
                                       'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI',
                                       'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC',
                                       'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
                                       'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

    return search_terms, search_locations


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
def urls(search_term, location, page_number):
    template = (
        'http://www.yellowpages.com/search?search_terms={search_term}&geo_location_terms={location}&page={page_number}')
    return template.format(search_term=search_term, location=location, page_number=page_number)


def pull_request(url, proxy, header, proxies_list):
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
            return

        time.sleep(15)
        proxy = {"http": next_proxy(proxies_list)}  # loads random proxy
#       # todo load random user-agent

    print('Ok, I give up.')
    return


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

    return models.Records(*[contact_detail(attrs) for attrs in elements])


# Main program
def run_scrape(search_term, search_location):
    # locate user agents and proxies files
    resource_path = os.path.join(app.root_path, 'static')

    # Import proxies and user agents files as lists and select initial proxy and user agent
    proxies_list = load_proxies(os.path.join(resource_path, 'proxies.txt'))
    uas_list = load_uas(os.path.join(resource_path, 'user_agents.txt'))

    answer_list = []
    i = 0
    while True:
        i += 1
        url = urls(search_term, search_location, i)
        proxy = {"http": next_proxy(proxies_list)}  # loads random proxy
        ua = next_ua(uas_list)  # loads random user-agent
        print(i, url, proxy, ua)  # to visual progress
        header = {
            "Connection": "close",  # cover tracks
            "User-Agent": ua}  # http://webaim.org/blog/user-agent-string-history/
        r = pull_request(url, header, proxy, proxies_list)  # runs requests.get
        if r:
            soup = BeautifulSoup(r.text, "html.parser")
            search_results = soup.find(attrs={'class': 'search-results organic'})
            page_nav = soup.find(attrs={'class': 'pagination'})
        else:
            search_results = None

        if search_results:
            records = search_results.find_all(attrs={'class': 'info'})
            answer_list += [contact_info(record) for record in records]
        elif i == 1:
            print("No results found.")
            break
        else:
            db.session.bulk_save_objects(answer_list)
            db.session.commit()
            print("Unable to find any more records. Either:\n"
                  "  1) there were geniunely no search results, or\n"
                  "  1) there were geniunely no more search results, or\n"
                  "  2) the webpage failed to load additional records. \n\n"
                  "If you believe there should have been more results, please rerun this State later.")
            break

        if not page_nav.find(attrs={'class': 'next ajax-page'}):
            db.session.bulk_save_objects(answer_list)
            db.session.commit()
            break
