import hashlib
import os
import requests

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

def sanitize_filename(name):
    return hashlib.md5(name.encode()).hexdigest() + ".png"

def fetch_price(skin_name, currency=1):
    url = "https://steamcommunity.com/market/priceoverview/"
    params = {
        'appid': 730,
        'currency': currency,
        'market_hash_name': skin_name
    }

    searchImgUrl = "https://steamcommunity.com/market/search/render/"
    searchParams = {
        'appid': 730,
        'query': skin_name,
        'norender': 1,
        'count': 1
    }

    try:
        resp = requests.get(url, params=params, timeout=10)
        resp.raise_for_status()
        data = resp.json()

        searchResp = requests.get(searchImgUrl, params=searchParams, timeout=10)
        searchResp.raise_for_status()
        searchData = searchResp.json()

        if data.get("success") and searchData.get("success"):
            price = data.get("lowest_price") or data.get("median_price")
            results = searchData.get("results", [])
            print(results)

            fullIconUrl = None

            if results and "asset_description" in results[0]:
                iconRelative = results[0]["asset_description"].get("icon_url")
                if iconRelative:
                    fullIconUrl = f"https://steamcommunity-a.akamaihd.net/economy/image/{iconRelative}"
                else:
                    print("Can't retrieve image (2) 😓")
            else:
                print("Can't retrieve image (1) 😓")

            if price:
                return {
                    "price": price,
                    "volume": data.get("volume"),
                    "img": fullIconUrl
                }
            else:
                print(f"API ISSUE: Price data missing for {skin_name}. Response: {data}")
        else:
            print(f"API ISSUE: {skin_name}. Response: {data}")

    except Exception as e:
        print(f"Error grabbing price or img for {skin_name}: {e}")

    return None
