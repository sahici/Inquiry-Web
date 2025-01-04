# Inquiry-Web v1.0
# Signature: Yasin Yaşar

import requests
import re

def crawl(url):
    try:
        istek = requests.get(f"https://{url}/lib/upgrade.txt")
        
        if istek.status_code == 200:
            response_text = istek.text
            
            match = re.search(r"===\s*(.*?)\s*===", response_text)
            
            if match:
                version_code = match.group(1)
                print(f"Version Code: {version_code}")
            
            else:
                print("Version Code Not Found")
        
        else:
            print(f"Request Failed, HTTP Status Code: {istek.status_code}")
    
    except requests.exceptions.RequestException as e:
        print(f"An Error Occurred: {e}")
