"""Configuration constants."""
import json
import uuid
import random
import hashlib

API_KEY = "121876164619130"
APP_SECRET = "1ab2c5c902faedd339c14b2d58e929dc"
ACCESS_TOKEN = f"{API_KEY}|{APP_SECRET}"
FBAV = "517.0.0.43.109"
FBBV = "775644512"

LOGIN_URL = "https://b-graph.facebook.com/auth/login"
GRAPH_URL = "https://graph.facebook.com"

DEVICES = [
    ("TECNO", "TECNO CK7n"), ("Samsung", "SM-A127F"), ("Samsung", "SM-G991B"),
    ("Xiaomi", "Redmi Note 11"), ("OPPO", "CPH2219"), ("Vivo", "V2111"),
    ("Realme", "RMX3740"), ("Huawei", "JNY-LX1"),
]
CARRIERS = ["Teletalk", "Banglalink", "Grameenphone", "Robi", "T-Mobile", "Vodafone"]
ANDROID_VERSIONS = ["11", "12", "13", "14"]
DENSITIES = ["2.0", "2.75", "2.7375", "3.0"]
RESOLUTIONS = [("1080", "2400"), ("1080", "2292"), ("720", "1600"), ("1440", "2560")]

PAGE_NAMES = ["Shop", "Store", "Tech", "Media", "Studio", "Hub", "Zone", "Point", "Spot", "Base"]
PAGE_CATEGORIES = ["INTERNET_COMPANY", "LOCAL_BUSINESS", "FOOD_BEVERAGE", "SHOPPING_RETAIL", "FINANCIAL_SERVICE"]

PASSWORD_FORMATS = ["#PWD_PAAA:0", "#PWD_FB4A:0"]
