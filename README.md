# YP_scraper  
Yellow Pages web scraper. Uses Python (requests and beautifulsoup) and outputs to csv. Uses random proxy and user-agent for each request.

### Planned Future Updates:
* Replace list of list data structure with a database
  * Add duplicate record handling
  * Add record counter
* Improve exception handling
* Improve proxy use
  * proxies should only be used until blocked
* Add GUI
  * Add selectors for keyword(s), location(s), field(s), proxy/user-agent sources, and csv save location
  * Add "Progress" visualization for current keyword, current location, records scraped, and time elapsed
  * Add task scheduler, start button, and stop button
* Freeze program as a .exe
