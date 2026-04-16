import os
# import settings
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
# task="delete"


#task="getassetinfo"
#task="debug"

# for user in 3,5:
#     print(user)
#     task="create_by_tag"

task="create_by_tag"

init_users = settings.init_users
iun = "4"
'''
init_users['1'] = "Ron Bruins"
init_users['2'] = "Ron Mirjam"
init_users['3'] = "Mirjam Nijburg"
init_users['4'] = "Julian Bruins"
init_users['5'] = "Thibault Bruins"
init_users['6'] = "Sandra Veld"
init_users['9'] = "Greetje Nijburg"
'''

# user_exec=["5"]
# user_exec=["4"]
user_exec=["2","3","4","5","9","1"]
# album_dict = {}
task == "debug"
def main():
    if task == "createloop":
        tasks.createloop(user_exec)
        tasks.update_album_list(user_exec)
    elif task == "deleteloop":
        tasks.deleteloop(user_exec)
    elif task == "tagloop":
         tasks.tagloop(user_exec)
    elif task == "libloop":
         tasks.libloop(user_exec)
    elif task == "updateloop":
        tasks.update_album_list(user_exec)
    elif task == "tagdelete":
        tasks.tagdelete(user_exec)


# def warn(init_user):
#     wait = input(f"Task: {task.upper()} \nUser: {init_user} \n\n#####      Are you sure, then press ENTER  #####\n#####        Or CTRL-C to stop             #####")

if __name__ == '__main__':
    main()

