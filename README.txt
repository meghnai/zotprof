HOW TO RUN PROGRAM:
1) cd into inf-133-final-project folder
2) from terminal, run "python myScraper.py"


REQUIREMENTS CHANGE:
We realized calculating the "average grade received" was too subjective.
If 1 person got an A, and one person got a D, would the average grade be 
a B or a C? Instead we opted to take the mode, and display the most 
commonly received grade. 


ADDED FEATURES:
-> Calculating average quality/difficulty will also display how many ratings 
   it is out of
-> Can delete and clear all cards
-> Even after creating multiple cards, can go back to a previous card and 
   change the course for that professor, and it will recalculate averages
-> Cached course lists, ratings, and professor names to optimize the speed of
   calculation over time, using JSON files
-> Previously searched for professors by any user will go into the cache, 
   and appear in the searchbar dropdown. These cached professors will be
   suggested as the user types in the searchbar.  


CODE FROM EXTERNAL SOURCE
-> Code for the getTid() function was copied from yiyangl6@asu.edu 's 
public RateMyProfessorAPI on GitHub: 
https://github.com/remiliacn/RateMyProfessorPy/blob/master/RMPClass.py


REFERENCES AND SOURCES
-> https://www.ratemyprofessors.com
-> https://www.ratemyprofessors.com/paginate/professors/ (for parsing data)
-> regex101.com (for building regex expressions)
-> https://www.youtube.com/watch?v=hAEJajltHxc&t=939s&ab_channel=PrettyPrinted 
(for processing request data from Flask)
-> https://stackoverflow.com/questions/45699660/jinja2-reverse-a-list
(putting cards in order from most recentlt added)
-> https://stackoverflow.com/questions/32019733/getting-value-from-select-tag-using-flask
(getting form value from POST requests)
-> https://stackoverflow.com/questions/53382746/scrape-data-with-load-more-button-from-ratemyprofessor
(explained how to get info from RMP)
-> https://stackoverflow.com/questions/24153519/how-to-read-html-from-a-url-in-python-3
(reading HTML from a url)
-> https://jinja.palletsprojects.com/en/2.11.x/templates/
(using python flask)
-> https://fonts.google.com/specimen/Lato
(source for Lato, the Google Font used)
-> https://getbootstrap.com/
(source for bootstrap for responsiveness)
-> https://fontawesome.com/
(source for plus and trash icons for add and delete buttons)