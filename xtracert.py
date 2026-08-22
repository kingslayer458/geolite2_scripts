import subprocess
import ipaddress
import json
import platform
import requests
import geoip2.database
from config import ACCOUNT_ID, LICENSE_KEY

ASN_DB = "GeoLite2-ASN.mmdb"
asn_reader = geoip2.database.Reader(ASN_DB)

def is_public_ip(value: str):
    try:
        return ipaddress.ip_address(value).is_global
    except ValueError:
        return False

def extract_ip(text: str):
    for token in text.split():
        token = token.strip("[](),")
        try:
            return str(ipaddress.ip_address(token))
        except ValueError:
            continue
    return None


def parse_traceroute(output: str):
    hops = []
    for line in output.splitlines():
        line = line.strip()
        if not line:
            continue
        parts = line.split()
        try:
            hop_number = int(parts[0])
        except (ValueError, IndexError):
            continue
        hop_text = " ".join(parts[1:])
        ip = extract_ip(hop_text)
        if ip:
            hops.append({
                "hop": hop_number,
                "ip": ip,
                "public": is_public_ip(ip),
                "response": ip
            })
        else:
            hops.append({
                "hop": hop_number,
                "ip": None,
                "public": False,
                "response": "* * *"
            })
    return hops

def run_traceroute(target: str):

    system = platform.system()

    if system == "Windows":
        command = ["tracert", "-d", "-w", "500", target]

    elif system in ("Linux", "Darwin"):
        command = ["traceroute", "-n", "-w", "0.5", target]

    else:
        raise RuntimeError(f"Unsupported OS: {system}")
    
    try:
        result = subprocess.run(command,capture_output=True,text=True,timeout=60)

    except FileNotFoundError:
        raise RuntimeError(f"Traceroute utility is not installed on {system}")
    
    except subprocess.TimeoutExpired:
        return []
    
    return parse_traceroute(result.stdout)

def lookup_hop(ip: str):
    url = f"https://geolite.info/geoip/v2.1/city/{ip}"
    try:
        response = requests.get( url,auth=(ACCOUNT_ID, LICENSE_KEY),timeout=10)
    except requests.RequestException as e:
        return {
            "ip": ip,
            "error": str(e)
        }
    if response.status_code != 200:
        return {
            "ip": ip,
            "error": response.text
        }
    try:
        city_data = response.json()
    except ValueError:
        return {
            "ip": ip,
            "error": "Invalid JSON response from GeoLite"
        }
    location = city_data.get("location", {})
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
def process_domain(domain: str):
    print(f"\nTracerouting {domain}...")
    trace = run_traceroute(domain)

    result = {
        "target": domain,
        "hops": []
    }

    for hop in trace:
        hop_number = hop["hop"]
        ip = hop["ip"]
        public = hop["public"]

        hop_data = {
            "hop": hop_number,
            "ip": ip,
            "public": public,
            "response": hop["response"]
        }

        if ip is None:
            print(f"  Hop {hop_number}: * * *")
            result["hops"].append(hop_data)
            continue

        if public:
            geo_data = lookup_hop(ip)

            if "error" in geo_data:
                hop_data["error"] = geo_data["error"]
                organization = "Unknown"
            else:
                hop_data["location"] = geo_data.get("location")
                hop_data["network"] = geo_data.get("network")

                organization = geo_data.get("network", {}).get("organization","Unknown")

            print(f"  Hop {hop_number}: {ip} "f"(PUBLIC) - {organization}")

        else:
            print(f"  Hop {hop_number}: {ip} "f"(PRIVATE)" )

        result["hops"].append(hop_data)

    return result

def main():
    domains = [
        "google.com",
        "cloudflare.com"
    ]
    final_result = []
    try:
        for domain in domains:
            final_result.append(process_domain(domain))
    finally:
        asn_reader.close()
    with open("traceroute_geolite_result.json","w",encoding="utf-8") as f:
        json.dump(final_result,f,indent=4,ensure_ascii=False)

if __name__ == "__main__":
    main()