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

    def call_api(self,method, api, admin, body):
        url = self.base_url + api
        if admin == False:
            #print(f"@@@@@  HEADERS @@@@@@ {self.headers}")
            if method != "DELETE":
                r = requests.request(method, url, headers=self.headers, data=body)
                responseJson = r.json()
                return responseJson
            else:
                r = requests.request(method, url, headers=self.headers)
        else:
            #print(f"@@@@@  ADMIN HEADERS @@@@@@ {self.admin_headers}")
            r = requests.request(method, url, headers=self.admin_headers, data=body)
            responseJson = r.json()
            return responseJson

    def get_users(self):
        api = "users"
        admin = False
        body = {}
        responseJson = self.call_api("GET", api, admin, body)
        return responseJson
    
    def get_libraries(self):
        api = "libraries"
        admin = True
        body = {}
        libraries = self.call_api("GET", api, admin, body)
        #print(libraries)
        return libraries

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

    def get_assets(self,asset_limit):
        assets = []
        api = "search/metadata"
        url = self.base_url + api
        payload = {}
        headers = {
        'x-api-key': f'{self.api_key}'
        }
        body = {}
        body['isNotInAlbum'] = 'true'
        body['size'] = asset_limit
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
    
    def createAlbum(self, album_dict):
        album_ids,album_list = self.get_albums()
        for albumName,albumDetails in album_dict.items():
            # print(albumName, assetIds)
            print(" ")
            assetIds = album_dict[albumName]['assetIds']
            AlbumUsers = album_dict[albumName]['albumUsers']

            api = "albums"
            url = self.base_url + api
            headers = {
            'x-api-key': f'{self.api_key}',
            }        
            if albumName not in album_list['album']:
                if albumName != None:
                    body = {
                    'albumName': albumName,
                    'description': albumName,
                    "assetIds": assetIds,
                    }
                    print(f"Creating Album: {albumName}")
                    payload = json.dumps(body)
                    admin = False
                    payload=json.dumps(body)
                    album_data = self.call_api("POST", api, admin, payload)
                    AlbumUsers = album_dict[albumName]['albumUsers']
                    if AlbumUsers != []:
                        print(f"Sharing with {AlbumUsers}")
                        album_id = album_data['id']
                        body = {
                        'albumUsers': AlbumUsers
                        }
                        api = f"albums/{album_id}/users"
                        admin = False
                        payload=json.dumps(body)
                        # print(payload)
                        debugresp = self.call_api("PUT", api, admin, payload)
                        # print(debugresp)

            else:
                AlbumId = album_list['album'][albumName]
                api = f"albums/{AlbumId}/assets"
                print(f"UPDATING {albumName}")
                body = {
                    "ids": assetIds,
                }
                admin = False
                payload=json.dumps(body)
                self.call_api("PUT", api, admin, payload)

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
                    print(f"Sharing with: {user_name}")
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
                    print(library)
        return search_lib
    


    def build_album_dict(self, assetsReceived,AlbumUsers,init_user):
        album_dict = {}
        for asset in assetsReceived:
            process_asset = True
            path = asset['originalPath']
            thumbhash = asset['thumbhash']
            if thumbhash != None:
                asset_id = asset['id']
                path = path.split("/")
                album_locid = len(path) - 2
                album = path[album_locid]
                album = album.replace("_"," ")
                procAlbum = album
                if "#" in procAlbum and process_asset == True:
                    procAlbum = f"{album[:4]} Diverse Fotos"
                    procAlbum = procAlbum.replace("#","")
                    if procAlbum not in album_dict:
                        print(f"CREATE ALBUM DICT {procAlbum}")
                        album_dict[procAlbum] = {}
                        album_dict[procAlbum]['assetIds'] = []
                        album_dict[procAlbum]['albumUsers'] = []
                        # print(f"DEFEFEFEFE {AlbumUsers[init_user]['def']}")
                        album_dict[procAlbum]['albumUsers'] = AlbumUsers[init_user]['def']
                    album_dict[procAlbum]['assetIds'].append(asset_id)
                elif "@@" in album and process_asset == True:
                    procAlbum = procAlbum.replace(" @@","")
                    if procAlbum not in album_dict:
                        print(f"CREATE ALBUM DICT {procAlbum}")
                        album_dict[procAlbum] = {}
                        album_dict[procAlbum]['assetIds'] = []
                        album_dict[procAlbum]['albumUsers'] = []
                        # print(f"DDDDDDDDDATATATATA {AlbumUsers[init_user]['@@']}")
                        
                        album_dict[procAlbum]['albumUsers'] = AlbumUsers[init_user]['@@']
                    album_dict[procAlbum]['assetIds'].append(asset_id)
                elif "@" in album and process_asset == True:
                    procAlbum = procAlbum.replace(" @","")
                    if procAlbum not in album_dict:
                        print(f"CREATE ALBUM DICT {procAlbum}")
                        album_dict[procAlbum] = {}
                        album_dict[procAlbum]['assetIds'] = []
                        album_dict[procAlbum]['albumUsers'] = []
                        # print(f"ATATATATA {AlbumUsers[init_user]['@']}")
                        album_dict[procAlbum]['albumUsers'] = AlbumUsers[init_user]['@']
                    album_dict[procAlbum]['assetIds'].append(asset_id)
                
                # procAlbum = procAlbum.replace("@","")
                
                # if procAlbum not in album_dict:
                #     album_dict[procAlbum] = {}
                #     album_dict[procAlbum]['assetIds'] = []


                # album_dict[procAlbum]['assetIds'].append(asset_id)
                # album_dict[procAlbum]['albumUsers'] = AlbumUsers

        # print(json.dumps(album_dict))    
        return album_dict
  