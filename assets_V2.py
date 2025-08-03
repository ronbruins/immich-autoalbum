import requests
import json
import os
import imclass
from math import radians, cos, sin, asin, sqrt
import settings

os.system('clear')

api_keys = settings.api_keys
to_share = settings.to_share
geo_dict = settings.geo_dict
cons_albums = settings.cons_albums
base_url = settings.base_url
album_id = settings.album_id
admin_api = settings.admin_api
assetid=settings.assetid

albums_set = set()
album_dict = {}
asset_limit = 1000

#task="album_info"

#task="list_albums"

#task="geo_create"

task="create_by_tag"


task="create"
# task="delete"


#task="getassetinfo"
#task="debug"

# for user in 3,5:
#     print(user)
#     task="create_by_tag"


init_users = settings.init_users
iun = "2"
'''
init_users['1'] = "Ron Bruins"
init_users['2'] = "Ron Mirjam"
init_users['3'] = "Mirjam Nijburg"
init_users['4'] = "Julian Bruins"
init_users['5'] = "Thibault Bruins"
init_users['6'] = "Sandra Veld"
'''

init_user = init_users[iun]
api_key = api_keys[init_user]

rbimmich = imclass.ImmichApi(api_key,base_url,init_user,admin_api)


def main():
    # warning function (see bottom) to prevent mistakenly executiom of destructive tasks
    warn()
    
    if task == "debug":
        #pass
        print(rbimmich.get_albums())
    elif task == "create":
        create_albums()
    elif task == "create_by_tag":
        create_albums_by_tag()
    elif task == "geo_create":
        build_geo(geo_dict)
    elif task == "getassetinfo":
        asset_info = rbimmich.get_asset_info(assetid)
        print(asset_info['tags'][0]['name'])
        print(asset_info['tags'])

        # for a in asset_info:
        #     print(a)
    elif task == "delete":
        delete_albums()
    elif task == "list_albums":
        album_ids,album_list = rbimmich.get_albums()
        print(album_list)
    elif task == "album_info":
        album_info = rbimmich.get_albums(album_id)
        print(album_info)

def delete_albums():
    # bug: delete albums tries to delete all albums, because of share option in get album method, needs to be checked
    album_ids,album_list = rbimmich.get_albums()
    #print(album_ids,album_list)
    for album_id in album_ids:
        print(f"deleting {album_id}")
        rbimmich.delete_album(album_id)

def init_album_build(share_veto=""):
    if share_veto == "":
        single_lib = True
    else:
        single_lib = False
    immich_users = rbimmich.get_users()
    AlbumUsers,set_user_id = rbimmich.build_album_users(immich_users,init_user,to_share,share_veto)
    print(f"User: {set_user_id}")
    if single_lib == True:
        libraries = rbimmich.get_libraries()
        search_lib = rbimmich.get_search_lib(set_user_id,libraries)
        
        print(f"Search Lib: {search_lib}")
    else:
        search_lib=""
    assetsReceived = rbimmich.get_assets(search_lib,asset_limit)
    
    return assetsReceived,AlbumUsers


def create_albums():
    assetsReceived,AlbumUsers = init_album_build()
    geo_album_name="" # Only used for geo_create to specifiy the album
    album_dict = rbimmich.build_album_dict(assetsReceived,cons_albums,geo_album_name)
    for k,v in album_dict.items():
        print(k)
    rbimmich.createAlbum(album_dict,AlbumUsers)

def create_albums_by_tag():
    #assetsReceived,AlbumUsers = init_album_build("Brunij")
    #assetsReceived,AlbumUsers = init_album_build("")
    # The above defines with who the albums will be shared with.
    # this is related to create albums for user or to share with the family
    # also need to verify then how to deal with the @ and no prefix to make
    # distinction between the two 
    share_veto = ""
    assetsReceived,AlbumUsers = init_album_build(share_veto)
    geo_album_name="" # Only used for geo_create to specifiy the album
    personal = True
    album_dict = rbimmich.build_album_dict_by_tag(assetsReceived,cons_albums,geo_album_name, personal)
    for k,v in album_dict.items():
        print(k)
    rbimmich.createAlbum(album_dict,AlbumUsers)
    print(f"############## {AlbumUsers}")

    # share_veto = settings.tag_share_veto
    # tag_veto['Mirjam Nijburg'] = "MirjamShare"
    share_veto = settings.tag_veto[init_user]
    assetsReceived,AlbumUsers = init_album_build(share_veto)
    geo_album_name="" # Only used for geo_create to specifiy the album
    personal = False
    album_dict = rbimmich.build_album_dict_by_tag(assetsReceived,cons_albums,geo_album_name, personal)
    for k,v in album_dict.items():
        print(k)
    # print(f"@@@@@@@@@@@@@@ {AlbumUsers}")
    rbimmich.createAlbum(album_dict,AlbumUsers)

def build_geo(geo_dict):
    share_veto = settings.geo_share_veto
    assetsReceived,AlbumUsers = init_album_build(share_veto)
    
    for geo_album in geo_dict:
        ok_assets = []
        geo_album_name = geo_album
        geo_data = geo_dict[geo_album]
        print(f"Album will be named: {geo_album_name}")
        print(f"coordintaes used: {geo_data}")

        for asset in assetsReceived:
            asset_id = asset['id']
            org_path = asset['originalPath']
            asset_info = rbimmich.get_asset_info(asset_id)
            try:
                lat = asset_info['exifInfo']['latitude']
                lon = asset_info['exifInfo']['longitude']
            except:
                pass
            if lat != None and lon != None:
                        use_asset = check_radius(geo_data,lat,lon,org_path)
                        if use_asset == True:
                            ok_assets.append(asset)
        
        album_dict = rbimmich.build_album_dict(ok_assets,cons_albums,geo_album_name)
        rbimmich.createAlbum(album_dict,AlbumUsers)

def check_radius(geo_data,check_lat,check_lon,org_path):
    use_asset = False
    center_point = [geo_data]

    ref_lat = center_point[0]['lat']
    ref_lon = center_point[0]['lng']
    radius = 0.5 # in kilometer
    a = haversine(ref_lon, ref_lat, check_lon, check_lat)
    
    if a <= radius:
        #print('Inside the area / Distance (km) : ', a)
        use_asset = True
        return use_asset

def haversine(lon1, lat1, lon2, lat2):
    """
    Calculate the great circle distance between two points 
    on the earth (specified in decimal degrees)
    """
    # convert decimal degrees to radians 
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])

    # haversine formula 
    dlon = lon2 - lon1 
    dlat = lat2 - lat1 
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    c = 2 * asin(sqrt(a)) 
    r = 6371 # Radius of earth in kilometers. Use 3956 for miles
    return c * r

def warn():
    wait = input(f"Task: {task.upper()} \nUser: {init_user} \n\n#####      Are you sure, then press ENTER  #####\n#####        Or CTRL-C to stop             #####")

if __name__ == '__main__':
    main()