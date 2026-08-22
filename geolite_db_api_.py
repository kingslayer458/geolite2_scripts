import requests
import geoip2.database
import json
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

major_isp_ips = [
    "8.8.8.8",
    "8.8.4.4",
    "1.1.1.1",
    "1.0.0.1",
    "9.9.9.9",
    "208.67.222.222",
    "208.67.220.220",
    "4.2.2.1",
    "4.2.2.2",
    "4.2.2.3",
    "4.2.2.4",
    "198.153.192.1",
    "198.153.194.1",
    "12.244.0.3",
    "75.75.75.75",
    "75.75.76.76",
    "208.54.0.1",
    "125.16.0.1",
    "202.56.230.1",
    "49.44.0.1",
    "49.44.1.1",
    "218.248.255.145",
    "59.144.0.1",
    "202.153.32.1",
    "180.87.12.1",
    "80.10.246.2",
    "217.0.43.1",
    "129.250.35.250",
    "62.115.148.1",
    "38.104.0.1",
    "184.105.64.1",
    "74.82.42.42",
    "3.5.140.2",
    "20.42.65.90",
    "34.117.59.81",
]

final_result = []

for i in major_isp_ips:
    print(i)
    data = lookup_hop(i)
    final_result.append(data)

# result = lookup_hop("")

# print(result)

# print(final_result)
asn_reader.close()

with open("geolite_check_result.json","w") as f:
    json.dump(final_result,f,indent=4)