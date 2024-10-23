from pydantic import BaseModel


class CourseScheduleEntry(BaseModel):
    term: str
    year: int
    department: str
    course: str
    section: str
    class_number: str
    mode_of_instruction: str
    course_title: str
    satisfies: str
    units: int
    class_type: str
    days: str
    times: str
    instructor: str
    instructorEmail: str
    location: str
    dates: str
    open_seats: int
    notes: str
