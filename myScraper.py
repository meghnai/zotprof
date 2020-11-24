# IMPORTANT: Code for getting the tid from the url (beginning of parse() function) was copied from yiyangl6@asu.edu 's public RateMyProfessorAPI on GitHub: 
# https://github.com/remiliacn/RateMyProfessorPy/blob/master/RMPClass.py

import re, requests
from lxml import etree
import logging
import urllib.request
import json
from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def home():
    return render_template("index.html")

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

# global dictionary where { key=professor : value=professor's courses }
# prevent having to call get_courses() more than once for a professor
uci_prof = {}


# returns the list of courses this professor has listed on RMP
def getCourses(url):
    # list to return
    courses= []

    # get the content of the page
    fp = urllib.request.urlopen(url)
    mybytes = fp.read()
    mystr = mybytes.decode("utf8")
    fp.close()

    # loop thru each page
    page_num = 1
    while(len(mystr) > 28):
        course_tags = re.findall('"rClass":"[A-Za-z0-9]*"', mystr)

        for c in course_tags:
            course = c.replace('"rClass":"', '')
            course = course.replace('"', '')

            if course not in courses:
                courses.append(course)

        # get the content of the next page
        page_num += 1
        fp = urllib.request.urlopen(url + "&page=" + str(page_num))
        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()

    print("courses:", courses)
    return courses


# gets the total quality rating & num of ratings of a certain page by looking for quality tags in the input string
def quality_total(mystr, course, alt):
    quality_rating = 0
    quality_num = 0

    # get all quality tags
    quality = re.findall('"quality":"[a-bA-z]*"', mystr)
    if alt:
        alt_str = '"quality":"[a-zA-z]*","rClarity":[0-9],"rClass":"' + course + '"'
        quality = re.findall(alt_str, mystr)

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
def difficulty_total(mystr, course, alt):
    difficulty_rating = 0
    difficulty_num = 0

    # get all difficulty tags
    difficulty = re.findall('"rEasy":[0-9].[0-9]', mystr)
    if alt:
        courses = re.findall('"rClass":"[A-Za-z0-9]*"', mystr)

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
def grade_mode(mystr):
    a = b = c = d = f = 0

    # get all grade tags
    grades = re.findall('"teacherGrade":"[A-Z][+-]?"', mystr)

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
def getRatings(mystr, course, alt, finalUrl, altUrl):
    # ---DEFINE VARIABLES---
    # Calculating average quality and average difficulty
    quality_rating = quality_num = difficulty_rating = difficulty_num = 0
    # for most common grade # a = b = c = d = f = 0


    # need to loop thru and get info for every page
    # if len(mystr) == 28, there is no info on the page
    page_num = 1
    while(len(mystr) > 28):
        # AVG QUALITY SECTION: quality_total() function returns a tuple
        qual_tuple = quality_total(mystr, course, alt)
        quality_rating += qual_tuple[0]
        quality_num += qual_tuple[1]

        # AVG DIFFICULTY SECTION: difficulty_total() function returns a tuple
        diff_tuple = difficulty_total(mystr, course, alt)
        difficulty_rating += diff_tuple[0]
        difficulty_num += diff_tuple[1]

        # GRADE SECTION: not using for now. if do use, make sure to account for altUrl
        # grade_mode() returns [a, b, c, d, f] where each elem is the # of that grade received
        # grade_list = grade_mode(mystr); a += grade_list[0]; b += grade_list[1]; c += grade_list[2]; d += grade_list[3]; f += grade_list[4]

        # Get the content of the next page
        page_num += 1

        if not alt:
            fp = urllib.request.urlopen(finalUrl + "&page=" + str(page_num))
        else:
            fp = urllib.request.urlopen(altUrl + "&page=" + str(page_num))

        mybytes = fp.read()
        mystr = mybytes.decode("utf8")
        fp.close()


    quality_rating /= quality_num
    difficulty_rating /= difficulty_num
    print("avg quality:", quality_rating)
    print("avg difficulty:", difficulty_rating)
    # max_grade = ""; if max(a, b, c, d, f) == a: max_grade = "A"; if max(a, b, c, d, f) == b: max_grade = "B"; if max(a, b, c, d, f) == c: max_grade = "C"; if max(a, b, c, d, f) == d: max_grade = "D"; if max(a, b, c, d, f) == f: max_grade = "F"; print([a, b, c, d, f]); print("most common grade:", max_grade)



def parse(schoolId, teacherName, course):
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


        # GETTING THE COURSES
        # load global dictionary of professor's courses from JSON file into uci_prof
        with open('my_dict.json') as f:
            uci_prof = json.load(f)
        preUrl = "https://www.ratemyprofessors.com/paginate/professors/ratings?" + tid
        if teacherName not in uci_prof:
            courses = getCourses(preUrl)
            uci_prof[teacherName] = courses
        # dump current uci_prof dict into the permanent dict
        with open('my_dict.json', 'w') as f:
            json.dump(uci_prof, f)


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
        mystr = mybytes.decode("utf8")
        fp.close()


        # GETTING THE RATINGS (AVG QUALITY & DIFFICULTY OF COURSE)
        getRatings(mystr, course, alt, finalUrl, altUrl)
            

if __name__ == "__main__":
    app.run()
    # parse(schoolId=1074, teacherName="Ray Klefstad", course="CS141")
    # parse(schoolId=1074, teacherName="Richard Pattis", course="ICS33")
    # parse(schoolId=1074, teacherName="Jennifer Wong-Ma", course="ICS53")
    # parse(schoolId=1074, teacherName="Sandra Irani", course="ICS6D")
    # parse(schoolId=1074, teacherName="Phillip Sheu", course="CS122A")
    # parse(schoolId=1074, teacherName="Phillip Sheu", course="COMPS122A")
    # parse(schoolId=1074, teacherName="Pavan Kadandale", course="BIO98")
    # parse(schoolId=1074, teacherName="Kimberly Hermans", course="ICS32A")
