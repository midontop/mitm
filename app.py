from flask import Flask, request, Response, render_template, redirect
from werkzeug.middleware.proxy_fix import ProxyFix
import requests
import sys
import pickle
import json
import os
from datetime import datetime, timedelta
import logging
import importlib
from pathlib import Path
import dotenv

# If using MITM Proxy
# proxy = 'http://localhost:8080'

# os.environ['http_proxy'] = proxy 
# os.environ['HTTP_PROXY'] = proxy
# os.environ['https_proxy'] = proxy
# os.environ['HTTPS_PROXY'] = proxy

dotenv.load_dotenv(".env")



if os.path.exists("config.json"):
    with open("config.json", "r") as f:
        config = json.load(f)
else:
    with open("config.json", "w") as f:
        json.dump(
            {
                "weekly": "online",
                "offline_weekly": False,
                "offline_normal": False,
                "download_replays": False,
                "account_changer": False,
            },
            f,
        )
    with open("config.json", "r") as f:
        config = json.load(f)

if config["account_changer"]:
    if os.path.exists("creds.json"):
        f = open("creds.json", "r")
        credentials = json.load(f)
        f.close()
    else:
        print("No creds.json file found, please create an account or disable account switcher")
        exit(1)
    f = open("creds.json", "r")
    credentials = json.load(f)
    f.close()

url = "https://1.1.1.1/dns-query"

querystring = {"name": "www.miubackend.net"}

headers = {"accept": "application/dns-json"}

response = requests.get(url, headers=headers, params=querystring)

MIU_IP = response.json()["Answer"][0]["data"]

Path("replays").mkdir(exist_ok=True)

offline_weekly = config["offline_weekly"]
offline_normal = config["offline_normal"]
download_replays = config["download_replays"]
weekly = config["weekly"]
if weekly != "online":
    weekly_data = importlib.import_module("weekly." + weekly)

# Create a Logger object
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG if int(os.environ.get("DEBUG", 0)) == 1 else logging.INFO)
print(os.environ.get("DEBUG", 0))
# Create a FileHandler for outputting logs to a file
fh = logging.FileHandler("debug.log")
console = logging.StreamHandler(sys.stdout)
console.setLevel(logging.DEBUG)
fh.setLevel(logging.DEBUG)
# Create a Formatter
formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
# Add the Formatter to the FileHandler
fh.setFormatter(formatter)
console.setFormatter(formatter)
# Add the FileHandler to the Logger
logger.addHandler(fh)
logger.addHandler(console)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)


@app.route("/api/config", methods=["GET", "POST"])
def api_config():

    print(request.get_data())
    if request.method == "POST":
        body = request.json

        with open("config.json", "r") as f:
            config = json.load(f)
        with open("config.json", "w") as f:
            for key, value in body.items():
                config[key] = value
            json.dump(config, f)
        with open("config.json", "r") as f:
            config = json.load(f)
        offline_weekly = config["offline_weekly"]
        offline_normal = config["offline_normal"]
        account_changer = config["account_changer"]
        download_replays = config["download_replays"]
        weekly = config["weekly"]
        print(f"{offline_weekly=}, {offline_normal=}, {download_replays=}, {weekly=}, {account_changer=}")
        if weekly != "online":
            weekly_data = importlib.import_module("weekly." + weekly)
        else:
            weekly_data = None
        return redirect("/config")
    else:
        with open("config.json", "r") as f:
            res = json.load(f)
            return Response(str(res), content_type="application/json")


@app.route("/config")
def config():
    weeklys = {}
    with open("config.json", "r") as f:
        config = json.load(f)
        offline_weekly = config["offline_weekly"]
        offline_normal = config["offline_normal"]
        download_replays = config["download_replays"]
        account_changer = config["account_changer"]
        weekly = config["weekly"]
    for f in os.listdir("weekly"):
        if f.endswith(".py") and not f.startswith("__init__"):
            m = importlib.import_module("weekly." + f[:-3])
            weeklys[f[:-3]] = m.name
    print(weekly)
    return render_template(
        "config.html",
        weeklys=weeklys,
        offline_weekly=offline_weekly,
        offline_normal=offline_normal,
        download_replays=download_replays,
        account_changer=account_changer,
        weekly=weekly,
    )


@app.route("/", defaults={"path": ""})
@app.route("/<path:path>", methods=["GET", "POST", "PUT", "DELETE"])
def proxy(path):

    target_url = "https://" + MIU_IP + "/"  # Replace with the actual backend URL
    url = f"{target_url}{path}"
    headers = {key: value for (key, value) in request.headers if key != "Host"}
    data = request.get_data()

    with open("config.json", "r") as f:
        config = json.load(f)
        offline_weekly = config["offline_weekly"]
        offline_normal = config["offline_normal"]
        account_changer = config["account_changer"]
        download_replays = config["download_replays"]
        weekly = config["weekly"]
        if weekly != "online":
            weekly_data = importlib.import_module("weekly." + weekly)

    if "/login" in path and account_changer == True:
        
        logger.debug("-------REQUEST------")
        # Log the method, path, query params, body and headers
        logger.debug("Method: %s", request.method)
        logger.debug("Path: %s", path)
        logger.debug("Query Params: %s", request.args)
        logger.debug("Body: %s", data)
        logger.debug("Headers: %s", headers)
        response = requests.request(
            method=request.method,
            url=url,
            headers=headers | {"Host": "www.miubackend.net"},
            data=data,
            cookies=request.cookies,
            params={"username": credentials["username"], "password": credentials["username"]},
            stream=True,
            verify=False,
        )
        logger.debug("-------RESPONSE------")
        # Log the response status code, headers and content
        logger.debug("Status Code: %s", response.status_code)
        logger.debug("Headers: %s", response.headers)
        logger.debug("Content: %s", response.text)
        return Response(
            response.content,
            status=response.status_code,
            content_type=response.headers["content-type"],
            direct_passthrough=True,
        )

    if (
        "ChallengeStats_Mayhem" in path
        and request.args.get("where", "") == '{"LevelID":"CHALLENGE_DATA"}'
        and weekly != "online"
    ):

        logger.debug("-------REQUEST------")
        # Log the method, path, query params, body and headers
        logger.debug("Method: %s", request.method)
        logger.debug("Path: %s", path)
        logger.debug("Query Params: %s", request.args)
        logger.debug("Body: %s", data)
        logger.debug("Headers: %s", headers)

        print("requested challenge!")
        res = Response(
            weekly_data.weekly.replace(
                "placeholder_date",
                (
                    (datetime.utcnow() + timedelta(days=1))
                    .replace(microsecond=0)
                    .isoformat()
                    + "Z"
                ),
            ).replace("\\\\", "\\"),
            status=200,
            mimetype="application/json",
        )

        logger.debug("-------RESPONSE------")
        # Log the response status code, headers and content
        logger.debug("Status Code: %s", res.status_code)
        logger.debug("Headers: %s", res.headers)
        logger.debug("Content: %s", res.data)

        return res

    if "parse/files/" in path and download_replays:
        print("replay?")
        if path.endswith(".replay"):
            if data == b"":
                response = requests.request(
                    method=request.method,
                    url=url,
                    headers=headers | {"Host": "www.miubackend.net"},
                    data=data,
                    cookies=request.cookies,
                    params=request.args.to_dict(),
                    stream=True,
                    verify=False,
                )
                print("Replay request!")
                f = open("replays/" + path.split("/")[-1], "wb")
                f.write(response.content)
                f.close()
            else:
                print("replay!")
                f = open("replays/" + path.split("/")[-1], "wb")
                f.write(data)
                f.close()

    if ("SPLeaderboard_Ultra" in path and offline_normal) or (
        "ChallengeLB_Mayhem" in path and offline_weekly
    ):
        print("Leaderboard stuff found!")
        if json.loads(data)["_noBody"] == False:
            print(
                "Found marble it Up! Ultra PUT to leaderboard. Not forwarding to server... Sending dummy response of "
                + '{"updatedAt":{}}'.replace(
                    "{}", datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
                )
            )
            return Response(
                status=200,
                mimetype="application/json",
                headers={
                    "Access-Control-Allow-Headers": "X-Parse-Master-Key, X-Parse-REST-API-Key, X-Parse-Javascript-Key, X-Parse-Application-Id, X-Parse-Client-Version, X-Parse-Session-Token, X-Requested-With, X-Parse-Revocable-Session, X-Parse-Request-Id, Content-Type, Pragma, Cache-Control",
                    "Access-Control-Allow-Methods": "GET,PUT,POST,DELETE,OPTIONS",
                    "Access-Control-Allow-Origin": "*",
                    "Access-Control-Expose-Headers": "X-Parse-Job-Status-Id, X-Parse-Push-Status-Id",
                    "Content-Type": "application/json; charset=utf-8",
                    "Date": "Sun, 11 Feb 2024 14:37:55 GMT",
                    "ETag": 'W/"28-p1vpCCRF4MD/rxk5IbNdfL9w8jg"',
                    "Server": "nginx/1.4.6 (Ubuntu)",
                    "X-Powered-By": "Express",
                    "Content-Length": "40",
                    "Connection": "keep-alive",
                },
                response='{"updatedAt":{}}'.replace(
                    "{}", datetime.utcnow().replace(microsecond=0).isoformat() + "Z"
                ),
            )
       
    response = requests.request(
        method=request.method,
        url=url,
        headers=headers | {"Host": "www.miubackend.net"},
        data=data,
        cookies=request.cookies,
        params=request.args.to_dict(),
        stream=True,
        verify=False,
    )

    logger.debug("-------REQUEST------")
    # Log the method, path, query params, body and headers
    logger.debug("Method: %s", request.method)
    logger.debug("Path: %s", path)
    logger.debug("Query Params: %s", request.args)
    logger.debug("Body: %s", data)
    logger.debug("Headers: %s", headers)

    logger.debug("-------RESPONSE------")
    # Log the response status code, headers and content
    logger.debug("Status Code: %s", response.status_code)
    logger.debug("Headers: %s", response.headers)
    logger.debug("Content: %s", response.content)

    return Response(
        response.content,
        status=response.status_code,
        content_type=response.headers["content-type"],
        direct_passthrough=True,
    )


if __name__ == "__main__":
    ssl_context = ("cert.pem", "key.pem")
    app.run(host="0.0.0.0", port=443, ssl_context=ssl_context, debug=False)
