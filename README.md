# YP_scraper 

<img src="https://github.com/ZaxR/YP_scraper/blob/master/app/static/img/yp-scraper-screenshotv2.png" width="100%">

YP_scraper is a Yellow Pages scraper webapp. It's built on Flask, with scraping via requests and lxml, and tasks being handled by Redis and Celery. Each request uses a random proxy and user-agent. Results are output as csvs, for local download or e-mail. 

A hosted version of the project can be found at https://yp-scraper.herokuapp.com/

### Running locally
1. Create a .env file. This file must have the following definitions:
```
REDIS_URL=redis://redis:6379/0
MAIL_USERNAME=your_email@domain.com
MAIL_PASSWORD=your_password
```

2. Build/run all services:
```docker-compose up --build```


### Running on Heroku

Heroku will read the heroku.yml file on deploying from this repo. To securely store the env vars/secrets in .env, Heroku has "Config Vars" that you can configure through the heroku cli or the UI.

Navigate to https://dashboard.heroku.com/apps/what_you_name_the_app/settings . Click "Reveal Config Vars" and manually enter the key=value pairs as are in the .env for running locally.