import requests
import json, hmac, hashlib, time
from datetime import datetime
import os
from dotenv import load_dotenv

BASE_URL = "https://api.coin.z.com/"
LINE_NOTIFY_URL = "https://notify-api.line.me/api/notify"
USE_LINE_NOTIFY = True

load_dotenv()
API_KEY = os.environ.get("API_KEY")
SECRET_KEY = os.environ.get("SECRET_KEY")
LOT = int(os.environ.get("LOT"))
ACCESS_TOKEN = os.environ.get("ACCESS_TOKEN")


def public_api(path: str):
    endPoint = BASE_URL + "public"
    return requests.get(endPoint + path)


def private_api(method: str, path: str, parameters: dict = {}):
    timestamp = "{0}000".format(int(time.mktime(datetime.now().timetuple())))
    endPoint = BASE_URL + "private"

    if method == "GET":
        text = timestamp + method + path
    if method == "POST":
        text = timestamp + method + path + ("" if parameters == {} else json.dumps(parameters))

    sign = hmac.new(bytes(SECRET_KEY.encode("ascii")), bytes(text.encode("ascii")), hashlib.sha256).hexdigest()

    headers = {"API-KEY": API_KEY, "API-TIMESTAMP": timestamp, "API-SIGN": sign}

    if method == "GET":
        return requests.get(endPoint + path, headers=headers)
    if method == "POST":
        return requests.post(endPoint + path, headers=headers, data=json.dumps(parameters))


def get_available_amount():
    res = private_api("GET", "/v1/account/margin")
    return int(res.json()["data"]["availableAmount"])


def get_btc_ask_price():
    res = public_api("/v1/ticker?symbol=BTC")
    return int(res.json()["data"][0]["ask"])


def get_min_order_size():
    res = public_api("/v1/symbols")
    return float(res.json()["data"][0]["minOrderSize"])


def place_market_order(size: float):
    market_order = {
        "symbol": "BTC",
        "side": "BUY",
        "executionType": "MARKET",
        "size": str(size),
    }
    res = private_api("POST", "/v1/order", market_order)
    return res.json()


def get_execution(orderId: int):
    # not working
    res = private_api("GET", f"/v1/executions", {"orderId": orderId})
    print(res)
    return res.json()


def send_line_message(message: str):
    if not USE_LINE_NOTIFY:
        return

    headers = {
        "Authorization": f"Bearer {ACCESS_TOKEN}",
        "Content-Type": "application/x-www-form-urlencoded",
    }
    payload = {"message": "\n" + message}

    requests.post(LINE_NOTIFY_URL, headers=headers, data=payload)


if __name__ == "__main__":
    try:
        # 注文情報の取得 / get general info for order
        available_amount = get_available_amount()
        print("available_amount: ", available_amount)
        if LOT > available_amount:
            raise ValueError(f"余力が不足しています。\n(現在余力: {available_amount:,}円)")
        btc_price = get_btc_ask_price()
        print("btc_price: ", btc_price)
        min_order_size = get_min_order_size()
        print("min_order_size: ", min_order_size)

        # 購入金額の計算 / calc amount to order
        order_size = round(int(LOT / btc_price / min_order_size) * min_order_size, 8)
        print("order_size: ", order_size)

        orderResult = place_market_order(order_size)
        if not orderResult["status"] == 0:
            raise RuntimeError(f"{orderResult['messages']}")

        order_id = int(orderResult["data"])
        print("order_id: ", order_id)

        # BTC購入後の余力から購入レートを計算 / calc bought price based on balance change
        time.sleep(2)
        new_available_amount = get_available_amount()
        used_jpy = available_amount - new_available_amount
        print("used_jpy: ", used_jpy)
        estimated_price = int(used_jpy / order_size)
        print("estimated_price: ", estimated_price)
        send_line_message(
            f"【今日のBTC購入】\n推定購入レート: {estimated_price:,}円\n購入数量: {order_size}BTC\n購入金額: {used_jpy:,}円\n現在余力: {new_available_amount:,}円"
        )

        # 次回購入時に余力が不足している場合に警告 / send caution if available JPY is not enough for next purchase
        if LOT > new_available_amount:
            send_line_message(f"次回購入のための余力が不足しています。")

    except Exception as e:
        print(f"Error: {e}")
        send_line_message(f"エラー: {e}")
