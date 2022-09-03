import os
import json
import datetime

from canvasapi.todo import Todo
import config
from pprint import pprint
from canvasapi import Canvas, assignment
from canvasapi.canvas import Course
from canvasapi.course import Assignment

API_URL = "https://pacific.instructure.com/"
API_KEY = config.API_TOKEN

JSON_PATH = "assignments2.json"
COURSE_WHITELIST = ["COMP-191A-0-82653 Deep Learning Images (Fall 2022)"]

class CanvasConnection:
    def __init__(self, url, token):
        self.canvas = Canvas(url, token)
        self.user = self.canvas.get_current_user()
        self.favorited_classes = self._get_favorited_classes()
        self.assignments_json = self._get_json()

    def _get_json(self) -> dict:
        with open(JSON_PATH, 'r') as f:
            data = json.load(f)
            return data

    def _write_to_json(self):
        with open(JSON_PATH, 'w') as f:
            json.dump(self.assignments_json, f, indent=4, sort_keys=True)

    def _get_favorited_classes(self) -> list[Course]:
        paginated_courses = self.user.get_favorite_courses()
        return [course for course in paginated_courses]

    def _get_assignments(self, course: Course) -> list[Assignment]:
        paginated_assignments = course.get_assignments()
        return [assignment  for assignment in paginated_assignments]

    def _get_todos(self, course: Course):
        paginated_todo = course.get_todo_items()
        todos: list[Todo] = [todo for todo in paginated_todo]
        return todos

    def build_course_json(self):
        """ This is only called once per semester
            It builds out initial json without courses
        """
        courses = {}
        for course in self.favorited_classes:
            course_name:str = course.name
            courses[course_name] = {}

        with open(JSON_PATH) as f:
            data = json.load(f)

        data.update(courses)

        with open(JSON_PATH,'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)


    def build_assignment_json(self):
        """ Builds out assignment dictionary for specified course """
        for course in self._get_favorited_classes():
            course_name = course.name
            todos = self._get_todos(course)
            for assignment in todos:
                assignment_data = assignment.__dict__
                name = assignment_data["assignment"].get('name', None)
                if self.assignments_json[course_name].get(name, None):
                    continue

                is_graded = assignment_data["assignment"].get('grading_type', None)

                if not course_name in COURSE_WHITELIST:
                    if not is_graded or is_graded == "not_graded":
                        continue

                unlock_date = assignment_data["assignment"].get('unlock_at', None)
                due_date = assignment_data["assignment"].get('created_at', None)
                link = assignment_data["assignment"].get('html_url', None)

                assignment_info = {
                    "unlock_date": unlock_date,
                    "due_date": due_date,
                    "link": link,
                }
                self.assignments_json[course_name][name] = assignment_info

    def build_json(self):
        self.build_course_json()
        self.build_assignment_json()
        self._write_to_json()


    def convert_times(self, time_:str) -> str:
        """ Converts from YYYY-MM-DDTHH:mm:ss.fZ -> YYYY-MM-DD DAY"""
        important_part = time_.split("T")[0]
        format_ = "%Y-%m-%d"
        dt_obj = datetime.datetime.strptime(important_part, format_)
        return str(dt_obj)

    def run(self):
        self.build_json()

    

if __name__ == "__main__":
    driver = CanvasConnection(url=API_URL, token=API_KEY)
    driver.run()

    # some_todo = driver._get_todos(driver.favorited_classes[0])[0]
    # pprint(some_todo.__dict__)
