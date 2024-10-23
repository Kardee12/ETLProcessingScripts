import luigi

import sys
import os

from dotenv import load_dotenv

from scrapers.schedule_scraping import SJSUScraper
from scrapers.course_scraping import scrapeCourses
from helpers.data_exporter import DataExporter
from database.database_connection import DatabaseConnection

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
load_dotenv()

class ScheduleProcessor(luigi.Task):
    """
    Task to scrape and process the schedule data
    """
    url = luigi.Parameter()
    term = luigi.Parameter()
    year = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(f'data/{self.term}_{self.year}_course_schedule.csv')

    def run(self):
        scraper = SJSUScraper(self.url, self.term, self.year)
        content = scraper.getHTML()
        class_schedule_data = scraper.parseHTML(content)

        exporter = DataExporter()
        jsonData = exporter.to_json(class_schedule_data)
        with self.output().open('w') as output_file:
            exporter.to_csv(jsonData, output_file)


class CourseProcessor(luigi.Task):
    """
    Task to scrape and process the scheduled data
    """
    departments = luigi.Parameter()
    term = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(f'data/{self.term}_courses.csv')

    def run(self):
        courses, departments = scrapeCourses(self.departments)

        exporter = DataExporter()

        coursesJson = exporter.to_json(courses)

        with self.output().open('w') as output_file:
            exporter.to_csv(coursesJson, output_file)


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

        # fetch courses & departments
        # courses, departments = scrapeCourses(self.departments)

        # fetch schedules
        scraper = SJSUScraper(self.url, self.term, self.year)
        content = scraper.getHTML()
        class_schedule_data = scraper.parseHTML(content)

        db_conn = DatabaseConnection()
        db_conn.connect_to_db(database, host, user, password, port)
        # db_conn.update_courses(courses)
        db_conn.update_schedules(class_schedule_data)


if __name__ == '__main__':
    luigi.build([DatabaseUpdater(departments=["AE"], url="https://www.sjsu.edu/classes/schedules/fall-2024.php", term="Fall", year=2024)], local_scheduler=True)
