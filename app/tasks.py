"""Test."""
import random
import time
from datetime import date

from flask_mail import Attachment, Message

from app import app, db, models, celery, mail
from app.scraper import run_scrape, get_results


@celery.task
def send_async_email(msgd):
    """Background task to send an email with Flask-Mail."""
    msg = Message(msgd.get('subject'),
                  sender=app.config['MAIL_DEFAULT_SENDER'],
                  recipients=msgd.get('recipients'),
                  body=msgd.get('body'),
                  attachments=msgd.get('attachments'))
    with app.app_context():
        mail.send(msg)


@celery.task(bind=True)
def long_task(self):
    """Background task that runs a long function with progress reports."""
    verb = ['Starting up', 'Booting', 'Repairing', 'Loading', 'Checking']
    adjective = ['master', 'radiant', 'silent', 'harmonic', 'fast']
    noun = ['solar array', 'particle reshaper', 'cosmic ray', 'orbiter', 'bit']
    message = ''
    total = random.randint(10, 50)
    for i in range(total):
        if not message or random.random() < 0.25:
            message = '{0} {1} {2}...'.format(random.choice(verb),
                                              random.choice(adjective),
                                              random.choice(noun))
        self.update_state(state='PROGRESS',
                          meta={'current': i, 'total': total,
                                'status': message})
        time.sleep(1)
    return {'current': 100, 'total': 100, 'status': 'Task completed!',
            'result': 42}


@celery.task(bind=True)
def long_task_test(self, recipient, search_terms, search_locations):
    search_combos = sum([1
                         for term_list, loc_list in zip(search_terms, search_locations)
                         for term in term_list
                         for loc in loc_list])

    for term_list, loc_list in zip(search_terms, search_locations):
        i = 0
        for term in term_list:
            for loc in loc_list:
                # add search to search history
                # todo update 'Anonymous to username if logged it
                db.session.add(models.SearchHistory(date.today(), term, loc, 'Anonymous'))
                db.session.commit()

                run_scrape(term, loc)
                i += 1
                self.update_state(state='PROGRESS',
                                  meta={'current': i, 'total': search_combos})

    results = get_results()

    fn_term = 'multi-term' if len(search_terms) > 1 else str(search_terms[0])
    fn_loc = 'multi-location' if len(search_locations) > 1 else str(search_locations[0])
    attachment_filename = "YP_" + fn_term + "_" + fn_loc + ".csv"

    content_type = 'text/csv'
    attachments = [Attachment(filename=attachment_filename, content_type=content_type, data=results.read())]
    recipients = [recipient]
    body = "tada"
    # body = (f"Attached are your results for the following search term/location combos: "
    #         f"{dict(zip(search_terms, search_locations))}")

    msgd = {"recipients": recipients, "subject": "Yellow Pages Scrape Results",
            "body": body, "attachments": attachments}

    send_async_email(msgd)
