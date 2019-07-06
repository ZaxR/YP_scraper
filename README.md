# YP_scraper 

<img src="images/yp-scraper-screenshotv1.png" width="100%">

YP_scraper is a Yellow Pages scraper webapp. It's built on Flask, with scraping via requests and lxml, and tasks being handled by Redis and Celery. Each request uses a random proxy and user-agent. Results are output as csvs, for local download or e-mail. 

A hosted version of the project can be found at https://yp-scraper.herokuapp.com/
