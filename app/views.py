"""Test."""
import datetime
import hashlib
from functools import wraps

from flask import current_app, flash, request, render_template, redirect, session, url_for
from flask_login import current_user, login_user, logout_user
from werkzeug.datastructures import MultiDict
from werkzeug.urls import url_parse

from app import app, db, models
from app.forms import LoginForm, RegistrationForm, ScrapeForm
from app.tasks import long_task_test


def generate_task_id(*args):
    """Generates a hash of the current datetime and any args to be used as a task_id."""
    current_dt = datetime.datetime.now().strftime("%Y%m%dT%H%M%S")
    to_hash = "".join([current_dt] + [str(arg) for arg in args])
    task_id = int(hashlib.sha512(to_hash.encode('utf-8')).hexdigest(), 16) % 10**8

    return str(task_id)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You're already logged in, silly.", category='info')
        return redirect(url_for('index'))
    form = LoginForm()

    next_url = request.args.get('next')
    method = request.args.get('method')

    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()

        # Check for valid user/pass combo
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid username or password', category='danger')
            return redirect(url_for('login', next=next_url, method=method))

        login_user(user, remember=form.remember_me.data)

        # Redirect properly
        if not next_url or url_parse(next_url).netloc != '':
            next_url = url_for('index')
        flash(f'Welcome, {user}!', category='success')
        # https://stackoverflow.com/questions/15473626/make-a-post-request-while-redirecting-in-flask
        code = 307 if method == "POST" else 302
        return redirect(next_url, code=code)  # right now always post

    return render_template('login.html', title='Sign In', form=form)


def login_required_submit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        # Auth disabled, already logged in, or GET. Implicitly assumes submit is "POST"
        if current_app.login_manager._login_disabled or current_user.is_authenticated or request.method == 'GET':
            return f(*args, **kwargs)

        # Store data before handling login
        session['form_data'] = request.form.to_dict(flat=False)
        session['form_path'] = request.path
        flash('Please log in to finish submitting your request.', category='warning')
        return redirect(url_for('login', next=request.url, method="POST"))
    return decorated


@app.route('/', methods=['GET', 'POST'])
@login_required_submit
def index():
    # Create form with stored data if available
    form = (ScrapeForm(MultiDict(session.pop('form_data')))
            if session.pop('form_path', None) == request.path
            else ScrapeForm())

    if form.validate_on_submit():
        search_term = form.search_term.data
        search_location = form.search_location.data
        recipient_emails = form.recipient_emails.data.strip().split(",")

        kwargs = {"user": current_user.get_id(),
                  "search_term": search_term,
                  "search_location": search_location,
                  "recipient_emails": recipient_emails}

        # Celery task
        task_id = generate_task_id(search_term, search_location)
        task = long_task_test.apply_async(kwargs=kwargs, task_id=task_id)  # task_id must be a string
        flash(f"Scrape started. Check the following e-mail inbox(es) shortly for the results: "
              f"{', '.join(recipient_emails)}.", category='success')
        # flash(f"To see scrape progress, visit https://yp-scraper.herokuapp.com/status/{task.id}")
        return redirect(url_for('index'))
        # return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}

    # Collect user's search history, if logged in
    search_history = []
    if current_user.is_authenticated:
        user_id = current_user.get_id()
        search_history = models.User.query.get(int(user_id)).history

    return render_template('index.html', form=form, search_history=search_history)


@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        flash("You're already a logged in user - you don't need to register, silly.", category='info')
        return redirect(url_for('index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = models.User(username=form.username.data, email=form.email.data)
        user.password = form.password.data
        db.session.add(user)
        db.session.commit()
        flash('Congratulations, you are now a registered user!', category='success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route('/logout')
def logout():
    if not current_user.is_authenticated:
        flash("You weren't even logged in, silly.", category='info')
    else:
        logout_user()
        flash("We'll miss you. The Yellow Pages won't.", category='info')
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
