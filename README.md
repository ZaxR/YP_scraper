# YP_scraper  
Yellow Pages scraper webapp made with Flask, requests, and beautifulsoup. Outputs results to users as csvs. Uses random proxy and user-agent for each request.

### Known Bugs:
* Remove trailing ',' after city name; rstrip(',') not working
* Have website actually be the url and/or link
* wtforms validation isn't working; temporarily using custom validation

### Roadmap:
* Improve custom validation
* Display output to screen
* Prettify
* Update file naming convention to prevent very long file names
* Prevent searches from exceeding memory/space; limit search terms/locations?
* Write tests

### Future Features:
* Add secure login/registration
  * Have route to view most recent/search past searches
  * Optional e-mail results? Or notification e-mail?
* Add visualization of progress (ajax)
* A "stop" button for active search
* Add logging
* Add manual proxy selection (including add/delete)
* Choose save location of file
* Multithreading
* Add a menu with a link to github, an about section, donate button?
