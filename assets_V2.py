import os
# import settings
import tasks

os.system('clear')

task="createloop"
# task="updateloop"
# task="libloop"
# task="tagloop"
# task="tagdelete"
# task="deleteloop"


'''
init_users['1'] = "Ron Bruins"
init_users['2'] = "Ron Mirjam"
init_users['3'] = "Mirjam Nijburg"
init_users['4'] = "Julian Bruins"
init_users['5'] = "Thibault Bruins"
init_users['6'] = "Sandra Veld"
'''

# user_exec=["1"]
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

