# import requests
import json
import os
import imclass_V2
from math import radians, cos, sin, asin, sqrt
import settings

import tasks

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

# task="tagloop"


# task="deleteloop"
# task="delete"
#task="getassetinfo"
#task="debug"

# for user in 3,5:
#     print(user)
#     task="create_by_tag"

# task="create_by_tag"


# task="createloop"
# task="updateloop"
task="libloop"
# task="tagloop"
# task="deleteloop"


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

user_exec=["2","3","4","5","1","6"]
album_dict = {}
task == "debug"
def main():
    if task == "createloop":
        createloop()
        update_album_list()
    elif task == "deleteloop":
        deleteloop()
    elif task == "tagloop":
         get_tag_list()
    elif task == "libloop":
         tasks.libloop(user_exec)
    elif task == "updateloop":
        update_album_list()


def createloop():
    album_dict={}
    album_list = {}
    album_final = dict(album_list)
    # album_list = {}
    for iun in user_exec:
        init_user = init_users[iun]
        api_key = api_keys[init_user]
        rbimmich = imclass_V2.ImmichApi(api_key,base_url,init_user,admin_api)
        local = False
        album_ids,album_list = rbimmich.get_albums(local)
        create_albums(rbimmich,album_dict,init_user,api_key)
        album_final.update(album_list['album'])
    
    sorted_data_keys = json.dumps({k: album_dict[k] for k in sorted(album_dict)})
    album_dict = json.loads(sorted_data_keys)
    for k,v in album_dict.items():
        print(k)
    rbimmich.createAlbum(album_dict,album_final)    

def deleteloop():
    for iun in user_exec:
        init_user = init_users[iun]
        api_key = api_keys[init_user]
        rbimmich = imclass_V2.ImmichApi(api_key,base_url,init_user,admin_api)
        local=False
        album_ids,album_list = rbimmich.get_albums(local)
        for album_id in album_ids:
            print(f"deleting {album_id}")
            # rbimmich.delete_album(album_id)

def get_tag_list():
    for iun in user_exec:
        #  for iun in "1":
        init_user = init_users[iun]
        api_key = api_keys[init_user]
        rbimmich = imclass_V2.ImmichApi(api_key,base_url,init_user,admin_api)
        taglist = rbimmich.gettags()
        # print(taglist)
        for a in taglist:
            print(a)    

def update_album_list():
    update_album_dict = {}
    for iun in user_exec:
        init_user = init_users[iun]
        api_key = api_keys[init_user]
        rbimmich = imclass_V2.ImmichApi(api_key,base_url,init_user,admin_api)
        local=True
        album_ids,album_list = rbimmich.get_albums(local)

        for albumname in album_list['album']:
            album_id = album_list['album'][albumname]
            update_album_dict[albumname]={}
            update_album_dict[albumname]['album_id']=album_id
            update_album_dict[albumname]['api_key']=api_key
            # print(albumname, api_key)
    sorted_data_keys = json.dumps({k: update_album_dict[k] for k in sorted(update_album_dict)})
    update_album_dict = json.loads(sorted_data_keys)
    
    update_albums = rbimmich.update_albums(update_album_dict)



def gettags(rbimmich):
    # bug: delete albums tries to delete all albums, because of share option in get album method, needs to be checked
    local=False
    taglist = rbimmich.gettags()

    # print(album_ids,album_list['album'])
    # for album_id in album_ids:
    #     print(f"deleting {album_id}")
    #     rbimmich.delete_album(album_id)

def init_album_build(rbimmich,init_user):
    YELLOW = '\033[33m'
    RESET = '\033[0m'
    immich_users = rbimmich.get_users()
    AlbumUsers,set_user_id = rbimmich.build_album_users(immich_users,init_user,to_share)
    print(f"User ID: \t \t \t \t {set_user_id}")
    libraries = rbimmich.get_libraries() 
    search_lib = rbimmich.get_search_lib(set_user_id,libraries)
    assetsReceived = rbimmich.get_assets(asset_limit,search_lib)
    
    return assetsReceived ,AlbumUsers


def create_albums(rbimmich,album_dict,init_user,api_key):
    assetsReceived,AlbumUsers = init_album_build(rbimmich,init_user)
    print("Initializing Folders build")
    user_album_dict = rbimmich.build_album_dict(assetsReceived,AlbumUsers,init_user,album_dict,api_key)
    print("Initializing Tags build")
    tag_album_dict = rbimmich.build_album_dict_by_tag(assetsReceived,AlbumUsers,init_user,user_album_dict,api_key)
    album_dict = tag_album_dict



def warn(init_user):
    wait = input(f"Task: {task.upper()} \nUser: {init_user} \n\n#####      Are you sure, then press ENTER  #####\n#####        Or CTRL-C to stop             #####")

if __name__ == '__main__':
    main()