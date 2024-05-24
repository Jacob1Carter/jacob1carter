from flask import Flask, render_template, request, redirect
import requests

carterapi_baseurl = "https://carterapi.pythonanywhere.com/"

app = Flask(__name__)


@app.route("/")
def index():
    return render_template("main/index.html", title="Home")


@app.route("/portfolio", methods=["GET", "POST"])
def portfolio():

    config_preset_id = 0
    segment_preset_id = 0

    show_config = False
    show_segment = False

    config_data = None
    segment_data = None

    config_error = None
    segment_error = None

    headers = {
        'x-api-key': "abc",
        'Content-Type': 'application/json'
    }

    if request.method == "POST":
        edit = request.form.get("edit")
        print(edit)
        if edit:
            edit_id = request.form.get(f"{edit}-id")
            print(f"{edit}-id")
            print(edit_id)
            if edit_id and edit_id.isdigit():
                return redirect(f"/portfolio/new-{edit}?id={edit_id}")
            else:
                return redirect(f"/portfolio/new-{edit}")

        else:
            config_preset_id = request.form.get("config-preset-id")
            if config_preset_id:
                request_data = {
                    "id": config_preset_id
                }

                response = requests.post(f"{carterapi_baseurl}/get/portfolio-config", headers=headers, json=request_data).json()
                if response["result"] == "success":
                    show_config = True
                    config_data = response["data"]
                else:
                    config_error = response
            else:
                config_preset_id = 0

            segment_preset_id = request.form.get("segment-preset-id")
            if segment_preset_id:
                pass
            else:
                segment_preset_id = 0

    return render_template(
        "main/portfolio.html",
        title="Edit Portfolio",
        config_id=config_preset_id,
        segment_id=segment_preset_id,
        show_config=show_config,
        show_segment=show_segment,
        config_data=config_data,
        segment_data=segment_data,
        config_error=config_error,
        segment_error=segment_error
    )


@app.route("/portfolio/new-config", methods=["GET", "POST"])
def new_config():
    config_id = request.args.get("id")
    if config_id:
        request_data = {
            "id": config_id
        }
    else:
        request_data = {
        }

    headers = {
        'x-api-key': "abc",
        'Content-Type': 'application/json'
    }

    error = None

    response = requests.post(f"{carterapi_baseurl}/get/portfolio-config", headers=headers, json=request_data).json()
    if response["result"] == "success":
        data = response["data"]
    else:
        data = None
        error = response

    return render_template(
        "main/new-config.html",
        title="New Portfolio Config",
        data=data,
        error=error
    )


@app.route("/portfolio/new-segment", methods=["GET", "POST"])
def new_segment():
    return render_template("main/new-segment.html", title="New Portfolio Segment")


if __name__ == '__main__':
    app.run()
