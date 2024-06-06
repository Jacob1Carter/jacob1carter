from flask import Flask, render_template, request, redirect
import requests
import base64
import json

carterapi_baseurl = "http://127.0.0.1:5000/"

app = Flask(__name__)


HEADERS = {
        'x-api-key': "t13y01789638d2L3Kk8rsj56hg789m7j",
        'Content-Type': 'application/json'
    }


def encode_image(image):
    image_data = image.read()
    base64_image = base64.b64encode(image_data).decode('utf-8')

    return base64_image


def to_rgba(hex_colour, transparency):
    hex_colour = hex_colour.lstrip('#')
    r = int(hex_colour[0:2], 16)
    g = int(hex_colour[2:4], 16)
    b = int(hex_colour[4:6], 16)

    return f"rgba({r}, {g}, {b}, {transparency})"


def from_rgba(rgba):
    rgba = rgba.split("(")[1].split(")")[0]
    r, g, b, a = rgba.split(", ")
    r = int(r)
    g = int(g)
    b = int(b)

    return f"#{r:02x}{g:02x}{b:02x}", str(a)


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

                response = requests.post(f"{carterapi_baseurl}/get/portfolio-config", headers=HEADERS, json=request_data).json()
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

                response = requests.post(f"{carterapi_baseurl}/get/portfolio-segment", headers=HEADERS, json=request_data).json()
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

    post_error = None
    post_response = None
    error = None

    if config_id == "0":
        data = None
    else:
        response = requests.post(f"{carterapi_baseurl}/get/portfolio-config", headers=HEADERS, json=request_data).json()
        if response["result"] == "success":
            data = response["data"]
            data["colours"]["light"]["p-t-colour"], data["colours"]["light"]["p-t-colour-transparency"] = from_rgba(data["colours"]["light"]["p-t-colour"])
            data["colours"]["light"]["s-t-colour"], data["colours"]["light"]["s-t-colour-transparency"] = from_rgba(data["colours"]["light"]["s-t-colour"])

            data["colours"]["dark"]["p-t-colour"], data["colours"]["dark"]["p-t-colour-transparency"] = from_rgba(data["colours"]["dark"]["p-t-colour"])
            data["colours"]["dark"]["s-t-colour"], data["colours"]["dark"]["s-t-colour-transparency"] = from_rgba(data["colours"]["dark"]["s-t-colour"])
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
            "favicon": "",
            "colours": {
                "light": {
                    "main-colour": request.form.get("main-colour-light"),
                    "off-colour": request.form.get("off-colour-light"),

                    "bg-colour-1": request.form.get("bg-colour-1-light"),
                    "bg-colour-2": request.form.get("bg-colour-2-light"),

                    "p-s-colour": request.form.get("p-s-colour-light"),
                    "p-t-colour": to_rgba(request.form.get("p-t-colour-light"), request.form.get("p-t-colour-transparency-light")),
                    "p-a-colour": request.form.get("p-a-colour-light"),

                    "s-s-colour": request.form.get("s-s-colour-light"),
                    "s-t-colour": to_rgba(request.form.get("s-t-colour-light"), request.form.get("s-t-colour-transparency-light"))
                },
                "dark": {
                    "main-colour": request.form.get("main-colour-dark"),
                    "off-colour": request.form.get("off-colour-dark"),

                    "bg-colour-1": request.form.get("bg-colour-1-dark"),
                    "bg-colour-2": request.form.get("bg-colour-2-dark"),

                    "p-s-colour": request.form.get("p-s-colour-dark"),
                    "p-t-colour": to_rgba(request.form.get("p-t-colour-dark"), request.form.get("p-t-colour-transparency-dark")),
                    "p-a-colour": request.form.get("p-a-colour-dark"),

                    "s-s-colour": request.form.get("s-s-colour-dark"),
                    "s-t-colour": to_rgba(request.form.get("s-t-colour-dark"), request.form.get("s-t-colour-transparency-dark"))
                }
            }
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

        response = requests.post(f"{carterapi_baseurl}/post/new/portfolio-config", headers=HEADERS, json=new_data).json()
        if response["result"] == "success":
            post_response = response
        else:
            post_error = response

        response = requests.post(f"{carterapi_baseurl}/get/portfolio-config", headers=HEADERS, json={}).json()
        if response["result"] == "success":
            data = response["data"]

            data["colours"]["light"]["p-t-colour"], data["colours"]["light"]["p-t-colour-transparency"] = from_rgba(data["colours"]["light"]["p-t-colour"])
            data["colours"]["light"]["s-t-colour"], data["colours"]["light"]["s-t-colour-transparency"] = from_rgba(data["colours"]["light"]["s-t-colour"])

            data["colours"]["dark"]["p-t-colour"], data["colours"]["dark"]["p-t-colour-transparency"] = from_rgba(data["colours"]["dark"]["p-t-colour"])
            data["colours"]["dark"]["s-t-colour"], data["colours"]["dark"]["s-t-colour-transparency"] = from_rgba(data["colours"]["dark"]["s-t-colour"])
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

    segment_id = request.args.get("id")
    if segment_id:
        request_data = {
            "id": segment_id
        }

        response = requests.post(f"{carterapi_baseurl}/get/portfolio-segment", headers=HEADERS, json=request_data).json()
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
                elif data is not None:
                    img_index = key[-1]
                    if img_index.isdigit():
                        if int(img_index) + 1 <= len(data["images"]):
                            new_data["images"].append(data["images"][int(img_index)])

        for key in request.form:
            if key.startswith("linkname"):
                link_id = key[-1]
                if request.form[key] != "" and request.form[f"linkurl{link_id}"] != "":
                    new_data["links"][request.form[key]] = request.form[f"linkurl{link_id}"]

        response = requests.post(f"{carterapi_baseurl}/post/new/portfolio-segment", headers=HEADERS, json=new_data).json()
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
        post_error=post_error,
        segment_id=segment_id,
    )


@app.route("/jiujitsu", methods=["GET", "POST"])
def jiujitsu():

    return render_template("main/jiujitsu.html", title="Jiu Jitsu")


@app.route("/jiujitsu/new-technique", methods=["GET", "POST"])
def new_technique():
    types = {
        "strike": ["test1", "test2"],
        "throw": ["test3", "test4"],
    }

    techniques = {
        "id": {"name_en", "name_jp"}
    }
    return render_template("main/new-technique.html", title="New Technique", types=types)


if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5001)
