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
# task="create"
task="loop"
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

# init_user = init_users[iun]
# api_key = api_keys[init_user]

# rbimmich = imclass_V2.ImmichApi(api_key,base_url,init_user,admin_api)
album_dict = {}
task == "debug"
def main():
    # os.system('clear')
    # warn()
    if task == "debug":
        print(rbimmich.get_albums())
    elif task == "create":
        album_dict={}
        create_albums(album_dict)
    elif task == "loop":
        album_dict={}
        for iun in "2","3","4","5","1":
        # for iun in "1":
            init_user = init_users[iun]
            # warn(init_user)
            api_key = api_keys[init_user]
            rbimmich = imclass_V2.ImmichApi(api_key,base_url,init_user,admin_api)


            create_albums(rbimmich,album_dict,init_user,api_key)
        sorted_data_keys = json.dumps({k: album_dict[k] for k in sorted(album_dict)})
        album_dict = json.loads(sorted_data_keys)
        for k,v in album_dict.items():
            print(k, album_dict[k]['api_key'])
        
        rbimmich.createAlbum(album_dict)
    
def init_album_build(rbimmich,init_user):
    immich_users = rbimmich.get_users()
    AlbumUsers,set_user_id = rbimmich.build_album_users(immich_users,init_user,to_share)
    print(f"User: {set_user_id}")
    libraries = rbimmich.get_libraries() 
    search_lib = rbimmich.get_search_lib(set_user_id,libraries)
    assetsReceived = rbimmich.get_assets(asset_limit,search_lib)
    
    return assetsReceived ,AlbumUsers


def create_albums(rbimmich,album_dict,init_user,api_key):
    # init_user = init_users[iun]
    # print(init_user)
    assetsReceived,AlbumUsers = init_album_build(rbimmich,init_user)
    # print(assetsReceived)
   

    user_album_dict = rbimmich.build_album_dict(assetsReceived,AlbumUsers,init_user,album_dict,api_key)
    tag_album_dict = rbimmich.build_album_dict_by_tag(assetsReceived,AlbumUsers,init_user,user_album_dict,api_key)
    album_dict = tag_album_dict


    # sorted_data_keys = json.dumps({k: data_dict[k] for k in sorted(data_dict)})
    # album_dict = json.loads(sorted_data_keys)
    # return album_dict
    # print(json.dumps(album_dict)) 
    



    # rbimmich.createAlbum(album_dict)



def warn(init_user):
    wait = input(f"Task: {task.upper()} \nUser: {init_user} \n\n#####      Are you sure, then press ENTER  #####\n#####        Or CTRL-C to stop             #####")

if __name__ == '__main__':
    main()