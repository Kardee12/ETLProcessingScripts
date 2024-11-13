from scrapers.ratemyprofessor import *

from models.review_entry import ReviewEntry

from datetime import datetime

import csv
import re

def scrape_reviews():
    reviews = []

    with open("../scrapers/users_rows.csv") as prof_rows:
        reader = csv.DictReader(prof_rows)
        for row in reader:
            professor = get_professor_by_school_and_name(
                get_school_by_name("San Jose State University"), row["name"])
            if professor is not None and professor.school.name == "San Jose State University":
                ratings = professor.get_ratings()
                for rating in ratings:
                    year = rating.date.year
                    current_year = datetime.now().year
                    if year >= current_year - 1:
                        class_name = rating.class_name
                        department, course_number = None, None
                        if "-" in class_name:
                            split = class_name.split("-")
                            department = split[0]
                            course_number = split[1]
                        else:
                            match = re.match(r"([A-Za-z]+)(\d+.*)", class_name)
                            if match:
                                department = match.group(1)
                                course_number = match.group(2)
                            else:
                                continue

                        parsed_tags = rating.rating_tags.split("--")
                        parsed_take_again = rating.take_again or False
                        department = department.upper()
                        course_number = course_number.lstrip("0")

                        review = ReviewEntry(
                            created_at=rating.date,
                            updated_at=None,
                            user_id=None,
                            professor_id=row["email"].replace("@sjsu.edu", ""),
                            course_number=course_number,
                            department=department,
                            content=rating.comment,
                            quality=rating.rating,
                            ease=rating.difficulty,
                            grade=rating.grade,
                            tags=parsed_tags,
                            take_again=parsed_take_again,
                            is_user_anonymous=False
                        )

                        reviews.append(review)
    return reviews