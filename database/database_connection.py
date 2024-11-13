import datetime

import psycopg2
from datetime import date

from matplotlib.backend_bases import cursors


class DatabaseConnection:

    connection = None

    def connect_to_db(self, database, host, user, password, port):
        self.connection = psycopg2.connect(database=database,
                                host=host,
                                user=user,
                                password=password,
                                port=port)

    def get_missing_emails(self, schedules):
        cursor = self.connection.cursor()
        missing_emails = set()
        # query instructor
        for schedule in schedules:
            full_name = schedule.instructor

            if full_name == "Staff":
                continue

            index = full_name.find("/")
            if index != -1:
                full_name = full_name[:index].strip()

            query = "SELECT * FROM users WHERE name = %s"
            cursor.execute(query, (full_name,))
            row = cursor.fetchone()

            # id exists, update schedule
            if row is None:
                missing_emails.add(full_name)

        return list(missing_emails)

    def update_courses(self, courses):
        cursor = self.connection.cursor()
        for course in courses:
            try:
                query = f"INSERT INTO courses (course_number, name, description, prereqs, units, satisfies_area, department)"\
                        f"VALUES ('{course.course}', '{course.name}', '{course.description}', '{course.prereqs}', '{course.units}', '{course.satisfies}', '{course.department}') ON CONFLICT (course_number, department) "\
                        f"DO UPDATE SET "\
                        f"course_number = EXCLUDED.course_number, "\
                        f"name = EXCLUDED.name, "\
                        f"description = EXCLUDED.description,"\
                        f"prereqs = EXCLUDED.prereqs,"\
                        f"units = EXCLUDED.units,"\
                        f"satisfies_area = EXCLUDED.satisfies_area,"\
                        f"department = EXCLUDED.department "\
                        f"WHERE courses.course_number IS DISTINCT FROM EXCLUDED.course_number "\
                        f"OR courses.name IS DISTINCT FROM EXCLUDED.name "\
                        f"OR courses.description IS DISTINCT FROM EXCLUDED.description "\
                        f"OR courses.prereqs IS DISTINCT FROM EXCLUDED.prereqs "\
                        f"OR courses.units IS DISTINCT FROM EXCLUDED.units "\
                        f"OR courses.satisfies_area IS DISTINCT FROM EXCLUDED.satisfies_area "\
                        f"OR courses.department IS DISTINCT FROM EXCLUDED.department;"
                cursor.execute(query)
            except psycopg2.errors.Error as e:
                self.connection.rollback()
                print(f"Error inserting course ({course.course}): \n" + str(e))

        self.connection.commit()
        cursor.close()

    def update_professors(self, professors):
        cursor = self.connection.cursor()
        for professor in professors:
            prof_id = professors[professor].split("@")[0]
            current_date = date.today()

            # %s = prof_id, current_date, professor
            try:
                query = f"INSERT INTO users (id, created_at, name, email, is_professor)" \
                        f"VALUES (%s, %s, %s, %s, %s) ON CONFLICT (id) " \
                        f"DO UPDATE SET " \
                        f"id = EXCLUDED.id, " \
                        f"created_at = EXCLUDED.created_at, " \
                        f"name = EXCLUDED.name," \
                        f"email = EXCLUDED.email," \
                        f"is_professor = EXCLUDED.is_professor " \
                        f"WHERE users.id IS DISTINCT FROM EXCLUDED.id " \
                        f"OR users.created_at IS DISTINCT FROM EXCLUDED.created_at " \
                        f"OR users.name IS DISTINCT FROM EXCLUDED.name " \
                        f"OR users.email IS DISTINCT FROM EXCLUDED.email " \
                        f"OR users.is_professor IS DISTINCT FROM EXCLUDED.is_professor;"

                cursor.execute(query, (prof_id, current_date, professor, professors[professor], True))
            except psycopg2.errors.Error as e:
                self.connection.rollback()
                print(f"Error inserting user ({id}): \n" + str(e))

        self.connection.commit()
        cursor.close()

    def update_schedules(self, schedules):
        cursor = self.connection.cursor()
        # query instructor
        for schedule in schedules:
            full_name = schedule.instructor

            if full_name == "Staff":
                continue

            index = full_name.find("/")
            if index != -1:
                full_name = full_name[:index].strip()

            query = "SELECT * FROM users WHERE name = %s"
            cursor.execute(query, (full_name,))
            row = cursor.fetchone()

            if row is not None:
                columns = [desc[0] for desc in cursor.description]
                row_dict = dict(zip(columns, row))
                professor_id = row_dict['id']

                # update schedule
                try:
                    query = f"INSERT INTO schedules (term, year, class_number, course_number, section, days, dates, times, class_type, units, location, mode_of_instruction, satisfies_area, professor_id, department)" \
                            f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT (class_number) " \
                            f"DO UPDATE SET " \
                            f"term = EXCLUDED.term, " \
                            f"year = EXCLUDED.year, " \
                            f"class_number = EXCLUDED.class_number," \
                            f"course_number = EXCLUDED.course_number," \
                            f"section = EXCLUDED.section," \
                            f"days = EXCLUDED.days," \
                            f"dates = EXCLUDED.dates, " \
                            f"times = EXCLUDED.times, " \
                            f"class_type = EXCLUDED.class_type, " \
                            f"units = EXCLUDED.units, " \
                            f"location = EXCLUDED.location, " \
                            f"mode_of_instruction = EXCLUDED.mode_of_instruction, " \
                            f"satisfies_area = EXCLUDED.satisfies_area, " \
                            f"professor_id = EXCLUDED.professor_id, " \
                            f"department = EXCLUDED.department " \
                            f"WHERE schedules.term IS DISTINCT FROM EXCLUDED.term " \
                            f"OR schedules.year IS DISTINCT FROM EXCLUDED.year " \
                            f"OR schedules.class_number IS DISTINCT FROM EXCLUDED.class_number " \
                            f"OR schedules.course_number IS DISTINCT FROM EXCLUDED.course_number " \
                            f"OR schedules.section IS DISTINCT FROM EXCLUDED.section " \
                            f"OR schedules.days IS DISTINCT FROM EXCLUDED.days " \
                            f"OR schedules.dates IS DISTINCT FROM EXCLUDED.dates " \
                            f"OR schedules.times IS DISTINCT FROM EXCLUDED.times " \
                            f"OR schedules.class_type IS DISTINCT FROM EXCLUDED.class_type " \
                            f"OR schedules.units IS DISTINCT FROM EXCLUDED.units " \
                            f"OR schedules.location IS DISTINCT FROM EXCLUDED.location " \
                            f"OR schedules.mode_of_instruction IS DISTINCT FROM EXCLUDED.mode_of_instruction " \
                            f"OR schedules.satisfies_area IS DISTINCT FROM EXCLUDED.satisfies_area " \
                            f"OR schedules.professor_id IS DISTINCT FROM EXCLUDED.professor_id " \
                            f"OR schedules.department IS DISTINCT FROM EXCLUDED.department;"
                    cursor.execute(query, (schedule.term, schedule.year, schedule.class_number, schedule.course, schedule.section, schedule.days, schedule.dates, schedule.times, schedule.class_type, schedule.units, schedule.location, schedule.mode_of_instruction, schedule.satisfies, professor_id, schedule.department))
                except psycopg2.errors.Error as e:
                    self.connection.rollback()
                    print(f"Error inserting class ({schedule.class_number}): \n" + str(e))

            self.connection.commit()

        cursor.close()

    def update_reviews(self, reviews):
        cursor = self.connection.cursor()

        valid_tags = self.__get_valid_enum("tag_enum")
        valid_grades = self.__get_valid_enum("grade_enum")
        for review in reviews:
            try:
                cleaned_tags = [tag.strip() for tag in review.tags if tag.strip() in valid_tags]
                review.grade = review.grade if review.grade in valid_grades else None
                query = f"INSERT INTO reviews (created_at, updated_at, user_id, professor_id, course_number, department, content, quality, ease, grade, tags, take_again, is_user_anonymous)" \
                        f"VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s::tag_enum[], %s, %s) ON CONFLICT (id) " \
                        f"DO UPDATE SET " \
                        f"created_at = EXCLUDED.created_at, " \
                        f"updated_at = EXCLUDED.updated_at," \
                        f"user_id = EXCLUDED.user_id," \
                        f"professor_id = EXCLUDED.professor_id," \
                        f"course_number = EXCLUDED.course_number," \
                        f"department = EXCLUDED.department, " \
                        f"content = EXCLUDED.content, " \
                        f"quality = EXCLUDED.quality, " \
                        f"ease = EXCLUDED.ease, " \
                        f"grade = EXCLUDED.grade, " \
                        f"tags = EXCLUDED.tags, " \
                        f"take_again = EXCLUDED.take_again, " \
                        f"is_user_anonymous = EXCLUDED.is_user_anonymous " \
                        f"WHERE reviews.created_at IS DISTINCT FROM EXCLUDED.created_at " \
                        f"OR reviews.updated_at IS DISTINCT FROM EXCLUDED.updated_at " \
                        f"OR reviews.user_id IS DISTINCT FROM EXCLUDED.user_id " \
                        f"OR reviews.professor_id IS DISTINCT FROM EXCLUDED.professor_id " \
                        f"OR reviews.course_number IS DISTINCT FROM EXCLUDED.course_number " \
                        f"OR reviews.department IS DISTINCT FROM EXCLUDED.department " \
                        f"OR reviews.content IS DISTINCT FROM EXCLUDED.content " \
                        f"OR reviews.quality IS DISTINCT FROM EXCLUDED.quality " \
                        f"OR reviews.ease IS DISTINCT FROM EXCLUDED.ease " \
                        f"OR reviews.grade IS DISTINCT FROM EXCLUDED.grade " \
                        f"OR reviews.tags IS DISTINCT FROM EXCLUDED.tags " \
                        f"OR reviews.take_again IS DISTINCT FROM EXCLUDED.take_again " \
                        f"OR reviews.is_user_anonymous IS DISTINCT FROM EXCLUDED.is_user_anonymous;"
                cursor.execute(query, (review.created_at, review.updated_at, review.user_id, review.professor_id, review.course_number, review.department, review.content, review.quality, review.ease, review.grade, cleaned_tags, review.take_again, review.is_user_anonymous))
            except psycopg2.errors.Error as e:
                self.connection.rollback()
                print(f"Error inserting review: \n" + str(e))

        self.connection.commit()
        cursor.close()

    def __get_valid_enum(self, enum_name):
        cursor = self.connection.cursor()
        try:
            query = f"SELECT unnest(enum_range(NULL::{enum_name}));"
            cursor.execute(query)
            enum_values = [row[0] for row in cursor.fetchall()]
            cursor.close()
            return enum_values
        except psycopg2.errors.Error as e:
            print(f"Error querying available enum values: \n" + str(e))
        cursor.close()
        return []
            

    def close_database(self):
        self.connection.close()