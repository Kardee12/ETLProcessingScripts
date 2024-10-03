import luigi

import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from scrapers.schedule_scraping import SJSUScraper
from scrapers.course_scraping import scrapeCourses
from helpers.data_exporter import DataExporter


class ScheduleProcessor(luigi.Task):
    """
    Task to scrape and process the scheduled data and process it and save it to database
    """
    url = luigi.Parameter()
    term = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget(f'data/{self.term}_course_schedule.csv')

    def run(self):
        scraper = SJSUScraper(self.url)
        content = scraper.getHTML()
        class_schedule_data = scraper.parseHTML(content)

        exporter = DataExporter()
        jsonData = exporter.to_json(class_schedule_data)
        with self.output().open('w') as output_file:
            exporter.to_csv(jsonData, output_file)


class CourseProcessor(luigi.Task):
    """
    Task to scrape and process the scheduled data and process it and save it to database
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


if __name__ == '__main__':
    luigi.build([CourseProcessor(departments=["AAS", "COMM"], term="2024_2025")], local_scheduler=True)
