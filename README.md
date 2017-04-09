# YP_scraper  
Yellow Pages web scraper. Uses Python (requests, beautifulsoup, tkinter) and outputs to csv. Uses random proxy and user-agent for each request.

### Roadmap:
* Improve GUI
  * Add stop button
  * Move output visualisation to widget
    * Design cleaner "Progress" visualization for current keyword, current location, records scraped, and time elapsed
  * Add widgets for selecting record fields, adding/removing proxies, and csv save location
  * Add output options: one file, one file per term, one file per term+location
  * Add task scheduler
* Add logging
  * Need a way to to recognize and rerun failed next page attempts
  * Need a way to gather data to analyze program weaknesses
* Improve proxy block detection and cycling
* Replace list of list data structure with a database
  * Need to remember last successful iteration prior to exception 
  * Add duplicate record handling
  * Add record counter
* Freeze program as an standalone executable -or- deploy as webapp
* Miscellaneous
  * Add handling for writing files when files can't be written (such as if a user already has the file in question open)

