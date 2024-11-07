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

    def get_assets(self,search_lib, asset_limit):
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
                #assert r.status_code == 200
                #responseJson = r.json()
                assetsReceived = responseJson['assets']['items']
                print(f"Received {len(assetsReceived)} assets with chunk {page}")
                assets = assets + assetsReceived
        return assets

    def get_albums(self, id=""):
        album_list = {}
        album_list['album'] = {}
        #api = "albums"
        api="albums?shared=true"
        # Hard Coded that only a specific album User will go through all existing albums
        # While Individual Users only check their own owned albums
        # Need to find way to make this dynamic
        # if self.init_user == "Brunij":
        #     api="albums?shared=true"
        # else:
        #     api="albums"
        url = self.base_url + api
        album_ids = []
        admin = False
        body = {}
        if id == "":
            responseJson = self.call_api("GET", api, admin, body)

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
    
    def createAlbum(self, album_dict,AlbumUsers ):
        album_ids,album_list = self.get_albums()
        for albumName,assetIds in album_dict.items():
            api = "albums"
            url = self.base_url + api
            headers = {
            'x-api-key': f'{self.api_key}',
            }        
            #if "@" in albumName:
            if albumName not in album_list['album']:
                if albumName != None:
                    #albumName = albumName.replace("@","")
                    #albumName = albumName.replace("#","")
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


                    if AlbumUsers != []:
                        print("Sharing")
                        album_id = album_data['id']
                        body = {
                        'albumUsers': AlbumUsers
                        }
                        api = f"albums/{album_id}/users"
                        admin = False
                        payload=json.dumps(body)
                        self.call_api("PUT", api, admin, payload)

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

    def build_album_users(self,immich_users,init_user,to_share,share_veto):
        AlbumUsers = []
        print(f"Building Albums and shares for user: {init_user}")
        for user in immich_users:
            user_name = user['name']
            if init_user == user_name:
                set_user_id = user['id']
            if share_veto == "":
                if user_name in to_share[init_user]:
                    print(f"Sharing with: {user_name}")
                    userid = user['id']
                    user_detail = {"role": "editor", "userId":userid}
                    AlbumUsers.append(user_detail)
            else:
                if user_name in to_share[share_veto]:
                    
                    userid = user['id']
                    user_detail = {"role": "editor", "userId":userid}
                    print(f"Sharing with: {user_name}, {user_detail}")
                    AlbumUsers.append(user_detail)
        return AlbumUsers,set_user_id
    


    def get_search_lib(self,set_user_id,libraries):
        #print(f"HEADERS TO CHECK: {self.headers}")
        for library in libraries:
            if set_user_id == library['ownerId']:
                search_lib = library['id']
                #print(library)
        return search_lib
    


    def build_album_dict(self, assetsReceived,cons_albums,geo_album_name):
        album_dict = {}
        for asset in assetsReceived:
            process_asset = True
            path = asset['originalPath']
            #print(path)
            asset_id = asset['id']
            path = path.split("/")
            album_locid = len(path) - 2
            album = path[album_locid]
            album = album.replace("_"," ")

            if geo_album_name != "" and process_asset == True:
                gen_album = f"{album[:4]} {geo_album_name}"
                if gen_album not in album_dict:
                    album_dict[gen_album] = []
                    album_dict[gen_album].append(asset_id)
                else:
                    album_dict[gen_album].append(asset_id)
                process_asset = False 

            for cons_check in cons_albums:
                if cons_check in album and process_asset == True:
                    gen_album = cons_albums[cons_check]
                    if gen_album not in album_dict:
                        album_dict[gen_album] = []
                        album_dict[gen_album].append(asset_id)
                    else:
                        album_dict[gen_album].append(asset_id)
                    process_asset = False        
            if " P" in album and process_asset == True:
                print("#################################### THIS IS SUPPOSED TO BE A PERSONAL ALBUM ####################################")
            if "@" in album and process_asset == True:
                album = album.replace("@","")
                album = album.replace("#","")
                if album not in album_dict:
                    album_dict[album] = []
                    album_dict[album].append(asset_id)
                else:
                    album_dict[album].append(asset_id)
            elif "@@" in album and process_asset == True:
                album = album.replace("@@","")
                album = album.replace("#","")
                if album not in album_dict:
                    album_dict[album] = []
                    album_dict[album].append(asset_id)
                else:
                    album_dict[album].append(asset_id)
            elif "#" in album and process_asset == True:
                gen_album = f"{album[:4]} Diverse Fotos"
                if gen_album not in album_dict:
                    album_dict[gen_album] = []
                    album_dict[gen_album].append(asset_id)
                else:
                    album_dict[gen_album].append(asset_id)
        return album_dict
    
    def build_album_dict_by_tag(self, assetsReceived,cons_albums,geo_album_name, personal):
        album_dict = {}
        for asset in assetsReceived:
            process_asset = True
            path = asset['originalPath']
            asset_id = asset['id']
            asset_info = self.get_asset_info(asset_id)
            #print(f"checking {path}")
            try:
                album_tag = asset_info['tags'][0]['name']
                #print(album_tag)
                album = album_tag

                for cons_check in cons_albums:
                    if cons_check in album and process_asset == True:
                        gen_album = cons_albums[cons_check]
                        if gen_album not in album_dict:
                            album_dict[gen_album] = []
                            album_dict[gen_album].append(asset_id)
                        else:
                            album_dict[gen_album].append(asset_id)
                        process_asset = False      
                

                if "@" in album and personal == False and process_asset == True:
                    album = album.replace("@","")
                    album = album.replace("#","")
                    #print(f"SHARED ALBUM: {album}")
                    if album not in album_dict:
                        album_dict[album] = []
                        album_dict[album].append(asset_id)
                    else:
                        album_dict[album].append(asset_id)
                elif "@" not in album and personal == True and process_asset == True:
                    #album = album.replace(" P","")
                    #print(f"PERSONAL ALBUM: {album}")
                    #album = album.replace("#","")
                    if album not in album_dict:
                        album_dict[album] = []
                        album_dict[album].append(asset_id)
                    else:
                        album_dict[album].append(asset_id)
            except:
                pass
        return album_dict
    

    

    
