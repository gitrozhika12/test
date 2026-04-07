"""Utility functions."""
import uuid
import random
import string
import hashlib
import json
import pyotp
from config import *


def generate_device():
    device_id = str(uuid.uuid4())
    adid = str(uuid.uuid4())
    family_device_id = str(uuid.uuid4())
    mfr, dev = random.choice(DEVICES)
    android_ver = random.choice(ANDROID_VERSIONS)
    density = random.choice(DENSITIES)
    width, height = random.choice(RESOLUTIONS)
    carrier = random.choice(CARRIERS)

    user_agent = (
        f"[FBAN/PAAA;FBAV/{FBAV};"
        f"FBDM/{{density={density},width={width},height={height}}};"
        f"FBLC/en_US;FBBV/{FBBV};FB_FW/2;FBSN/Android;"
        f"FBDI/{device_id};FBCR/{carrier};"
        f"FBMF/{mfr};FBBD/{mfr};FBDV/{dev};"
        f"FBSV/{android_ver};FBCA/arm64-v8a:null;]"
    )

    return {
        "device_id": device_id,
        "adid": adid,
        "family_device_id": family_device_id,
        "user_agent": user_agent,
    }


def generate_totp(secret):
    try:
        totp = pyotp.TOTP(secret)
        return totp.now()
    except Exception:
        return None


def build_headers(device_id, user_agent):
    return {
        "Host": "b-graph.facebook.com",
        "X-FB-Request-Analytics-Tags": json.dumps({
            "network_tags": {"product": API_KEY, "retry_attempt": "0"},
            "application_tags": "unknown",
        }),
        "X-FB-Connection-Type": "WIFI",
        "app-scope-id-header": str(uuid.uuid4()),
        "Content-Type": "application/x-www-form-urlencoded",
        "X-FB-SIM-HNI": str(random.randrange(47000, 48000)),
        "X-FB-Net-HNI": str(random.randrange(47000, 48000)),
        "X-ZERO-F-DEVICE-ID": device_id,
        "X-FB-Friendly-Name": "authenticate",
        "X-ZERO-STATE": "unknown",
        "X-FB-Connection-Quality": "GOOD",
        "x-zero-eh": hashlib.md5(device_id.encode()).hexdigest(),
        "User-Agent": user_agent,
        "Authorization": "OAuth null",
        "x-tigon-is-retry": "False",
        "Accept-Encoding": "gzip, deflate",
        "X-FB-HTTP-Engine": "Tigon/Liger",
        "x-fb-client-ip": "True",
        "x-fb-server-cluster": "True",
        "Connection": "keep-alive",
    }


def random_page_name():
    return random.choice(PAGE_NAMES) + str(random.randint(100, 9999))


def random_category():
    return random.choice(PAGE_CATEGORIES)


def load_accounts(filepath):
    accounts = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                parts = line.split("|")
                if len(parts) >= 3:
                    accounts.append({
                        "phone": parts[0],
                        "password": parts[1],
                        "totp_secret": parts[2],
                    })
    return accounts


def load_proxies(filepath):
    proxies = []
    with open(filepath) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                proxies.append(line)
    return proxies


GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
RESET = "\033[0m"
BOLD = "\033[1m"

def log_success(msg): print(f"{GREEN}[+] {msg}{RESET}")
def log_error(msg): print(f"{RED}[-] {msg}{RESET}")
def log_warn(msg): print(f"{YELLOW}[!] {msg}{RESET}")
def log_info(msg): print(f"{CYAN}[*] {msg}{RESET}")
