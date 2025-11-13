import json

import imclass_V2
import settings

api_keys = settings.api_keys
to_share = settings.to_share
geo_dict = settings.geo_dict
cons_albums = settings.cons_albums
base_url = settings.base_url
album_id = settings.album_id
admin_api = settings.admin_api
assetid=settings.assetid
init_users = settings.init_users


def libloop(user_exec):
    for iun in user_exec:
        init_user = init_users[iun]
        api_key = api_keys[init_user]
        rbimmich = imclass_V2.ImmichApi(api_key,base_url,init_user,admin_api)
        libraries = rbimmich.get_libraries() 
        print(json.dumps(libraries))


def tagloop(user_exec):
    for iun in user_exec:
        #  for iun in "1":
        init_user = init_users[iun]
        api_key = api_keys[init_user]
        rbimmich = imclass_V2.ImmichApi(api_key,base_url,init_user,admin_api)
        taglist = rbimmich.gettags()
        # print(taglist)
        for a in taglist:
            print(a)   

def deleteloop(user_exec):
    for iun in user_exec:
        init_user = init_users[iun]
        api_key = api_keys[init_user]
        rbimmich = imclass_V2.ImmichApi(api_key,base_url,init_user,admin_api)
        local=False
        album_ids,album_list = rbimmich.get_albums(local)
        for album_id in album_ids:
            print(f"deleting {album_id}")
            # rbimmich.delete_album(album_id)

def update_album_list(user_exec):
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