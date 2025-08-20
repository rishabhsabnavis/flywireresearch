from caveclient import CAVEclient
import os


client = CAVEclient("flywire_fafb_public")
client.auth.save_token(token='b647de7b3ecda31cdb9c04e538de1f20', overwrite=True)



root_id = '720575940626979621'

root_info = client.chunkedgraph.get_root_id(root_id)
print("Root info:", root_info)

