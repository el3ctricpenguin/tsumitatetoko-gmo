import requests
import json, hmac, hashlib, time
from datetime import datetime
import os
from dotenv import load_dotenv

BASE_URL = "https://api.coin.z.com/"

load_dotenv()
API_KEY = os.environ.get("API_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
LOT = int(os.environ.get("LOT"))


def private_api(method: str, path: str):
    timestamp = "{0}000".format(int(time.mktime(datetime.now().timetuple())))
    endPoint = BASE_URL + "private"
    reqBody = {}

    text = timestamp + method + path + "" if reqBody == {} else json.dumps(reqBody)
    sign = hmac.new(bytes(SECRET_KEY.encode("ascii")), bytes(text.encode("ascii")), hashlib.sha256).hexdigest()

    headers = {"API-KEY": API_KEY, "API-TIMESTAMP": timestamp, "API-SIGN": sign}

    if method == "GET":
        return requests.get(endPoint + path, headers=headers)
    if method == "POST":
        return requests.post(endPoint + path, headers=headers)


def get_available_amount():
    res = private_api("GET", "/v1/account/margin")
    return res.json()["data"]["availableAmount"]


if __name__ == "__main__":
    available_amount = int(get_available_amount())
    print("available_amount: ", available_amount)
    if LOT > available_amount:
        raise ValueError("余力が不足しています。")
