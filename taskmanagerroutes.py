from flask import session, Blueprint, render_template, request, redirect

tm = Blueprint("taskmanager", __name__)

@tm.route("/")
def tm_index():
    return ""