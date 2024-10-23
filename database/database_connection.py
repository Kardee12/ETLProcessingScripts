import psycopg2


class DatabaseConnection:

    connection = None

    def connect_to_db(self, database, host, user, password, port):
        self.connection = psycopg2.connect(database=database,
                                host=host,
                                user=user,
                                password=password,
                                port=port)

    def update_courses(self, courses):
        cursor = self.connection.cursor()
        for course in courses:
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

            # id exists, update schedule
            if row is not None:
                columns = [desc[0] for desc in cursor.description]
                row_dict = dict(zip(columns, row))
                professor_id = row_dict['id']

                # update schedule
                try:
                    query = f"INSERT INTO schedules (term, year, class_number, course_number, section, days, dates, times, class_type, units, location, mode_of_instruction, satisfies_area, professor_id, department)" \
                            f"VALUES ('{schedule.term}', '{schedule.year}', '{schedule.class_number}', '{schedule.course}', '{schedule.section}', '{schedule.days}', '{schedule.dates}', '{schedule.times}', '{schedule.class_type}', '{schedule.units}', '{schedule.location}', '{schedule.mode_of_instruction}', '{schedule.satisfies}', %s, '{schedule.department}') ON CONFLICT (class_number) " \
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
                    cursor.execute(query, (professor_id,))
                    self.connection.commit()
                except psycopg2.errors.ForeignKeyViolation as e:
                    self.connection.rollback()
                    print("Error inserting: " + str(e))


        cursor.close()

    def close_database(self):
        self.connection.close()