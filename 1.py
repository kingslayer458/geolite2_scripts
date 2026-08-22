import geoip2.database

CITY_DB = "GeoLite2-City.mmdb"
ASN_DB = "GeoLite2-ASN.mmdb"

city_reader = geoip2.database.Reader(CITY_DB)
asn_reader = geoip2.database.Reader(ASN_DB)

ip = input("Enter hop IP: ").strip()

try:
    city = city_reader.city(ip)
    print("IP:", ip)
    print("Country:", city.country.name)
    print("Country Code:", city.country.iso_code)
    print("City:", city.city.name)
    print("State:", city.subdivisions.most_specific.name)
    print("Latitude:", city.location.latitude)
    print("Longitude:", city.location.longitude)

except Exception as e:
    print("Location lookup failed:", e)

try:
    asn = asn_reader.asn(ip)

    print("\n=== NETWORK ===")
    print("ASN:", asn.autonomous_system_number)
    print("Organization:", asn.autonomous_system_organization)

except Exception as e:
    print("ASN lookup failed:", e)

city_reader.close()
asn_reader.close()