import csv
import itertools
import os
import random
import requests
import sys
import time
from bs4 import BeautifulSoup
from flask import Flask, flash, redirect, render_template, request, send_file, url_for
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
        search_term = form.search_term.data
        search_location = form.search_location.data
        run_scrape(search_term, search_location)

        query = models.Records.query.all()
        query2 = [[getattr(curr, column.name) for column in models.Records.__mapper__.columns] for curr in query]
        output = StringIO()
        writer = csv.writer(output)
        csvfile = writer.writerows(query2)

        answer = BytesIO()
        answer.write(output.getvalue().encode('utf-8'))
        answer.seek(0)
        output.close()

        return send_file(answer,attachment_filename="YP_" + search_term + "_" + search_location + ".csv",
                         as_attachment=True, mimetype='text/csv')

    return render_template('index.html', form=form)

@app.route('/download_csv/', methods=['GET'])
def download_csv():
    # search_term, search_location = request.args.get('search_term', None), request.args.get('search_location', None)
    return send_file(os.path.join(app.root_path, 'YP_Cheese_IL.csv'), attachment_filename='Dicks', mimetype='text/csv')


# Turns list of lists into csv file
def write_to_csv(search_term, search_location, answer_list):  # todo handle PermissionError when file locked
    file_name = os.path.join(app.root_path, "YP_" + search_term + "_" + search_location + ".csv")
    csv_columns = ['Name', 'Phone Number', 'Street Address', 'City', 'State', 'Zip Code', 'Website']
    with open(file_name, 'w') as csv_file:
        writer = csv.writer(csv_file, lineterminator='\n')
        writer.writerow(csv_columns)
        writer.writerows(answer_list)
    print(search_location + " " + search_term + " " + "complete.")

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
            sys.exit()

        time.sleep(15)
        proxy = {"http": next_proxy(proxies_list)}  # loads random proxy
#       # todo load random user-agent

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

    return models.Records(*[contact_detail(attrs) for attrs in elements])

# Main program
def run_scrape(search_term, search_location):
    # Search criteria
    resource_path = os.path.join(app.root_path, 'static')

    user_agents_file = os.path.join(resource_path, 'user_agents.txt')  # 'user_agents.txt'  # user-agent txt file path as string
    proxies_file = os.path.join(resource_path, 'proxies.txt')  # proxies txt file path as string

    # Import proxies and user agents files as lists and select initial proxy and user agent
    proxies_list = load_proxies(proxies_file)
    uas_list = load_uas(user_agents_file)

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
        soup = BeautifulSoup(r.text, "html.parser")
        search_results = soup.find(attrs={'class': 'search-results organic'})
        page_nav = soup.find(attrs={'class': 'pagination'})

        try:
            records = search_results.find_all(attrs={'class': 'info'})
        except:  # todo narrow scope of exception
            db.session.bulk_save_objects(answer_list)
            db.session.commit()
            print("Last seach had a Nonetype error. Rerun this State later.")
            break

        answer_list += [contact_info(record) for record in records]

        if not page_nav.find(attrs={'class': 'next ajax-page'}):
            db.session.bulk_save_objects(answer_list)
            db.session.commit()
            break