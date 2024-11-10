import requests
import json
import sys
import settings

admin_api_keys = settings.admin_api
api_keys = {}
api_keys['Admin']=admin_api_keys
payload={}
base_url = settings.base_url

def main():
    for api_key, api_value in api_keys.items():
        api = "libraries"
        url = base_url + api
        libraries = callimmich(url, api_value, "GET", payload)
        scanlib(api_value,libraries)
        sendtg(f"CD Test All Libraries Scanned")

def sendtg(message):
    TOKEN = settings.tg_token
    chat_id = settings.chat_id
    url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
    print(requests.get(url).json()) # this sends the message

def scanlib(api_value,libraries):
    for library in libraries:
        id = library['id']
        name = library['name']
        api = f"libraries/{id}/scan"
        url = base_url + api        
        scan_library = callimmich(url,api_value, "POST", payload)
        print(name,api_value,scan_library, url,api_value, payload)  
        

def callimmich(url,api_value, method, payload):
    headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'x-api-key': api_value
                }
    response = requests.request(method, url, headers=headers, data=payload)
    if method == "GET":
        return response.json()
    else:
        return response.status_code

if __name__ == '__main__':
    main()

