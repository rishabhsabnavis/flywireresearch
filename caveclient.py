from caveclient import CAVEclient



client = CAVEclient("flywire_fafb_public")
client.auth.get_new_token()
print("Client setup successfully")




root_id = '720575940625102224'



root_info = client.chunkedgraph.get_root_id(root_id)
print("Root info:", root_info)