from caveclient import CAVEclient





def connect_to_cave():
    client = CAVEclient("flywire_fafb_public")
    print("Client setup successfully")

def token_initialize():
    client = CAVEclient(server_address = 'https://global.daf-apis.com')
    client.auth.get_new_token()




def token_setup():
    client = CAVEclient(server_address = 'https://global.daf-apis.com')
    client.auth.save_token(token = '6775c8122c31f85d603376492ec4eb21', overwrite  = True)






#token_initialize()
token_setup()
connect_to_cave()