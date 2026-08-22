import requests
import geoip2.database
from config import  ACCOUNT_ID , LICENSE_KEY

ASN_DB = "GeoLite2-ASN.mmdb"

asn_reader = geoip2.database.Reader(ASN_DB)


def lookup_hop(ip: str):


    url = f"https://geolite.info/geoip/v2.1/city/{ip}"

    response = requests.get(
        url,
        auth=(ACCOUNT_ID, LICENSE_KEY),
        timeout=10
    )

    if response.status_code != 200:
        return {
            "ip": ip,
            "error": response.text
        }

    city_data = response.json()

    location = city_data.get("location", {})
    city = city_data.get("city", {})
    country = city_data.get("country", {})


    try:
        asn_data = asn_reader.asn(ip)

        asn = asn_data.autonomous_system_number
        organization = asn_data.autonomous_system_organization

    except Exception:
        asn = None
        organization = None


    return {
        "ip": ip,

        "location": {
            "city": city.get("names", {}).get("en"),
            "country": country.get("names", {}).get("en"),
            "country_code": country.get("iso_code"),
            "latitude": location.get("latitude"),
            "longitude": location.get("longitude"),
            "accuracy_radius_km": location.get("accuracy_radius")
        },

        "network": {
            "asn": asn,
            "organization": organization
        }
    }


result = lookup_hop("")

print(result)

asn_reader.close()