# Inquiry-Web v1.0
# Signature: Yasin Yaşar

import requests
import json
import threading

def fetch_subdomain_status(common_name, results):
    try:
        response = requests.get(f"http://{common_name}", timeout=5)
        status_code = response.status_code
        if status_code == 200:
            results.append({"subdomain": common_name, "status_code": status_code})
    except requests.exceptions.RequestException:
        pass

def find_subdomains(domain):
    print(f"Starting subdomain detection: {domain}")
    url = f"https://crt.sh/?q={domain}&output=json"
    
    try:
        response = requests.get(url)
        response.raise_for_status()
        print(f"Response received from CRT.sh: {domain}")

        subdomains = []
        seen_subdomains = set()
        json_data = json.loads(response.text)

        results = []
        threads = []

        for item in json_data:
            common_name = item.get("common_name")
            if common_name and not common_name.startswith("www.") and common_name not in seen_subdomains and common_name != domain:
                seen_subdomains.add(common_name)
                thread = threading.Thread(target=fetch_subdomain_status, args=(common_name, results))
                threads.append(thread)
                thread.start()

        for thread in threads:
            thread.join()
            
        if results:
            print_subdomains(results)
        else:
            print("No subdomains found.")

    except requests.exceptions.HTTPError as e:
        if 500 <= response.status_code < 600:
            print("CRT.sh is currently unavailable, please try again later. (Recommended 5 minutes)")
        else:
            print(f"Error: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Connection error: {e}")

def print_subdomains(subdomains):
    print("\nFound Subdomains:")
    
    for entry in subdomains:
        print(f"Subdomain: {entry['subdomain']}")
        print(f"Status Code: {entry['status_code']}\n")
