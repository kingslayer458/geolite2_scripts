import requests
from config import  ACCOUNT_ID , LICENSE_KEY


def geolocate_ip(ip: str):
    url = f"https://geolite.info/geoip/v2.1/city/{ip}"

    response = requests.get(
        url,
        auth=(ACCOUNT_ID, LICENSE_KEY),
        headers={"Accept": "application/json"},
        timeout=10
    )

    if response.status_code != 200:
        return {
            "ip": ip,
            "error": response.text
        }

    data = response.json()

    country = data.get("country", {})
    city = data.get("city", {})
    location = data.get("location", {})

    return {
        "ip": ip,
        "country": country.get("names", {}).get("en"),
        "country_code": country.get("iso_code"),
        "city": city.get("names", {}).get("en"),
        "latitude": location.get("latitude"),
        "longitude": location.get("longitude"),
        "accuracy_radius_km": location.get("accuracy_radius")
    }


result = geolocate_ip("")

print(result)