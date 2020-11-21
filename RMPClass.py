import re, requests
from lxml import etree
import logging
import urllib.request

#Author Email: yiyangl6@asu.edu

headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/75.0.3770.142 Safari/537.36"
}

INFO_NOT_AVAILABLE = "Info currently not available"

teacherList = []
tagFeedBackList = []
ratingList = []
takeAgainList = []

class RateMyProfAPI:

    #school id 45 = Arizona State University, the ID is initialized to 45 if not set upon usage.
    def __init__(self, schoolId=1074, teacher="staff", course=""):
        global teacherList
        if teacher != "staff":
            teacher = str(teacher).replace(" ", "+")
        else:
            teacher = ""

        self.pageData = ""
        self.finalUrl = ""
        self.tagFeedBack = ""
        self.rating = ""
        self.takeAgain = ""
        self.teacherName = teacher
        self.index = -1

        self.schoolId = schoolId

        try:
            self.index = teacherList.index(self.teacherName)
        except ValueError:
            teacherList.append(self.teacherName)

        self.course = course

    def retrieveRMPInfo(self):
        """
        :function: initialize the RMP data
        """
        print("MATCHA")
        global tagFeedBackList, ratingList, takeAgainList
        #If professor showed as "staff"
        if self.teacherName == "":
            self.rating = INFO_NOT_AVAILABLE
            self.takeAgain = INFO_NOT_AVAILABLE
            self.tagFeedBack = []

            ratingList.append(INFO_NOT_AVAILABLE)
            takeAgainList.append(INFO_NOT_AVAILABLE)
            tagFeedBackList.append(INFO_NOT_AVAILABLE)

            return

        # https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&queryBy=ErikJohnson&schoolName=Arizona+State+University&schoolID=45
        if self.index == -1:
            print("HOKKAIDO")
            #making request to the RMP page
            url = "https://www.ratemyprofessors.com/search.jsp?queryoption=HEADER&" \
                  "queryBy=teacherName&schoolName=University+of+California+Irvine&schoolID=%s&query=" % self.schoolId + self.teacherName
            print(url)

            page = requests.get(url=url, headers=headers)
            self.pageData = page.text
            # print(self.pageData)

            pageDataTemp = re.findall(r'ShowRatings\.jsp\?tid=\d+', self.pageData)
            # print(pageDataTemp)

            if len(pageDataTemp) > 0:
                pageDataTemp = re.findall(r'ShowRatings\.jsp\?tid=\d+', self.pageData)[0]
                self.finalUrl = "https://www.ratemyprofessors.com/" + pageDataTemp
                print(self.finalUrl)
                print(pageDataTemp)
                tid_location = pageDataTemp.find("tid=")
                tid = pageDataTemp[tid_location:]
                otherUrl = "https://www.ratemyprofessors.com/paginate/professors/ratings?" + tid + "&courseCode=" + self.course
                print(otherUrl)

                # to calculate avg quality rating
                quality_rating = 0
                quality_num = 0

                # get the content of the page
                fp = urllib.request.urlopen(otherUrl)
                mybytes = fp.read()
                mystr = mybytes.decode("utf8")
                fp.close()
                print("len(mystr):", len(mystr))

                # need to loop thru and get info for every page
                # if len(mystr) == 28, there is no info on the page
                page_num = 1
                while(len(mystr) > 28):

                    # get all quality tags
                    quality = re.findall('"quality":"[a-bA-z]*"', mystr)

                    for q in quality:
                        adjective = q.replace('"quality":"', '')
                        adjective = adjective.replace('"', '')
                        # print(adjective)

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

                    # get the content of the next page
                    page_num += 1
                    fp = urllib.request.urlopen(otherUrl + "&page=" + str(page_num))
                    mybytes = fp.read()
                    mystr = mybytes.decode("utf8")
                    fp.close()
                    print("len(mystr):", len(mystr))
                    

                print(quality_rating/quality_num)


                # courses = mystr.find('css-2b097c-container')
                # print(courses)
                # # end = courses + 3000
                # # print(end)
                # if(courses != -1):
                #     print(mystr[courses:courses+3000])
                # else:
                #     print("courses not found my guy")
                c2 = "RatingHeader__StyledClass-sc-1dlkqw1-2 gxDIt"
                c2_list = [i.start() for i in re.finditer(c2, mystr)]
                # re.findall(c2, mystr)
                # print(c2_list)
                # for c in range(0, len(c2_list), 2):
                #     start = c2_list[c]
                #     end = c2_list[c+1]
                #     print(mystr[start:end], "\n")


                self.tagFeedBack = []
                # Get tags
                page = requests.get(self.finalUrl)
                t = etree.HTML(page.text)
                # print(page.text)
                smth = '<div class="EmotionLabel__StyledEmotionLabel-sc-1u525uj-0 [a-zA-z0-9]*"><span role="img" aria-label="[a-zA-z0-9]*">'
                cooks = re.search(smth, page.text)
                # print("COOKS:", cooks)
                # output = open("output.txt", "w")
                # output.write(str(page.text))

                # END MY CODE

                tags = str(t.xpath('//*[@id="mainContent"]/div[1]/div[3]/div[2]/div[2]/span/text()'))
                # print("tags:", tags)
                tagList = re.findall(r'\' (.*?) \'', tags)
                # print("tagList:", tagList)
                if len(tagList) == 0:
                    self.tagFeedBack = []
                else:
                    self.tagFeedBack = tagList
                # print(self.tagFeedBack)

                # Get rating
                self.rating = str(t.xpath('//*[@id="mainContent"]/div[1]/div[3]/div[1]/div/div[1]/div/div/div/text()'))
                if re.match(r'.*?N/A', self.rating):
                    self.rating = INFO_NOT_AVAILABLE
                else:
                    try:
                        self.rating = re.findall(r'\d\.\d', self.rating)[0]
                    except IndexError:
                        self.rating = INFO_NOT_AVAILABLE
                # print(self.rating)

                # Get "Would Take Again" Percentage
                self.takeAgain = str(
                    t.xpath('//*[@id="mainContent"]/div[1]/div[3]/div[1]/div/div[2]/div[1]/div/text()'))
                if re.match(r'.*?N/A', self.takeAgain):
                    self.takeAgain = INFO_NOT_AVAILABLE
                else:
                    try:
                        self.takeAgain = re.findall(r'\d+%', self.takeAgain)[0]
                    except IndexError:
                        self.takeAgain = INFO_NOT_AVAILABLE

            else:
                self.rating = INFO_NOT_AVAILABLE
                self.takeAgain = INFO_NOT_AVAILABLE
                self.tagFeedBack = []

            ratingList.append(self.rating)
            takeAgainList.append(self.takeAgain)
            tagFeedBackList.append(self.tagFeedBack)

        else:
            self.rating = ratingList[self.index]
            self.takeAgain = takeAgainList[self.index]
            self.tagFeedBack = tagFeedBackList[self.index]

    def getRMPInfo(self):
        """
        :return: RMP rating.
        """

        if self.rating == INFO_NOT_AVAILABLE:
            return INFO_NOT_AVAILABLE

        return self.rating + "/5.0"

    def getTags(self):
        """
        :return: teacher's tag in [list]
        """
        return self.tagFeedBack

    def getFirstTag(self):
        """
        :return: teacher's most popular tag [string]
        """
        if len(self.tagFeedBack) > 0:
            return self.tagFeedBack[0]

        return INFO_NOT_AVAILABLE

    def getWouldTakeAgain(self):
        """
        :return: teacher's percentage of would take again.
        """
        return self.takeAgain


if __name__ == "__main__":
    aapi = RateMyProfAPI(schoolId=1074, teacher="Ray Klefstad", course="CS141")
    aapi.retrieveRMPInfo()
    print(aapi.getRMPInfo())