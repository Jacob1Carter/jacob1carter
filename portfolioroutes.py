from flask import session, Blueprint, render_template, request, redirect

portfolio = Blueprint("portfolio", __name__)

@portfolio.route("/")
def portfolio_index():
    return "not yet implemented"