from flask import session, Blueprint, render_template, request, redirect

convert = Blueprint("convert", __name__)

@convert.route("/")
def convert_index():
    return render_template("convert/index.html")


@convert.route("/youtube")
def convert_youtube():
    return render_template("convert/youtube.html")