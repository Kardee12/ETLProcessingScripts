from pydantic import BaseModel


class CourseEntry(BaseModel):
    department: str
    course: str
    name: str
    units: str
    description: str
    prereqs: str
    satisfies: str
    grading: str
    repeatable: str
    crosslist: str
    sustainability: str
    notes: str


class DepartmentEntry(BaseModel):
    tag: str
    name: str
