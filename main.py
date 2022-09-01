import os
import json
import datetime
import config
from canvasapi import Canvas
from canvasapi.canvas import Course
from canvasapi.course import Assignment

API_URL = "https://pacific.instructure.com/"
API_KEY = config.API_TOKEN

JSON_PATH = "assignments2.json"

class CanvasConnection:
    def __init__(self, url, token):
        self.canvas = Canvas(url, token)
        self.user = self.canvas.get_current_user()
        self.favorited_classes = self._get_favorited_classes()
        self.assignments_json = self._get_json()

    def _get_json(self):
        with open(JSON_PATH) as f:
            self.assignments_json = json.load(f)

    def _get_favorited_classes(self) -> list[Course]:
        paginated_courses = self.user.get_favorite_courses()
        return [course for course in paginated_courses]

    def _get_assignments(self, course: Course) -> list[Assignment]:
        paginated_assignments = course.get_assignments()
        return [assignment  for assignment in paginated_assignments]

    def build_course_json(self):
        """ This is only called once per semester
            It builds out initial json without courses
        """
        courses = {}
        for course in self.favorited_classes:
            course_name:str = course.name
            course_name = '-'.join(course_name.split('-')[0:2])

        with open(JSON_PATH) as f:
            data = json.load(f)

        with open(JSON_PATH) as f:
            json.dump(data, f, indent=4, sort_keys=True)


    def build_assignment_json(self, course: Course) -> dict:
        """ Builds out assignment dictionary for specified course """
        list_assignments = self._get_assignments(course)
        course_assignments_dict = {}

        for assignment in list_assignments:
            try:
                grade = assignment.grade
                posted_date = self.convert_times(assignment.posted_at)
                due_date = self.convert_times(assignment.due_at)
            except:
                continue
        return course_assignments_dict

    def convert_times(self, time_:str) -> str:
        """ Converts from YYYY-MM-DDTHH:mm:ss.fZ -> YYYY-MM-DD DAY"""
        important_part = time_.split("T")[0]
        format_ = "%Y-%m-%d"
        dt_obj = datetime.datetime.strptime(time_, format_)
        return str(dt_obj)

    

if __name__ == "__main__":
    pass
