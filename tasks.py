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
asset_limit = settings.asset_limit


update_album_dict = {}
album_list = {}
album_final = dict(album_list)

def mainexecutor(user_exec, task):
    album_dict={}
    for iun in user_exec:
        init_user = init_users[iun]
        api_key = api_keys[init_user]
        rbimmich = imclass_V2.ImmichApi(api_key,base_url,init_user,admin_api)
        if task == "libloop":
            libloop(rbimmich) # Get Libraries
        elif task == "tagloop":
            tagloop(rbimmich)  # Get Tags
        elif task == "tagdelete":
            tagdelete(rbimmich) # Delete Tags
        elif task == "deleteloop":
            deleteloop(rbimmich) # Delete Albums
        elif task == "updateloop": 
            update_album_dict = updateloop(rbimmich,api_key) # Update album modified date
        elif task == "createloop": 
            createloop(rbimmich,init_user,api_key,album_dict) # Create or update assets in albums

    if task == "updateloop":
        sorted_data_keys = json.dumps({k: update_album_dict[k] for k in sorted(update_album_dict)})
        update_album_dict = json.loads(sorted_data_keys)
        rbimmich.update_albums(update_album_dict)

    elif task == "createloop":
        sorted_data_keys = json.dumps({k: album_dict[k] for k in sorted(album_dict)})
        album_dict = json.loads(sorted_data_keys)
        for k,v in album_dict.items():
            print(k)
        rbimmich.createAlbum(album_dict,album_final) 

# Get Libraries from mainexecutor():
def libloop(rbimmich):
        libraries = rbimmich.get_libraries() 
        print(json.dumps(libraries))

# Get tags from mainexecutor():
def tagloop(rbimmich):
        taglist = rbimmich.gettags()
        return taglist

# Delete tags collected from mainexecutor():
def tagdelete(rbimmich):
    taglist = rbimmich.gettags()
    for tag in taglist:
        tag_id=tag['id']
        print(f"deleting {tag_id}")
        rbimmich.delete_tags(tag_id)

# Update albums so execution date is last modified for all albums from mainexecutor():
def updateloop(rbimmich,api_key):
    local=True
    album_ids,album_list = rbimmich.get_albums(local)
    for albumname in album_list['album']:
        album_id = album_list['album'][albumname]
        update_album_dict[albumname]={}
        update_album_dict[albumname]['album_id']=album_id
        update_album_dict[albumname]['api_key']=api_key
    return update_album_dict

# Delete albums collected from mainexecutor():
def deleteloop(rbimmich):
        local=False
        album_ids,album_list = rbimmich.get_albums(local)
        for album_id in album_ids:
            print(f"deleting {album_id}")
            rbimmich.delete_album(album_id)

# Create albums collected from mainexecutor():
def createloop(rbimmich,init_user,api_key,album_dict):
    local = False
    album_ids,album_list = rbimmich.get_albums(local)
    immich_users = rbimmich.get_users()
    AlbumUsers,set_user_id = rbimmich.build_album_users(immich_users,init_user,to_share)
    print(f"User ID: \t \t \t \t {set_user_id}")
    libraries = rbimmich.get_libraries() 
    search_lib = rbimmich.get_search_lib(set_user_id,libraries)
    assetsReceived = rbimmich.get_assets(asset_limit,search_lib)
    # print("Initializing Folders build")
    # user_album_dict = rbimmich.build_album_dict(assetsReceived,AlbumUsers,init_user,album_dict,api_key)
    # print("Initializing Tags build")
    tag_album_dict = rbimmich.build_album_dict_by_tag(assetsReceived,AlbumUsers,init_user,album_dict,api_key)
    album_dict = tag_album_dict
    album_final.update(album_list['album'])
