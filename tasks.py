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