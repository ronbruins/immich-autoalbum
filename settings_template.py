#base_url = "https://immich.domain.com/api/"
base_url = "http://192.168.1.171:2283/api/"
album_id = "936f0349-8199-4c80-95f5-4fc4f9b57ee3"
assetid="8b439bc5-68e6-475f-b990-9e8f937e9523"

tag_share_veto = "Mary"
geo_share_veto = "Soccer"

api_keys = {}
api_keys['John']=""
api_keys['Mary']=""
api_keys['Archive']=""


admin_api = api_keys['John']

geo_dict = {}
geo_dict['location 1'] = {'lat': 51.323340222499525, 'lng': 3.8554779826176295}
geo_dict['Location 2'] = {'lat': 51.3611279066105,  'lng': 3.872249469125365}
geo_dict['location 3'] = {'lat': 51.13112471538997,  'lng': 5.6253172844951}

to_share = {}
to_share['John']=["Mary"]
to_share['Mary']=["John"]
to_share['Archive']=["John","Mary"]

cons_albums = {}
cons_albums['Soccer'] = "Soccer Album"

init_users = {}
init_users['1'] = "John"
init_users['2'] = "Mary"
init_users['3'] = "Archive"


