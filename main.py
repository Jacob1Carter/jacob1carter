from flask import Flask, render_template, request, redirect
import requests
import base64

carterapi_baseurl = "https://carterapi.pythonanywhere.com/"

app = Flask(__name__)


def encode_image(image):
    image_data = image.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')

    return base64_image


@app.route("/")
def index():
    return render_template("main/index.html", title="Home")


@app.route("/portfolio", methods=["GET", "POST"])
def portfolio():

    config_preset_id = 0
    segment_preset_id = 0

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
        if edit:
            edit_id = request.form.get(f"{edit}-id")
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
                    config_data = response["data"]
                else:
                    config_error = response
            else:
                config_preset_id = 0

            segment_preset_id = request.form.get("segment-preset-id")
            if segment_preset_id:
                request_data = {
                    "id": segment_preset_id
                }

                response = requests.post(f"{carterapi_baseurl}/get/portfolio-segment", headers=headers, json=request_data).json()
                if response["result"] == "success":
                    segment_data = response["data"]
                else:
                    segment_error = response

    return render_template(
        "main/portfolio.html",
        title="Edit Portfolio",
        config_id=config_preset_id,
        segment_id=segment_preset_id,
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

    post_error = None
    post_response = None
    error = None

    if config_id == "0":
        data = None
    else:
        response = requests.post(f"{carterapi_baseurl}/get/portfolio-config", headers=headers, json=request_data).json()
        if response["result"] == "success":
            data = response["data"]
        else:
            data = None
            error = response

    if request.method == "POST":

        new_data = {
            "pagename": request.form.get("pagename"),
            "title": request.form.get("title"),
            "bio": request.form.get("bio"),
            "links": {},
            "banners": {},
            "icon": "",
            "segments": [],
            "favicon": ""
        }

        if "icondata" in request.files and request.files[f"icondata"].filename != '':
            icondata = request.files["icondata"]
            new_data["icon"] = encode_image(icondata)
        else:
            new_data["icon"] = data["icon"]

        if "favicondata" in request.files and request.files[f"favicondata"].filename != '':
            favicondata = request.files["favicondata"]
            new_data["favicon"] = encode_image(favicondata)
        else:
            new_data["favicon"] = data["favicon"]

        for key in request.form:
            if key.startswith("linkname"):
                link_id = key[-1]
                if request.form[key] != "" and request.form[f"linkurl{link_id}"] != "":
                    new_data["links"][request.form[key]] = request.form[f"linkurl{link_id}"]

            if key.startswith("bannername"):
                banner_id = key[-1]
                if request.form[key] != "":
                    if f"bannerdata{banner_id}" in request.files and request.files[f"bannerdata{banner_id}"].filename != '':
                        bannerdata = request.files[f"bannerdata{banner_id}"]
                        new_data["banners"][request.form[key]] = encode_image(bannerdata)
                    elif request.form[key] in data["banners"]:
                        new_data["banners"][request.form[key]] = data["banners"][request.form[key]]

            if key.startswith("segment"):
                if request.form[key] != "" and request.form[key].isdigit():
                    new_data["segments"].append(int(request.form[key]))

        response = requests.post(f"{carterapi_baseurl}/post/new/portfolio-config", headers=headers, json=new_data).json()
        if response["result"] == "success":
            post_response = response
        else:
            post_error = response

        response = requests.post(f"{carterapi_baseurl}/get/portfolio-config", headers=headers, json={}).json()
        if response["result"] == "success":
            data = response["data"]
        else:
            data = None
            error = response

    return render_template(
        "main/new-config.html",
        title="New Portfolio Config",
        data=data,
        error=error,
        post_response=post_response,
        post_error=post_error
    )


@app.route("/portfolio/new-segment", methods=["GET", "POST"])
def new_segment():
    error = None
    data = None
    post_error = None
    post_response = None

    headers = {
        'x-api-key': "abc",
        'Content-Type': 'application/json'
    }

    config_id = request.args.get("id")
    if config_id:
        request_data = {
            "id": config_id
        }

        response = requests.post(f"{carterapi_baseurl}/get/portfolio-segment", headers=headers, json=request_data).json()
        if response["result"] == "success":
            data = response["data"]
        else:
            error = response

    if request.method == "POST":

        new_data = {
            "name": request.form.get("name"),
            "title": request.form.get("title"),
            "text": request.form.get("text"),
            "images": [],
            "icon": "",
            "links": {}
        }

        if "icondata" in request.files and request.files[f"icondata"].filename != '':
            icondata = request.files["icondata"]
            new_data["icon"] = encode_image(icondata)
        elif data is not None:
            new_data["icon"] = data["icon"]

        # loop through request.files:
        for key in request.files:
            if key.startswith("image"):
                if request.files[key].filename != '':
                    new_data["images"].append(encode_image(request.files[key]))

        for key in request.form:
            if key.startswith("linkname"):
                link_id = key[-1]
                if request.form[key] != "" and request.form[f"linkurl{link_id}"] != "":
                    new_data["links"][request.form[key]] = request.form[f"linkurl{link_id}"]

        response = requests.post(f"{carterapi_baseurl}/post/new/portfolio-segment", headers=headers, json=new_data).json()
        if response["result"] == "success":
            post_response = response
        else:
            post_error = response

        data = None

    return render_template(
        "main/new-segment.html",
        title="New Portfolio Segment",
        data=data,
        error=error,
        post_response=post_response,
        post_error=post_error
    )


if __name__ == '__main__':
    app.run("0.0.0.0", 5001)
