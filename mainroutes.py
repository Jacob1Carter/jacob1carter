from flask import session, Blueprint, render_template, request, redirect

main = Blueprint("main", __name__)

@main.route("/")
def index():
    return render_template("main/dashboard.html", title="Dashboard")

@main.route("/notif")
def notif_demo():
    return render_template("main/notif.html")