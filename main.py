import os
import json
import datetime

from canvasapi.todo import Todo
import config
from canvasapi import Canvas
from canvasapi.canvas import Course
from canvasapi.course import Assignment

API_URL = config.API_URL
API_KEY = config.API_TOKEN

JSON_PATH = config.JSON_PATH
ORG_PATH = config.ORG_PATH

COURSE_WHITELIST = config.COURSE_WHITELIST


class CanvasConnection:
    def __init__(self, url, token):
        self.canvas = Canvas(url, token)
        self.user = self.canvas.get_current_user()
        self.favorited_classes = self._get_favorited_classes()
        self.assignments_json = self._get_json()
        self.added_lines = {}

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
        with open(JSON_PATH) as f:
            data: dict = json.load(f)

        courses = {}
        for course in self.favorited_classes:
            course_name:str = course.name
            if course_name in data.keys():
                continue
            courses[course_name] = {}
            print("Built dict for ", course_name)


        data.update(courses)

        with open(JSON_PATH,'w') as f:
            json.dump(data, f, indent=4, sort_keys=True)

        self.assignments_json = data


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

                # Filterng out reading assignments, unless its in course whitelist
                if not course_name in COURSE_WHITELIST:
                    if not is_graded or is_graded == "not_graded":
                        continue


                print(f"Building assignment '{name}' for course '{course_name}'")
                unlock_date = assignment_data["assignment"].get('unlock_at', None)
                due_date = assignment_data["assignment"].get('due_at', None)
                link = assignment_data["assignment"].get('html_url', None)

                assignment_info = {
                    "unlock_date": convert_time(unlock_date),
                    "due_date": convert_time(due_date),
                    "link": link,
                }
                self.assignments_json[course_name][name] = assignment_info
                course_prefix = ''.join(course_name.split('-')[0:2])
                self.added_lines[f"{course_prefix}: {name}"] = assignment_info

    def build_json(self):
        self.build_course_json()
        self.build_assignment_json()
        self._write_to_json()

    def write_to_org(self):
        with open(ORG_PATH, 'a') as f:
            for assignment in self.added_lines.keys():
                unlock_date = self.added_lines[assignment]["unlock_date"]
                due_date = self.added_lines[assignment]["due_date"]
                link = self.added_lines[assignment]["link"]

                print("Writing org entry for ", assignment)
                f.write(f"* TODO {assignment}\n")

                # SCHEDULED: <2022-09-05 Mon 18:00> DEADLINE: <2022-09-09 Fri>
                time_due = ""
                if unlock_date:
                    time_due += f"SCHEDULED: <{unlock_date}> "

                time_due += f"DEADLINE: <{due_date}>"
                f.write(f"{time_due}\n")
                f.write(f"[[{link}][Link to assignment]]\n")

    def run(self):
        self.build_json()
        print()
        self.write_to_org()

def convert_time(time_) -> str:
    """ Converts from YYYY-MM-DDTHH:mm:ss.fZ -> YYYY-MM-DD DAY"""
    if not time_:
        return time_

    days = {0:"Mon", 1:"Tue", 2:"Wed", 3:"Thu", 4:"Fri", 5:"Sat", 6:"Sun"}
    important_part = time_.split("T")[0]
    format_ = "%Y-%m-%d"
    dt_obj = datetime.datetime.strptime(important_part, format_)
    dt_obj -= datetime.timedelta(days=1)
    dt_str = ''.join(str(dt_obj).split(" ")[0])
    return f"{dt_str} {days[dt_obj.weekday()]}"



if __name__ == "__main__":
    driver = CanvasConnection(url=API_URL, token=API_KEY)
    driver.run()
