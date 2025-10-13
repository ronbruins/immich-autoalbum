import requests
import json

class ImmichApi:
    def __init__(self,api_key,base_url,init_user,admin_api):
        self.api_key = api_key
        self.base_url = base_url
        self.init_user = init_user
        self.admin_api = admin_api
        self.headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'x-api-key': f'{self.api_key}'
                }
        #body['size'] = asset_limit
        self.admin_headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'x-api-key': f'{admin_api}'
                }
        self.payload = {}

    def call_api(self,method, api, admin, body, own_api_key="default"):
        url = self.base_url + api
        if admin == False:
            if method != "DELETE":
                if own_api_key != "default":
                    own_headers = {
                        'Content-Type': 'application/json',
                        'Accept': 'application/json',
                        'x-api-key': f'{own_api_key}'
                        }
                    # print("INDIVIDUAL HEADERS")
                    r = requests.request(method, url, headers=own_headers, data=body)
                else:
                    r = requests.request(method, url, headers=self.headers, data=body)
                responseJson = r.json()
                return responseJson
            else:
                # if own_api_key != "default":
                #     own_headers = {
                #         'Content-Type': 'application/json',
                #         'Accept': 'application/json',
                #         'x-api-key': f'{own_api_key}'
                #         }
                #     r = requests.request(method, url, headers=own_headers)
                # else:
                r = requests.request(method, url, headers=self.headers, data=body)
        else:
            print(f"@@@@@  ADMIN HEADERS @@@@@@ {self.admin_headers}")
            r = requests.request(method, url, headers=self.admin_headers, data=body)
            responseJson = r.json()
            return responseJson

    def get_users(self):
        api = "users"
        admin = False
        body = {}
        responseJson = self.call_api("GET", api, admin, body)
        return responseJson    

    def get_asset_info(self,asset_id):
        api = f"assets/{asset_id}"
        url = self.base_url + api
        #r = requests.request("GET", url, headers=self.headers)
        admin = False
        body = {}
        asset_info = self.call_api("GET", api, admin, body)
        return asset_info

    def delete_album(self,album_id):
        api = f"albums/{album_id}"
        admin = False
        body = {}
        self.call_api("DELETE", api, admin, body)

    def get_assets(self,asset_limit,search_lib):
        assets = []
        api = "search/metadata"
        url = self.base_url + api
        payload = {}
        headers = {
        'x-api-key': f'{self.api_key}'
        }
        print(self.api_key)
        body = {}
        body['isNotInAlbum'] = 'true'
        body['size'] = asset_limit
        if search_lib != "":
            print("Using single library owned by user")
            body['libraryId'] = search_lib
        admin = False
        payload=json.dumps(body)
        responseJson = self.call_api("POST", api, admin, payload)

        page = 1
        assetsReceived = responseJson['assets']['items']
        assets = assets + assetsReceived
        print(f"Received {len(assetsReceived)} assets with chunk {page}")
        while len(assetsReceived) == 1000:
                page += 1
                body['page'] = page
                payload=json.dumps(body)
                admin = False
                responseJson = self.call_api("POST", api, admin, payload)
                assetsReceived = responseJson['assets']['items']
                print(f"Received {len(assetsReceived)} assets with chunk {page}")
                assets = assets + assetsReceived
        return assets

    def get_albums(self, id=""):
        album_list = {}
        album_list['album'] = {}
        # api = "albums?shared=false"
        api="albums?shared=true"
        # Hard Coded that only a specific album User will go through all existing albums
        # While Individual Users only check their own owned albums
        # Need to find way to make this dynamic
        # if self.init_user == "Brunij":
        #     api="albums?shared=true"
        # else:
        # api="albums"
        url = self.base_url + api
        album_ids = []
        admin = False
        body = {}
        if id == "":
            responseJson = self.call_api("GET", api, admin, body)
            #print(responseJson)

            for album in responseJson:
                album_name = album['albumName']
                album_id = album['id']
                album_ids.append(album_id)
                album_list['album'][album_name]=album_id
            return album_ids,album_list
        else:
            api = f"albums/{id}"
            album_info = self.call_api("GET", api, admin, body)
            return album_info

    def get_asset_info(self,asset_id):
        api = f"assets/{asset_id}"
        url = self.base_url + api
        r = requests.request("GET", url, headers=self.headers)

        return r.json()
    
    def get_libraries(self):
            api = "libraries"
            admin = True
            body = {}
            libraries = self.call_api("GET", api, admin, body)
            # print(libraries)
            return libraries

    def createAlbum(self, album_dict):
        album_ids,album_list = self.get_albums()
        for albumName,albumDetails in album_dict.items():
            assetIds = album_dict[albumName]['assetIds']
            AlbumUsers = album_dict[albumName]['albumUsers']
            own_api_key = album_dict[albumName]['api_key']

            api = "albums"
            # url = self.base_url + api
            # headers = {
            # 'x-api-key': f'{self.api_key}',
            # }        
            if albumName not in album_list['album']:
                if albumName != None:
                    body = {
                    'albumName': albumName,
                    'description': albumName,
                    "assetIds": assetIds,
                    }
                    payload = json.dumps(body)
                    admin = False
                    payload=json.dumps(body)
                    album_data = self.call_api("POST", api, admin, payload,own_api_key)
                    AlbumUsers = album_dict[albumName]['albumUsers']
                    if AlbumUsers != []:
                        print(f"Sharing {albumName} with {AlbumUsers} for API: {own_api_key}")
                        album_id = album_data['id']
                        body = {
                        'albumUsers': AlbumUsers
                        }
                        api = f"albums/{album_id}/users"
                        admin = False
                        payload=json.dumps(body)
                        debugresp = self.call_api("PUT", api, admin, payload, own_api_key)

            else:
                AlbumId = album_list['album'][albumName]
                api = f"albums/{AlbumId}/assets"
                print(f"UPDATING {albumName} for API: {own_api_key}")
                body = {
                    "ids": assetIds,
                }
                admin = False
                payload=json.dumps(body)
                self.call_api("PUT", api, admin, payload,own_api_key)

    def build_album_users(self,immich_users,init_user,to_share):
        AlbumUsers = {}
        AlbumUsers[init_user] = {}
        print(f"Building Albums and shares for user: {init_user}")
        for line in to_share[init_user]:
            AlbumUsers[init_user][line] = []        
            for user in immich_users:
                user_name = user['name']
                if init_user == user_name:
                    set_user_id = user['id']
                if user_name in to_share[init_user][line]:
                    # print(f"Sharing with: {user_name}")
                    userid = user['id']
                    user_detail = {"role": "editor", "userId":userid}
                    AlbumUsers[init_user][line].append(user_detail)
        return AlbumUsers,set_user_id
    


    def get_search_lib(self,set_user_id,libraries):
        #print(f"HEADERS TO CHECK: {self.headers}")
        for library in libraries:
            if set_user_id == library['ownerId']:
                lib_name = library['name']
                if "Video" not in lib_name:
                    search_lib = library['id']              
                    print(f"Name: {lib_name}")
                    # print(library)
        return search_lib
    
    def build_album_dict(self, assetsReceived,AlbumUsers,init_user, album_dict,api_key):
        # album_dict = {}
        for asset in assetsReceived:
            path = asset['originalPath']
            thumbhash = asset['thumbhash']
            if thumbhash != None:
                asset_id = asset['id']
                path = path.split("/")
                album_locid = len(path) - 2
                album = path[album_locid]
                album = album.replace("_"," ")
                procAlbum = album
                if "#" in procAlbum:
                    suffix = "#"
                    procAlbum = f"{album[:4]}{album[10:]}" #consolidate album into year and description
                elif "@@" in album:
                    suffix = "@@"
                elif "@" in album:
                    suffix = "@"
                else:
                    suffix = "SKIP"
                
                if suffix != "SKIP":
                    procAlbum = procAlbum.replace(f" {suffix}","")
                    if procAlbum not in album_dict:
                        # print(f"CREATE ALBUM DICT {procAlbum}")
                        album_dict[procAlbum] = {}
                        album_dict[procAlbum]['api_key'] = api_key
                        album_dict[procAlbum]['assetIds'] = []
                        album_dict[procAlbum]['albumUsers'] = []
                        album_dict[procAlbum]['albumUsers'] = AlbumUsers[init_user][suffix]
                    album_dict[procAlbum]['assetIds'].append(asset_id)

        return album_dict
    
    def build_album_dict_by_tag(self, assetsReceived,AlbumUsers,init_user,album_dict,api_key):
        # album_dict = {}
        for asset in assetsReceived:
            path = asset['originalPath']
            thumbhash = asset['thumbhash']
            if thumbhash != None:
                asset_id = asset['id']
                asset_info = self.get_asset_info(asset_id)
                # print(asset_info['tags'])
                #print(f"checking {path}")
                try:
                    for tags in asset_info['tags']:
                        album_tag = tags['name']

                        album = album_tag
                        procAlbum = album
                        # print(procAlbum, asset_id)
                        
                        if "#" in procAlbum:
                            suffix = "#"
                            procAlbum = f"{album[:4]} Diverse Fotos"
                        elif "@@" in album:
                            suffix = "@@"
                        elif "@" in album:
                            suffix = "@"
                        else:
                            suffix = "DEFGHIJ"
                        procAlbum = procAlbum.replace(f" {suffix}","")
                        # print(f"ALBUMDICT:")
                        if procAlbum not in album_dict:
                            # print(f"CREATE ALBUM DICT {procAlbum}")
                            album_dict[procAlbum] = {}
                            album_dict[procAlbum]['api_key'] = api_key
                            album_dict[procAlbum]['assetIds'] = []
                            album_dict[procAlbum]['albumUsers'] = []
                            album_dict[procAlbum]['albumUsers'] = AlbumUsers[init_user][suffix]
                        album_dict[procAlbum]['assetIds'].append(asset_id)
                        
                except:
                    pass
        # print(json.dumps(album_dict)) 
        return album_dict