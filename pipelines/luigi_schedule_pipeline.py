import luigi

import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv

from scrapers.review_scraping import scrape_reviews

from database.database_connection import DatabaseConnection

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
        database = os.getenv("DB_DATABASE")
        host = os.getenv("DB_HOST")
        user = os.getenv("DB_USER")
        password = os.getenv("DB_PASSWORD")
        port = os.getenv("DB_PORT")

        db_conn = DatabaseConnection()
        db_conn.connect_to_db(database, host, user, password, port)

        # 1) fetch courses
        # courses, departments_scraped = scrapeCourses(self.departments)

        # 2) fetch schedules
        # scraper = SJSUScraper(self.url, self.term, self.year)
        # content = scraper.getHTML()
        # class_schedule_data = scraper.parseHTML(content)

        # 3) fetch missing professors
        # missing_emails = db_conn.get_missing_emails(class_schedule_data)
        # scraped_profs = scrape_professor_emails(missing_emails)

        # 4) fetch reviews
        reviews = scrape_reviews()

        # 5) insert professors, courses, and schedules
        # db_conn.update_professors(scraped_profs)
        # db_conn.update_courses(courses)
        # db_conn.update_schedules(class_schedule_data)
        db_conn.update_reviews(reviews)

        db_conn.close_database()

if __name__ == '__main__':
    luigi.build([DatabaseUpdater(departments=["MUSC", "MATH"], url="https://www.sjsu.edu/classes/schedules/fall-2024.php", term="Fall", year="2024")], local_scheduler=True)
