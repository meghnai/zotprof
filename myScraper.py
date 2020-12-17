# IMPORTANT: Code for getting the tid from the url (beginning of parse() function) was copied from yiyangl6@asu.edu 's public RateMyProfessorAPI on GitHub: 
# https://github.com/remiliacn/RateMyProfessorPy/blob/master/RMPClass.py

import re, requests
from lxml import etree
import logging
import urllib.request
import json
from flask import Flask, render_template, request
import math

app = Flask(__name__)

# global variables to put in the HTML
teacherName = "Baldwin, Mark"
courses = []
count = 0     # keeps track of profCards
course = ""
professors = {}     # dropdown suggestions professors

# variables to keep track of cards
teachers = ["Professor"]
qualities = ["-"]
difficulties = ["-"]
totals = ["-"]
course_lists = [["-----"]]
chosens = ["-"]     # the chosen class for each card
d_displays = ["none"]   # whether to display the course dropdown
t_displays = ["none"]   # whether to display the chosen course
hide_card = ["none"]    # will be none when delete button pressed

@app.route('/', methods=['GET', 'POST'])
def home():
    global teacherName, courses, course, count, teachers

    # searching for teacher -> loads course dropdown
    if request.method == 'POST':
        print("searchbar POST")

        teacherName = request.form.get('searchbar') # gets the teacher inputted in search bar
        count += 1  # count keeps track of the cards, also = id
        hide_card.append("inline-block")    # pre-deletion, card display is inline-block

        # append - as placeholders before class is selected
        qualities.append("—")
        difficulties.append("—")
        totals.append("—")

        tid = getTid(teacherName)
        # if prof not found, show not found message on the card
        if tid == -1:
            teachers.append("'" + teacherName + "' not found on RMP. Please try again.")
            course_lists.append([])
            d_displays[count] = "none"
            return render_template("index.html", teachers=teachers, count=count, qualities=qualities, difficulties=difficulties, course_lists=course_lists, d_displays=d_displays, t_displays=t_displays, chosens=chosens, professors=professors, totals=totals, hide_card=hide_card)


        teachers.append(teacherName)
        courses = loadCourses(tid, teacherName)    # get the courses for this teacher
        course_lists.append(courses)
        
        print("courses:", courses)
        print("course_lists:", course_lists)
        return render_template("index.html", teachers=teachers, count=count, qualities=qualities, difficulties=difficulties, course_lists=course_lists, d_displays=d_displays, t_displays=t_displays, chosens=chosens, professors=professors, totals=totals, hide_card=hide_card)
        
    else:
        print("ELSE")
        return render_template("index.html", teachers=teachers, count=count, qualities=qualities, difficulties=difficulties, course_lists=course_lists, d_displays=d_displays, t_displays=t_displays, chosens=chosens, professors=professors, totals=totals, hide_card=hide_card)


# function to delete a card
@app.route('/delete', methods=['POST'])
def delete_card():
    if request.method == 'POST':
        id = request.form.get('id')
        hide_card[int(id)] = "none"
        return render_template("index.html", teachers=teachers, count=count, qualities=qualities, difficulties=difficulties, course_lists=course_lists, d_displays=d_displays, t_displays=t_displays, chosens=chosens, professors=professors, totals=totals, hide_card=hide_card)

# function for getting ratings for selected class
@app.route('/<id>', methods=['POST'])
def select_class(id):
    print("select_class()")
    print("id: ", id)

    id = int(id)

    # get the chosen course and course list for this card
    courses = course_lists[id]
    course = request.form.get('course_dropdown')    # get selected course
    # chosens.append("")
    # chosens[id] = course

    # get the teacher at this card id
    teacherName = teachers[id]

    # get ratings
    ratings = parse(teacherName, course)
    qual = ratings["quality"]
    diff = ratings["difficulty"]
    total = ratings["total"]

    # put ratings in their respective lists by id for card rendering
    qualities[id] = qual
    difficulties[id] = diff
    totals[id] = total

    # move course to front of courses for the dropdown display
    courses.remove(course)
    courses.insert(0, course)
    course_lists[id] = courses

    return render_template("index.html", teachers=teachers, count=count, qualities=qualities, difficulties=difficulties, course_lists=course_lists, d_displays=d_displays, t_displays=t_displays, chosens=chosens, professors=professors, totals=totals, hide_card=hide_card)
 

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

# global dictionary where { key=professor : value=professor's courses }
# prevent having to call get_courses() more than once for a professor
uci_prof = {}

# global dict keeps track of ratings
# ratings = {"professor": {"course": [quality, difficulty]}}
# ratings = {}
ratings2 = {}

# returns the tid of a teacher
def getTid(teacherName, schoolId=1074):
    url = "https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&" \
                  "queryBy=teacherName&schoolName=University+of+California+Irvine&schoolID=%s&query=" % schoolId + teacherName
    print(url)

    page = requests.get(url=url, headers=headers)
    pageData = page.text
    # print(self.pageData)

    pageDataTemp = re.findall(r'ShowRatings\.jsp\?tid=\d+', pageData)

    if len(pageDataTemp) > 0:
        # GETTING THE TID
        pageDataTemp = re.findall(r'ShowRatings\.jsp\?tid=\d+', pageData)[0]
        tid_location = pageDataTemp.find("tid=")
        tid = pageDataTemp[tid_location:]
        
        print(tid)
        return tid
    
    print("ERROR: tid not found")
    return -1
    # raise ValueError

# if courses not in uci_prof, call getCourses()
# else return uci_prof[teacherName]
def loadCourses(tid, teacherName):
    # global uci_prof
    courses = []
    
    # load global dictionary of professor's courses from JSON file into uci_prof
    with open('my_dict.json') as f:
        uci_prof = json.load(f)

    preUrl = "https://www.ratemyprofessors.com/paginate/professors/ratings?" + tid
    print("preUrl:", preUrl)

    if teacherName not in uci_prof:
        # print(teacherName + " not in uci_prof dict")
        courses = getCourses(preUrl)
        uci_prof[teacherName] = courses
        # print("obtaining courses:", courses)
    else:
        courses = uci_prof[teacherName]
        # print("courses alr obtained:", courses)

    # dump current uci_prof dict into the permanent dict
    with open('my_dict.json', 'w') as f:
        json.dump(uci_prof, f)

    # print("updated uci_prof:", uci_prof)

    return courses

# returns the list of courses this professor has listed on RMP
def getCourses(url):
    # list to return
    courses= []

    # get the content of the page
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    html_str = mybytes.decode("utf8")
    fp.close()

    # loop thru each page
    page_num = 1
    while(len(html_str) > 28):
        course_tags = re.findall('"rClass":"[A-Za-z0-9]*"', html_str)

        for c in course_tags:
            course = c.replace('"rClass":"', '')
            course = course.replace('"', '')

            if course not in courses:
                courses.append(course)

        # get the content of the next page
        page_num += 1
        fp = urllib.request.urlopen(url + "&page=" + str(page_num))
        mybytes = fp.read()
        html_str = mybytes.decode("utf8")
        fp.close()

    # print("courses:", courses)
    return courses

# TESTING NEW VERSION
# def getCourses(url):
#     # dict to return
#     courses= {}

#     # get the content of the page
#     fp = urllib.request.urlopen(url)
#     mybytes = fp.read()
#     html_str = mybytes.decode("utf8")
#     fp.close()

#     # loop thru each page
#     page_num = 1
#     while(len(html_str) > 28):
#         course_tags = re.findall('"rClass":"[A-Za-z0-9]*"', html_str)

#         for c in course_tags:
#             course = c.replace('"rClass":"', '')
#             course = course.replace('"', '')

#             if course not in courses:
#                 courses[course] = None

#         # get the content of the next page
#         page_num += 1
#         fp = urllib.request.urlopen(url + "&page=" + str(page_num))
#         mybytes = fp.read()
#         html_str = mybytes.decode("utf8")
#         fp.close()

#     # print("courses:", courses)
#     return courses


# gets the total quality rating & num of ratings of a certain page by looking for quality tags in the input string
def quality_total(html_str, course, alt):
    quality_rating = 0
    quality_num = 0

    # get all quality tags
    quality = re.findall('"quality":"[a-bA-z]*"', html_str)
    if alt:
        alt_str = '"quality":"[a-zA-z]*","rClarity":[0-9],"rClass":"' + course + '"'
        quality = re.findall(alt_str, html_str)

    for q in quality:
        adjective = q.replace('"quality":"', '')
        adjective = adjective.replace('"', '')
        if alt:
            index = adjective.find(',rClarity')
            adjective = adjective[:index]
            # print(adjective[:index])

        if adjective == "awful":
            quality_rating += 1
        elif adjective == "poor":
            quality_rating += 2
        elif adjective == "average":
            quality_rating += 3
        elif adjective == "good":
            quality_rating += 4
        elif adjective == "awesome":
            quality_rating += 5
        
        quality_num += 1

    return (quality_rating, quality_num)


# gets the total difficulty rating & num of ratings of a certain page by looking for difficulty tags in the input string
def difficulty_total(html_str, course, alt):
    difficulty_rating = 0
    difficulty_num = 0

    # get all difficulty tags
    difficulty = re.findall('"rEasy":[0-9].[0-9]', html_str)
    if alt:
        courses = re.findall('"rClass":"[A-Za-z0-9]*"', html_str)

    for i in range(len(difficulty)):
        num = difficulty[i].replace('"rEasy":', '')

        if alt:
            c = courses[i].replace('"rClass":"', '')
            c = c.replace('"', '')
            if c == course:
                difficulty_rating += float(num)
                difficulty_num += 1
        else:
            difficulty_rating += float(num)
            difficulty_num += 1

        # print(num, c)


    # print(difficulty_rating, difficulty_num)
    return (difficulty_rating, difficulty_num)


# returns the most common grade received out of A, B, C, D, F
def grade_mode(html_str):
    a = b = c = d = f = 0

    # get all grade tags
    grades = re.findall('"teacherGrade":"[A-Z][+-]?"', html_str)

    for g in grades:
        letter = g.replace('"teacherGrade":"', '')
        letter = letter.replace('"', '')

        if letter in ["A+", "A", "A-"]: a += 1
        if letter in ["B+", "B", "B-"]: b += 1
        if letter in ["C+", "C", "C-"]: c += 1
        if letter in ["D+", "D", "D-"]: d += 1
        if letter == "F": f += 1

    # print([a,b,c,d,f])
    return [a,b,c,d,f]

# prints the average quality and difficulty of teacher for course
def getRatings(html_str, course, alt, finalUrl, altUrl, prof):

    # CHECK if the rating has already been calculated once
    with open('ratings2.json') as f:
        ratings2 = json.load(f)

    if prof in ratings2:
        print("ratings2[prof]:", ratings2[prof])
        if course in ratings2[prof]:
            print("ratings2[prof][course]:", ratings2[prof][course])
            return {"quality": ratings2[prof][course][0], "difficulty": ratings2[prof][course][1], "total": ratings2[prof][course][2]}
        else:
            print("course not in ratings2[prof]")
    else:
        print("prof not in ratings2.json")


    # ---DEFINE VARIABLES---
    # Calculating average quality and average difficulty
    quality_rating = quality_num = difficulty_rating = difficulty_num = 0
    # for most common grade 
    # a = b = c = d = f = 0


    # need to loop thru and get info for every page
    # if len(html_str) == 28, there is no info on the page
    page_num = 1
    while(len(html_str) > 28):
        # AVG QUALITY SECTION: quality_total() function returns a tuple
        qual_tuple = quality_total(html_str, course, alt)
        quality_rating += qual_tuple[0]
        quality_num += qual_tuple[1]

        # AVG DIFFICULTY SECTION: difficulty_total() function returns a tuple
        diff_tuple = difficulty_total(html_str, course, alt)
        difficulty_rating += diff_tuple[0]
        difficulty_num += diff_tuple[1]

        # GRADE SECTION: not using for now. if do use, make sure to account for altUrl
        # grade_mode() returns [a, b, c, d, f] where each elem is the # of that grade received
        # grade_list = grade_mode(html_str); a += grade_list[0]; b += grade_list[1]; c += grade_list[2]; d += grade_list[3]; f += grade_list[4]

        # Get the content of the next page
        page_num += 1

        if not alt:
            fp = urllib.request.urlopen(finalUrl + "&page=" + str(page_num))
        else:
            fp = urllib.request.urlopen(altUrl + "&page=" + str(page_num))

        mybytes = fp.read()
        html_str = mybytes.decode("utf8")
        fp.close()


    quality_rating /= quality_num
    difficulty_rating /= difficulty_num
    quality_rating = round(quality_rating, 2)
    difficulty_rating = round(difficulty_rating, 2)
    print("avg quality:", quality_rating)
    print("avg difficulty:", difficulty_rating)
    # max_grade = ""; if max(a, b, c, d, f) == a: max_grade = "A"; if max(a, b, c, d, f) == b: max_grade = "B"; if max(a, b, c, d, f) == c: max_grade = "C"; if max(a, b, c, d, f) == d: max_grade = "D"; if max(a, b, c, d, f) == f: max_grade = "F"; print([a, b, c, d, f]); print("most common grade:", max_grade)

    # # PUT RATING IN THE DICT
    # if prof not in ratings:
    #     ratings[prof] = {}
    # ratings[prof][course] = [quality_rating, difficulty_rating]

    # # dump current ratings dict into the permanent dict
    # with open('ratings.json', 'w') as f:
    #     json.dump(ratings, f)

    # PUT RATING IN THE DICT
    if prof not in ratings2:
        ratings2[prof] = {}
    ratings2[prof][course] = [quality_rating, difficulty_rating, quality_num]

    # dump current ratings2 dict into the permanent dict
    with open('ratings2.json', 'w') as f:
        json.dump(ratings2, f)

    return {"quality": quality_rating, "difficulty": difficulty_rating, "total": quality_num}



def parse(teacherName, course, schoolId=1074):
    # GET TID
    tid = getTid(teacherName, schoolId)
    print(tid)
    if(tid == -1):
        return {"quality": "Not found", "difficulty": "Not found"}


    # GETTING THE COURSES
    # prob dont need to call this here?
    loadCourses(tid, teacherName)


    # GETTING THE URLs TO PARSE
    finalUrl = "https://www.ratemyprofessors.com/paginate/professors/ratings?" + tid + "&courseCode=" + course
    altUrl = "https://www.ratemyprofessors.com/paginate/professors/ratings?" + tid  # use when courseCode param gets an error (newer professors)
    alt = False     # set to true if we need to search for course too


    # GETTING THE PAGE CONTENT
    try:
        fp = urllib.request.urlopen(finalUrl)
        print(finalUrl)
    except:
        fp = urllib.request.urlopen(altUrl)
        print(altUrl)
        print("Error: Can't use course code to parse :(")
        alt = True

    mybytes = fp.read()
    html_str = mybytes.decode("utf8")
    fp.close()


    # GETTING THE RATINGS (AVG QUALITY & DIFFICULTY OF COURSE)
    return getRatings(html_str, course, alt, finalUrl, altUrl, teacherName)
            

if __name__ == "__main__":
    # professors uses the same my_dict {}, so only gets updated each time the app is run
    with open('my_dict.json') as f:
        professors = json.load(f)
        
    app.run(debug=True)
    # parse(teacherName="Ray Klefstad", course="CS141")
    # parse(teacherName="Richard Pattis", course="ICS33")
    # parse(teacherName="Jennifer Wong-Ma", course="ICS53")
    # parse(teacherName="Sandra Irani", course="ICS6D")
    # parse(teacherName="Phillip Sheu", course="CS122A")
    # parse(teacherName="Phillip Sheu", course="COMPS122A")
    # parse(teacherName="Pavan Kadandale", course="BIO98")
    # parse(teacherName="Kimberly Hermans", course="ICS32A")
    # parse(teacherName="Kimberly Hermans", course="ICS32A")
    # parse(teacherName="Michael Shindler", course="ICS46")
    # parse(teacherName="Alex Thornton", course="ICS46")

