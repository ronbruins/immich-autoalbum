import os
# import settings
import tasks

os.system('clear')

task="createloop"
task="updateloop"
# task="libloop"
# task="tagloop"
# task="tagdelete"
# task="deleteloop"

#deptest piush
'''
init_users['1'] = "Ron Bruins"
init_users['2'] = "Ron Mirjam"
init_users['3'] = "Mirjam Nijburg"
init_users['4'] = "Julian Bruins"
init_users['5'] = "Thibault Bruins"
init_users['6'] = "Sandra Veld"
init_users['9'] = "Greetje Nijburg"
'''

user_exec=["2","3","4","5","9","1"]
user_exec=["1"]
# user_exec=["4"]
# album_dict = {}
# task == "debug"

def main():
    tasks.mainexecutor(user_exec,task) 
    if task == "createloop": 
        tasks.mainexecutor(user_exec,"updateloop")

if __name__ == '__main__':
    main()

