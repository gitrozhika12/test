"""API client module."""
import time
import string
import random
import hashlib
import uuid
import json
import requests

from config import *
from utils import generate_device, generate_totp, build_headers


class MetaBusinessAPI:
    def __init__(self, proxy=None):
        self.session = requests.Session()
        self.session.verify = True
        self.timeout = 30
        if proxy:
            self.session.proxies = {"http": proxy, "https": proxy}
        self.device = generate_device()
        self.headers = build_headers(self.device["device_id"], self.device["user_agent"])
        self.access_token = None
        self.uid = None

    def _build_login_data(self, phone, password, pwd_prefix):
        ts = str(int(time.time()))
        return {
            "adid": self.device["adid"],
            "format": "json",
            "device_id": self.device["device_id"],
            "email": phone,
            "password": f"{pwd_prefix}:{ts}:{password}",
            "generate_analytics_claim": "1",
            "community_id": "",
            "cpl": "true",
            "family_device_id": self.device["family_device_id"],
            "secure_family_device_id": "",
            "credentials_type": "password",
            "generate_session_cookies": "1",
            "generate_machine_id": "1",
            "jazoest": str(22000 + random.randrange(0, 1000)),
            "meta_inf_fbmeta": "NO_FILE",
            "advertiser_id": self.device["adid"],
            "currently_logged_in_userid": "0",
            "locale": "en_US",
            "client_country_code": "US",
            "fb_api_req_friendly_name": "authenticate",
            "fb_api_caller_class": "AuthOperations$PasswordAuthOperation",
            "api_key": API_KEY,
            "sig": hashlib.md5(str(uuid.uuid4()).encode()).hexdigest(),
            "access_token": ACCESS_TOKEN,
        }

    def login(self, phone, password, totp_secret):
        last_error = None

        for pwd_prefix in PASSWORD_FORMATS:
            login_data = self._build_login_data(phone, password, pwd_prefix)

            try:
                resp = self.session.post(
                    LOGIN_URL, data=login_data, headers=self.headers, timeout=self.timeout
                )
                result = resp.json()
            except Exception as e:
                last_error = str(e)
                continue

            if "access_token" in result and "session_key" in result:
                self.access_token = result["access_token"]
                self.uid = result.get("uid")
                return {"success": True, "access_token": self.access_token, "uid": self.uid}

            error = result.get("error", {})
            error_code = error.get("code")
            error_data = error.get("error_data", {})

            if isinstance(error_data, str):
                try:
                    error_data = json.loads(error_data)
                except Exception:
                    error_data = {}

            if error_code == 406 or "login_first_factor" in str(error_data):
                totp_code = generate_totp(totp_secret)
                if not totp_code:
                    return {"success": False, "error": "Invalid TOTP secret"}

                tfa_data = login_data.copy()
                tfa_data["twofactor_code"] = totp_code
                tfa_data["userid"] = str(error_data.get("uid", ""))
                tfa_data["machine_id"] = error_data.get("machine_id", "")
                tfa_data["first_factor"] = error_data.get("login_first_factor", "")
                tfa_data["credentials_type"] = "two_factor"

                try:
                    resp2 = self.session.post(
                        LOGIN_URL, data=tfa_data, headers=self.headers, timeout=self.timeout
                    )
                    result2 = resp2.json()
                except Exception as e:
                    return {"success": False, "error": f"2FA request failed: {e}"}

                if "access_token" in result2 and "session_key" in result2:
                    self.access_token = result2["access_token"]
                    self.uid = result2.get("uid")
                    return {"success": True, "access_token": self.access_token, "uid": self.uid}
                else:
                    err2 = result2.get("error", {})
                    return {"success": False, "error": f"2FA failed: {err2.get('message', str(result2))}"}

            last_error = error.get("message", str(result))

        return {"success": False, "error": last_error or "All password formats failed"}

    def create_page(self, name=None, category=None):
        if not self.access_token:
            return {"success": False, "error": "Not logged in"}

        from utils import random_page_name, random_category
        name = name or random_page_name()
        category = category or random_category()

        try:
            resp = self.session.post(
                f"{GRAPH_URL}/v19.0/me/accounts",
                data={
                    "access_token": self.access_token,
                    "name": name,
                    "category_enum": category,
                    "about": name,
                },
                timeout=self.timeout,
            )
            result = resp.json()
            if "id" in result:
                return {"success": True, "page_id": result["id"], "name": name}
        except Exception:
            pass

        try:
            resp = self.session.post(
                f"{GRAPH_URL}/graphql",
                data={
                    "access_token": self.access_token,
                    "method": "post",
                    "format": "json",
                    "locale": "en_US",
                    "fb_api_req_friendly_name": "PageCreationMutation",
                    "fb_api_caller_class": "graphservice",
                    "variables": json.dumps({
                        "input": {
                            "name": name,
                            "category_id": category,
                            "client_mutation_id": str(uuid.uuid4()),
                        }
                    }),
                    "server_timestamps": "true",
                },
                timeout=self.timeout,
            )
            result = resp.json()
            page_id = None
            if "data" in result:
                page_id = str(result["data"])
            return {"success": bool(page_id), "page_id": page_id, "name": name, "raw": result}
        except Exception as e:
            return {"success": False, "error": str(e), "name": name}
