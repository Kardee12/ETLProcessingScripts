from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service

from models.course_entry import CourseEntry
from models.course_entry import DepartmentEntry


def initializeDriver():
    options = webdriver.ChromeOptions()
    prefs = {"profile.default_content_setting_values.notifications": 2}
    options.add_experimental_option("prefs", prefs)
    service = Service(ChromeDriverManager().install())
    return webdriver.Chrome(service=service, options=options)


def parseBody(body):
    # name = body.pop(0)
    department, course, name = body.pop(0).strip().split(" ", 2)
    name = name.split("- ", 1)[1]
    units = next((text for text in body if text.endswith("unit(s)")), None) or ""
    description = next((text for text in body if not text.startswith("Prerequisite(s)") and not text.startswith(
        "Grading: ") and not text.endswith("unit(s)")), None) or ""
    prereqs = next(
        (text for text in body if text.startswith("Prerequisite(s)") or text.startswith("Pre/Corequisite(s)")), None) or ""
    crosslist = next((text for text in body if text.startswith("Cross-listed ")), None) or ""
    grading = next((text for text in body if text.startswith("Grading: ")), None) or ""
    satisfies = next((text for text in body if text.startswith("Satisfies ")), None) or ""
    repeatable = next((text for text in body if text.startswith("Course may be repeated for credit for up to ")), None) or ""
    sustainability = next((text for text in body if text.startswith("Sustainability")), None) or ""
    notes = next((text for text in body if text.startswith("Note(s):")), None) or ""

    course_entry = CourseEntry(
        department=department,
        course=course,
        name=name,
        units=units,
        description=description,
        prereqs=prereqs,
        satisfies=satisfies,
        grading=grading,
        repeatable=repeatable,
        crosslist=crosslist,
        sustainability=sustainability,
        notes=notes
    )

    return course_entry


# need this bc the course website sometimes just doesnt load correctly for some reason and needs a refresh
# why is sj's own course website broken
def findDeptName(driver):
    # try 10 reloads
    for i in range(10):
        try:
            deptName = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.TAG_NAME, "strong"))
            ).text
            return deptName
        except:
            driver.refresh()
            continue
    exit()


def getClassesData(driver, courses):
    rows = WebDriverWait(driver, 5).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "width"))
    )
    for row in rows:
        WebDriverWait(row, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "a"))
        ).click()
        title = WebDriverWait(row, 5).until(
            EC.presence_of_element_located((By.TAG_NAME, "h3"))
        )
        body = title.find_element(By.XPATH, "..").text
        body = body.split("\n")
        courseInfo = parseBody(body)
        courses.append(courseInfo)


def scrapeCourses(prefixes):
    courses = []
    departmentNames = []
    driver = initializeDriver()
    for tag in prefixes:
        driver.get(
            f'https://catalog.sjsu.edu/content.php?filter[27]={tag}&filter[29]=&filter[keyword]=&filter[32]=1&filter[cpage]=1&cur_cat_oid=14&expand=&navoid=5106&search_database=Filter&filter[exact_match]=1#acalog_template_course_filter')
        deptName = findDeptName(driver)

        department_entry = DepartmentEntry(
            tag=tag,
            name=deptName
        )

        departmentNames.append(department_entry)
        getClassesData(driver, courses)

        try:
            # sometimes the page has a page 2...
            driver.find_element(By.CSS_SELECTOR, '[aria-label="Page 2"]').click()
            findDeptName(driver)
            getClassesData(driver, courses)
        except:
            continue

    return [courses, departmentNames]