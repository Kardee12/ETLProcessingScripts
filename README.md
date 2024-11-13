# ETL Processing Scripts

This repository contains the scripts for scraping and processing the data needed for the [ACM Course Scheduler](https://github.com/SJSUCSClub/course-scheduling-client).

## Getting Started

In order to get started, first set up your environment. Make a file `.env` inside the project directory, similar to the one below

```sh
DB_DATABASE="course_scheduler"
DB_HOST="localhost"
DB_USER="postgres"
DB_PASSWORD="postgres"
DB_PORT="5432"
```

Then, make sure that your database is running and accessible at the location specified in your `.env`. Assuming you're testing with the [ACM Course Scheduler Server](https://github.com/SJSUCSClub/course-scheduling-server), the above variables will work.

### Locally

To run everything locally, simply install the requirements with:

```sh
pip install -r requirements.txt
```

And then run the pipeline by doing:

```sh
python3 ./pipelines/luigi_schedule_pipeline.py
```

### With Docker

To run with docker, use the development dockerfile

```sh
docker compose -f docker-compose.dev.yml up --build
```
