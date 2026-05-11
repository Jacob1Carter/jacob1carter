from flask import session, Blueprint, render_template, request, redirect

api = Blueprint("api", __name__)

@api.route("/")
def api_index():
    return "not yet implemented"