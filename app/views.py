"""Test."""
import re

from flask import request, render_template, session, flash, redirect, \
    url_for, jsonify

from app import app, db, models
from app.forms import ScrapeForm
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


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ScrapeForm(request.form)
    if request.method == 'POST':  # form.validate_on_submit():
        models.Records.__table__.drop(db.session.bind, checkfirst=True)
        models.Records.__table__.create(db.session.bind, checkfirst=True)

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
        kwargs = {"recipient": request.form.get("recipient"),
                  "search_terms": search_terms,
                  "search_locations": search_locations}

        long_task_test.apply_async(kwargs=kwargs)
        flash('Starting scrape...')

    return render_template('index.html', form=form)


# @app.route('/', methods=['GET', 'POST'])
# def index():
#     if request.method == 'GET':
#         return render_template('index.html', email=session.get('email', ''))
#     # email = request.form['email']
#     # session['email'] = email

#     # subject = "Hello From Flask"
#     # msgd = {'to': request.form['email'], 'subject': subject}
#     # # send the email
#     if request.form['submit'] == "Start Long Calculation":
#         #     # send right away
#         #     send_async_email.delay(msgd)
#         flash('Start long running task')
#         # flash('Sending email to {0}'.format(email))
#     # else:
#     #     # send in one minute
#     #     send_async_email.apply_async(args=[msgd], countdown=60)
#     #     flash('An email will be sent to {0} in one minute'.format(email))

#     return redirect(url_for('index'))


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
