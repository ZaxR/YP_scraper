"""Test."""
from datetime import datetime

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
def long_task_test(self, user, recipient_emails, search_term, search_location):
    task_id = int(self.request.id.__str__())

    # add search to search history
    print(f"long_task_test task user: {user}")
    search_history = models.SearchHistory(timestamp=datetime.now(),
                                          term=search_term,
                                          location=search_location,
                                          user_id=user)
    db.session.add(search_history)
    db.session.commit()

    # TODO: Update current/total with page of search results
    self.update_state(state='PROGRESS', meta={'current': 0, 'total': 1})
    run_scrape(search_term=search_term, search_location=search_location, task_id=task_id)
    self.update_state(state='PROGRESS', meta={'current': 1, 'total': 1})

    results = get_results(task_id)

    attachments = []
    if results:
        attachment_filename = "YP_" + search_term + "_" + search_location + ".csv"
        content_type = 'text/csv'
        attachments.append(Attachment(filename=attachment_filename,
                                      content_type=content_type,
                                      data=results.read()))
        body = f"Attached are your scraped results for the term '{search_term}' for the location '{search_location}'."
    else:
        body = f"No results found for the term '{search_term}' for the location '{search_location}'."

    msgd = {"recipients": recipient_emails, "subject": "Yellow Pages Scrape Results",
            "body": body, "attachments": attachments}

    send_async_email(msgd)

    # temporarily delete records after they're emailed to save db space
    try:
        models.Records.query.filter_by(task_id=task_id).delete()
        db.session.commit()
    except:
        db.session.rollback()

    # return {'current': 100, 'total': 100, 'status': 'Task completed!',
    #         'result': 42}
