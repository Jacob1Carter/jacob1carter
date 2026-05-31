from flask import Flask, render_template, request, redirect
from mainroutes import main
from apiroutes import api
from taskmanagerroutes import tm
from portfolioroutes import portfolio
from convert import convert

app = Flask(__name__)
app.secret_key = "b'+=\x02\x1eLN\x8dM\xf9\xc7L\xb0\x9b\xe8\x1c\x1c=i28\x021\xb0/'"

app.register_blueprint(main)
app.register_blueprint(api, url_prefix="/api")
app.register_blueprint(tm, url_prefix="/taskmanager")
app.register_blueprint(portfolio, url_prefix="/portfolio")
app.register_blueprint(convert, url_prefix="/convert")


if __name__ == "__main__":
    app.run()
