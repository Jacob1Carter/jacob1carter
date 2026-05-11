from flask import session, Blueprint, render_template, request, redirect

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("main/dashboard.html", title="Dashboard")