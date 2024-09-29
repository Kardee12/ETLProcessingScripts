import luigi

from helpers.data_exporter import DataExporter
from scrapers.schedule_scraping import SJSUScraper


class scrape_and_process_data(luigi.Task):
    """
    Task to scrape and process the scheduled data and process it and save it to database
    """
    url = luigi.Parameter()
    term = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget('data/{self.term}_course_schedule')

    def run(self):
        scraper = SJSUScraper(self.url)
        content = scraper.getHTML()
        class_schedule_data = scraper.parseHTML(content)

        exporter = DataExporter()
        jsonData = exporter.to_json(class_schedule_data)
        with self.output().open('w') as output_file:
            exporter.to_csv(jsonData, output_file)