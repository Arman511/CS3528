from flask import render_template, request
from .models import Opportunity
from core import handlers
from courses.models import Course
from skills.models import Skill