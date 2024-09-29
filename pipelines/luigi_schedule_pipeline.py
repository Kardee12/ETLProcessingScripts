import luigi
import requests
import psycopg2
from bs4 import BeautifulSoup

class scrape_and_process_data(luigi.Task):
    """
    Task to scrape and process the scheduled data and process it and save it to database
    """
    url = luigi.Parameter()
    term = luigi.Parameter()

    def output(self):
        return luigi.LocalTarget('data/' + self.term + '_course_schedule')

    def run(self):
