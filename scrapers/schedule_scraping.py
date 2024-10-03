import re
import requests
from bs4 import BeautifulSoup
from models.course_schedule_entry import CourseScheduleEntry


class SJSUScraper:
    def __init__(self, url):
        self.url = url

    def getHTML(self):
        response = requests.get(self.url)
        response.raise_for_status()
        return response.content

    def parseHTML(self, html):
        soup = BeautifulSoup(html, "html.parser")
        table = soup.find("table", id="classSchedule")
        schedule_data = []

        for row in table.find_all("tr"):
            if row.find("th"):
                continue
            columns = row.find_all("td")

            department, course, section = columns[0].text.strip().split(" ", 2)
            section = re.findall(r"[a-zA-Z0-9]+", section)[0]
            class_number = columns[1].text.strip()
            mode_of_instruction = columns[2].text.strip()
            course_title = columns[3].text.strip()
            satisfies = columns[4].text.strip()
            units = int(float(columns[5].text.strip()))
            class_type = columns[6].text.strip()
            days = columns[7].text.strip()
            times = columns[8].text.strip()
            instructor = columns[9].text
            email_link_tag = columns[9].find('a')
            if email_link_tag and email_link_tag.has_attr('href'):
                instructorEmail = email_link_tag['href']
                instructorEmail = instructorEmail.replace("mailto:", "")
            else:
                instructorEmail = ""
            location = columns[10].text.strip()
            dates = columns[11].text.strip()
            open_seats = int(float(columns[12].text.strip()))
            notes = columns[13].text.strip()

            entry = CourseScheduleEntry(
                term=None,
                department=department,
                course=course,
                section=section,
                class_number=class_number,
                mode_of_instruction=mode_of_instruction,
                course_title=course_title,
                satisfies=satisfies,
                units=units,
                class_type=class_type,
                days=days,
                times=times,
                instructor=instructor,
                instructorEmail=instructorEmail,
                location=location,
                dates=dates,
                open_seats=open_seats,
                notes=notes,
            )
            schedule_data.append(entry)

        return schedule_data

