# YP_scraper  
Yellow Pages scraper webapp made with Flask, requests, and beautifulsoup. Outputs results to users as csvs. Uses random proxy and user-agent for each request.

### Known Bugs:
* Remove trailing ',' after city name; rstrip(',') not working
* Have website actually be the url and/or link
* Change wtform to dynamic number of inputs; update js

### Roadmap:
* Handle multiple search criteria with cities
* Display output to screen
* Update db record table clearing/csv outputting logic
   * Move download csv to a button?
* Deploy on Heroku

### Future Features:
* Add secure login/registration
* Have route to view most recent/search past searches
* Add logging
* Add visualization of progress (ajax)
* Add manual proxy selection (including add/delete)
* Optional e-mail results
* Choose save location of file
* Multithreading
* A "stop" button for active search
* Add a menu with a link to github, an about section, donate button?
