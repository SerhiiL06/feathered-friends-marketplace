"""
LiqPay Python SDK
~~~~~~~~~~~~~~~~~
supports python 3 version
requires requests module
"""

__title__ = "LiqPay Python SDK"
__version__ = "1.0"

import base64
import hashlib
import json
from copy import deepcopy
from urllib.parse import urljoin

import requests

from . import config


class ParamValidationError(Exception):
    pass


class LiqPay(object):
    _supportedCurrencies = ["EUR", "USD", "UAH"]
    _supportedLangs = ["uk", "ru", "en"]
    _supportedActions = ["pay", "hold", "subscribe", "paydonate"]

    _button_translations = {"ru": "Оплатить", "uk": "Сплатити", "en": "Pay"}

    _FORM_TEMPLATE = """
        <form method="POST" action="{action}" accept-charset="utf-8">
            <input type="hidden" name="data" value="{data}" />
            <input type="hidden" name="signature" value="{signature}" />
            <script type="text/javascript" src="https://static.liqpay.ua/libjs/sdk_button.js"></script>
            <sdk-button label="{label}" background="#77CC5D" onClick="submit()"></sdk-button>
        </form>
    """

    SUPPORTED_PARAMS = [
        "public_key",
        "amount",
        "currency",
        "description",
        "order_id",
        "result_url",
        "server_url",
        "type",
        "signature",
        "language",
        "version",
        "action",
    ]

    def __init__(self, public_key, private_key, host="https://www.liqpay.ua/api/"):
        self._public_key = public_key
        self._private_key = private_key
        self._host = host

    def _make_signature(self, private_key, data):
        str_to_sign = private_key + data + private_key
        sha1_hash = hashlib.sha1(str_to_sign.encode("utf-8")).digest()
        signature = base64.b64encode(sha1_hash).decode("ascii")
        return signature

    def _prepare_params(self, params):
        params = {} if params is None else deepcopy(params)
        params.update(public_key=self._public_key)
        return params

    def api(self, url, params=None):
        params = self._prepare_params(params)
        print(params)
        params_validator = (
            ("version", lambda x: x is not None),
            ("action", lambda x: x is not None),
        )
        for key, validator in params_validator:
            if validator(params.get(key)):
                continue
            raise ParamValidationError("Invalid param: '{}'".format(key))

        encoded_data, signature = self.get_data_end_signature("api", params)

        request_url = urljoin(self._host, url)
        request_data = {"data": encoded_data, "signature": signature}
        response = requests.post(request_url, data=request_data, verify=True)
        return json.loads(response.content.decode("utf-8"))

    def cnb_form(self, params):
        params = self._prepare_params(params)

        params_validator = (
            ("version", lambda x: x is not None),
            ("amount", lambda x: x is not None and float(x) > 0),
            ("currency", lambda x: x is not None and x in self._supportedCurrencies),
            ("action", lambda x: x is not None),
            ("description", lambda x: x is not None and isinstance(x, str)),
        )
        for key, validator in params_validator:
            if validator(params.get(key)):
                continue

            raise ParamValidationError("Invalid param: '{}'".format(key))

        if "language" in params:
            language = params["language"].lower()
            if language not in self._supportedLangs:
                params["language"] = "uk"
                language = "uk"
        else:
            language = "uk"

        encoded_data, signature = self.get_data_end_signature("cnb_form", params)

        form_action_url = urljoin(self._host, "3/checkout/")
        return self._FORM_TEMPLATE.format(
            action=form_action_url,
            data=encoded_data,
            signature=signature,
            label=self._button_translations[language],
        )

    def get_data_end_signature(self, type, params):
        json_encoded_params = json.dumps(params, sort_keys=True)
        if type == "cnb_form":
            bytes_data = json_encoded_params.encode("utf-8")
            base64_encoded_params = base64.b64encode(bytes_data).decode("utf-8")
            signature = self._make_signature(self._private_key, base64_encoded_params)
            return base64_encoded_params, signature
        else:
            signature = self._make_signature(self._private_key, json_encoded_params)
        return json_encoded_params, signature

    def cnb_signature(self, params):
        params = self._prepare_params(params)
        data_to_sign = self.data_to_sign(params)
        return self._make_signature(self._private_key, data_to_sign)

    def cnb_data(self, params):
        params = self._prepare_params(params)
        return self.data_to_sign(params)

    def str_to_sign(self, str):
        return base64.b64encode(hashlib.sha1(str.encode("utf-8")).digest()).decode(
            "ascii"
        )

    def data_to_sign(self, params):
        json_encoded_params = json.dumps(params, sort_keys=True)
        bytes_data = json_encoded_params.encode("utf-8")
        return base64.b64encode(bytes_data).decode("utf-8")

    def decode_data_from_str(self, data, signature=None):
        """Decoding data that were encoded by base64.b64encode(str)

        Args:
            data: json string with api params and encoded by base64.b64encode(str).
            signature: signature received from LiqPay (optional).

        Returns:
            Dict

        Raises:
            ParamValidationError: If the signature is provided and is invalid.

        """
        if signature:
            expected_signature = self._make_signature(
                self._private_key, base64.b64decode(data).decode("utf-8")
            )
            if expected_signature != signature:
                raise ParamValidationError("Invalid signature")

        return json.loads(base64.b64decode(data).decode("utf-8"))


class LiqPayTools:
    __PUBLIC_KEY = config.PUBLIC_KEY
    __PRIVATE_KEY = config.PRIVATE_KEY

    def __init__(self):
        self.liqpay = LiqPay(self.__PUBLIC_KEY, self.__PRIVATE_KEY)

    def generate_pay_link(self, order_data):

        description = f"Order by {order_data['recipient_data']['user']['first_name']} {order_data['recipient_data']['user']['first_name']}"
        # Дані для відправки на LiqPay
        data = {
            "version": "3",
            "public_key": self.__PUBLIC_KEY,
            "private_key": self.__PRIVATE_KEY,
            "action": "pay",
            "amount": order_data["total_price"],
            "currency": "UAH",
            "result_url": f"http://127.0.0.1:8000/success-pay",
            "server_url": f"http://127.0.0.1:8000/verify-order",
            "description": description,
            "order_id": str(order_data["_id"]),
        }

        data_to_sign = self.liqpay.data_to_sign(data)

        params = {"data": data_to_sign, "signature": self.liqpay.cnb_signature(data)}
        try:
            response = requests.post(
                url="https://www.liqpay.ua/api/3/checkout/", data=params
            )
            if response.status_code == 200:
                return response.url

            return response.status_code
        except:
            return 400

    def check_pay_status(self, order_id):

        data = {
            "version": "3",
            "public_key": config.PUBLIC_KEY,
        }

        data["action"] = "status"
        data["order_id"] = order_id
        response = self.liqpay.api("request", data)

        return response
