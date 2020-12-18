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