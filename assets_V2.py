# import requests
import json
import os
import imclass_V2
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

# task="album_info"
#task="list_albums"
# task="geo_create"
# task="create_by_tag"
task="create"
# task="loop"
# task="delete"
#task="getassetinfo"
#task="debug"

# for user in 3,5:
#     print(user)
#     task="create_by_tag"

# task="create_by_tag"

init_users = settings.init_users
iun = "1"
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

rbimmich = imclass_V2.ImmichApi(api_key,base_url,init_user,admin_api)
album_dict = {}

def main():
    warn()
    if task == "debug":
        print(rbimmich.get_albums())
    elif task == "create":
        album_dict={}
        create_albums(album_dict)
    # elif task == "loop":
    #     album_dict={}
    #     create_albums(album_dict, str(iun))
    
def init_album_build():
    immich_users = rbimmich.get_users()
    AlbumUsers,set_user_id = rbimmich.build_album_users(immich_users,init_user,to_share)
    print(f"User: {set_user_id}")
    assetsReceived = rbimmich.get_assets(asset_limit)
    
    return assetsReceived ,AlbumUsers


def create_albums(album_dict):
    init_user = init_users[iun]
    print(init_user)
    assetsReceived,AlbumUsers = init_album_build()
    user_album_dict = rbimmich.build_album_dict(assetsReceived,AlbumUsers,init_user,album_dict)
    tag_album_dict = rbimmich.build_album_dict_by_tag(assetsReceived,AlbumUsers,init_user,user_album_dict)
    data_dict = tag_album_dict
    sorted_data_keys = json.dumps({k: data_dict[k] for k in sorted(data_dict)})
    album_dict = json.loads(sorted_data_keys)
    print(json.dumps(album_dict)) 



    # rbimmich.createAlbum(album_dict)



def warn():
    wait = input(f"Task: {task.upper()} \nUser: {init_user} \n\n#####      Are you sure, then press ENTER  #####\n#####        Or CTRL-C to stop             #####")

if __name__ == '__main__':
    main()