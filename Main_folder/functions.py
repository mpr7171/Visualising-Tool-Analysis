import firebase_admin
from firebase_admin import credentials, auth
from firebase_admin import db
from flask import Flask, session, render_template, request, redirect, request, flash, url_for
import re
import json
import requests
import plotly.graph_objects as go
import numpy as np
from plotly.subplots import make_subplots
import random
import pandas as pd
from datetime import datetime
import logging


def calculate_percentage(scores, your_score):
    higher_scores = 0
    for sc in scores:
        if sc > your_score:
            higher_scores += 1
    total_scores = len(scores)
    percentage = (higher_scores / total_scores) * 100
    return percentage

def extract_roll_number(email):
    if email is None:
        return None
    
    if '20' in email:
        se = re.sub(r'^(.*?)20', 'se20', str(email))
        roll_number_match = re.search(r'^[^@]+', se)

    elif '19' in email:
        se = re.sub(r'^(.*?)19', 'se19', str(email))
        roll_number_match = re.search(r'^[^@]+', se)

    else:
        roll_number_match = re.search(r'^[^@]+', str(email))

    if roll_number_match:
        roll_number = roll_number_match.group(0)
    else:
        roll_number = None

    return roll_number

def extraction(email):
    year_match = re.search(r'\d+', str(email))
    if year_match:
        year = year_match.group(0)
    else:
        year = None

    branch_match = re.search(r'\d+(.*?)\d+', str(email))
    if branch_match:
        branch = branch_match.group(1)
    else:
        branch = None

    return year, branch

def calculate_current_semester(batch_year):
    current_month = datetime.now().month
    current_year = datetime.now().year

    completed_semesters = ((current_year - batch_year) * 12 + current_month - 1 - 6) // 6

    completed_semesters = min(completed_semesters, 8)

    current_semester = completed_semesters + 1

    return current_semester
