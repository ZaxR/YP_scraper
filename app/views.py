"""Test."""
import datetime
import hashlib
import re

from flask import request, render_template, session, flash, redirect, url_for, jsonify
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse

from app import app, db, models
from app.forms import LoginForm, ScrapeForm
from app.tasks import long_task, long_task_test, send_async_email


def scrub_parameters(search_terms, search_locations):
    for c, term_group in enumerate(search_terms):
        search_terms[c] = list(set([i.strip() for i in re.split('[;]+', re.sub('[^a-zA-Z0-9; ]', '', term_group))]))

    for c, loc_group in enumerate(search_locations):
        search_locations[c] = list(set([i.strip() for i in re.split('[;]+', re.sub('[^a-zA-Z0-9;, ]', '', loc_group))]))

    for c, loc_list in enumerate(search_locations):
        for c2, loc in enumerate(loc_list):
            if loc == 'ALL':
                search_locations[c] = ['AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA', 'HI',
                                       'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD', 'MA', 'MI',
                                       'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ', 'NM', 'NY', 'NC',
                                       'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC', 'SD', 'TN', 'TX', 'UT',
                                       'VT', 'VA', 'WA', 'WV', 'WI', 'WY']

    return search_terms, search_locations


def generate_task_id(*args):
    """Generates a hash of the current datetime and any args to be used as a task_id."""
    current_dt = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    to_hash = "".join([current_dt] + [str(arg) for arg in args])
    task_id = int(hashlib.sha512(to_hash.encode('utf-8')).hexdigest(), 16) % 10**8

    return str(task_id)


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ScrapeForm(request.form)
    if request.method == 'POST':  # form.validate_on_submit():
        # models.Records.__table__.drop(db.session.bind, checkfirst=True)
        # models.Records.__table__.create(db.session.bind, checkfirst=True)

        # get raw input
        search_terms = request.form.getlist('search_terms')
        search_locations = request.form.getlist('search_locations')

        # takes semicolon-separated terms and semicolon-separated locations
        search_terms, search_locations = scrub_parameters(search_terms, search_locations)

        # Custom validation until wtforms with FieldList solution found
        # todo give more specific flash output. Auto-delete blank rows?
        for g in [search_terms, search_locations]:
            for s in g:
                for i in s:
                    if i == '':
                        flash('All fields for created rows are required. Please delete any blank rows and try again.', category='danger')
                        return render_template('index.html', form=form)

        # long running stuff call goes here
        task_id = generate_task_id(search_terms, search_locations)
        kwargs = {"recipient": request.form.get("recipient"),
                  "search_terms": search_terms,
                  "search_locations": search_locations}

        task = long_task_test.apply_async(kwargs=kwargs, task_id=task_id)  # task_id must be a string
        flash('Starting scrape...')
        # flash(f"To see scrape progress, visit https://yp-scraper.herokuapp.com/status/{task.id}")
        # return redirect(url_for('index'))
        # return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    return render_template('index.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('Invalid username or password')
            return redirect(url_for('login'))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


@app.route('/logout')
def logout():
    logout_user()

    return redirect(url_for('index'))


# @app.route('/longtask', methods=['POST'])
# def longtask():
#     task = long_task.apply_async()
#     return jsonify({}), 202, {'Location': url_for('taskstatus',
#                                                   task_id=task.id)}


# @app.route('/status/<task_id>')
# def taskstatus(task_id):
#     task = long_task.AsyncResult(task_id)
#     if task.state == 'PENDING':
#         response = {
#             'state': task.state,
#             'current': 0,
#             'total': 1,
#             'status': 'Pending...'
#         }
#     elif task.state != 'FAILURE':
#         response = {
#             'state': task.state,
#             'current': task.info.get('current', 0),
#             'total': task.info.get('total', 1),
#             'status': task.info.get('status', '')
#         }
#         if 'result' in task.info:
#             response['result'] = task.info['result']
#     else:
#         # something went wrong in the background job
#         response = {
#             'state': task.state,
#             'current': 1,
#             'total': 1,
#             'status': str(task.info),  # this is the exception raised
#         }
#     return jsonify(response)
