import os
import re
import requests
from bs4 import BeautifulSoup
from luigi.notifications import email
import csv


def scrape_professor_emails(instructor_list):
    email_list = []
    others = []
    no_mail = []
    email_map = {}
    for x in range(0, len(instructor_list)):
        if len(instructor_list[x].split(' ')) > 2:
            others.append(instructor_list[x])
        email_list.append('N/A')

    failed = False

    for i, name in enumerate(instructor_list):
        namelist = name.split(' ')

        hrefs = ['nothing in here', 'N/A']

        url = 'https://www.sjsuone.sjsu.edu/sjsuPhoneBook/SearchResults.aspx?firstname=' + \
              namelist[0] + '|StartsWith&' + 'lastname=' + namelist[1] + '|StartsWith'
        page = requests.get(url)
        soup = BeautifulSoup(page.content, "html.parser")
        result_count = soup.find(id='BodyPlaceHolder_lblDisplayRecs')
        counts = result_count.text[0]

        if counts == '0':
            url = 'https://www.sjsuone.sjsu.edu/sjsuPhoneBook/SearchResults.aspx?firstname=' + \
                  namelist[0] + '+' + namelist[1] + '|StartsWith&' + \
                  'lastname=' + namelist[-1] + '|Contains'

            page = requests.get(url)
            soup = BeautifulSoup(page.content, "html.parser")
            result_count = soup.find(id='BodyPlaceHolder_lblDisplayRecs')
            counts = result_count.text[0]

        hrefs = soup.find_all('a', string=lambda text: namelist[0].lower() in str(
            text).lower() and namelist[-1].lower() in str(text).lower())

        if len(hrefs) == 0:
            # failed = True
            no_mail.append(name)
            continue

        if len(hrefs) == 1:
            nextEmail = hrefs[0].findNext('a')
            hrefs.append(nextEmail)

        email_list[i] = hrefs[1].text
        email_map[name] = hrefs[1].text

    for x in email_map:
        print(x + ": " + email_map[x])
    
    # write to csv file
    f = open(os.path.join(os.path.dirname(__file__), "users_rows.csv"), "w")
    writer = csv.DictWriter(f, fieldnames=["name", "email"])
    writer.writeheader()
    for x in email_map:
        writer.writerow({"name":x, "email":email_map[x]})

    return email_map