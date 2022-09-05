#!/usr/bin/env python3
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

API_URL = os.getenv("API_URL")
API_TOKEN = os.getenv("API_TOKEN")

JSON_PATH = str(Path.home()) + str(os.getenv("JSON_PATH"))
ORG_PATH = str(Path.home()) + str(os.getenv("ORG_PATH"))

COURSE_WHITELIST = ["COMP-191A-0-82653 Deep Learning Images (Fall 2022)"]
