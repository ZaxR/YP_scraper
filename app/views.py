"""Test."""
import datetime
import hashlib

from flask import request, render_template, flash, redirect, url_for
from flask_login import current_user, login_user, logout_user
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


@app.route('/', methods=['GET', 'POST'])
def index():
    form = ScrapeForm(request.form)
    if request.method == 'POST':
        if not current_user.is_authenticated:
            flash('Please log in to finish submitting your request.', category='warning')
            return redirect(url_for('login', next=request.url))

        if form.validate():
            search_term = request.form.get('search_term')
            search_location = request.form.get('search_location')
            recipient_emails = request.form.get("recipient_emails").strip().split(",")

            kwargs = {"user": current_user.get_id(),
                      "search_term": search_term,
                      "search_location": search_location,
                      "recipient_emails": recipient_emails}

            # Celery task
            task_id = generate_task_id(search_term, search_location)
            task = long_task_test.apply_async(kwargs=kwargs, task_id=task_id)  # task_id must be a string
            flash('Starting scrape...', category='success')
            # flash(f"To see scrape progress, visit https://yp-scraper.herokuapp.com/status/{task.id}")
            # return redirect(url_for('index'))
            # return jsonify({}), 202, {'Location': url_for('taskstatus', task_id=task.id)}
        else:
            flash("Bad validation")

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


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        flash("You're already logged in, silly.", category='info')
        return redirect(url_for('index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = models.User.query.filter_by(username=form.username.data).first()
        if user is None or not user.verify_password(form.password.data):
            flash('Invalid username or password', category='danger')
            return redirect(url_for('login', next=request.args.get('next')))
        login_user(user, remember=form.remember_me.data)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('index')
        flash(f'Welcome, {user}!', category='success')
        return redirect(next_page)

    return render_template('login.html', title='Sign In', form=form)


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
