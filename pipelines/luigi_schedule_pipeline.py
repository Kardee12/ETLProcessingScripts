import luigi

import sys
import os

from dotenv import load_dotenv

from scrapers.schedule_scraping import SJSUScraper
from scrapers.course_scraping import scrapeCourses
from scrapers.professor_scraping import scrape_professor_emails
from helpers.data_exporter import DataExporter
from database.database_connection import DatabaseConnection

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

class DatabaseUpdater(luigi.Task):
    """
    Task to insert scraped data into a database
    """
    departments = luigi.Parameter()
    url = luigi.Parameter()
    term = luigi.Parameter()
    year = luigi.Parameter()

    def run(self):
        # database details
        database = os.getenv("DATABASE")
        host = os.getenv("HOST")
        user = os.getenv("USER")
        password = os.getenv("PASSWORD")
        port = os.getenv("PORT")

        db_conn = DatabaseConnection()
        db_conn.connect_to_db(database, host, user, password, port)

        # 1) fetch courses
        courses, departments_scraped = scrapeCourses(self.departments)

        # 2) fetch schedules
        scraper = SJSUScraper(self.url, self.term, self.year)
        content = scraper.getHTML()
        class_schedule_data = scraper.parseHTML(content)

        # 3) fetch missing professors
        missing_emails = db_conn.get_missing_emails(class_schedule_data)
        scraped_profs = scrape_professor_emails(missing_emails)

        # 4) insert professors, courses, and schedules
        db_conn.update_professors(scraped_profs)
        db_conn.update_courses(courses)
        db_conn.update_schedules(class_schedule_data)

        db_conn.close_database()

if __name__ == '__main__':
    luigi.build([DatabaseUpdater(departments=["MUSC"], url="https://www.sjsu.edu/classes/schedules/fall-2024.php", term="Fall", year=2024)], local_scheduler=True)
