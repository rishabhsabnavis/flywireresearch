from caveclient import CAVEclient
import os
from fafbseg import flywire
import navis




#Setup Cave
client = CAVEclient("flywire_fafb_public")
client.auth.save_token(token='b647de7b3ecda31cdb9c04e538de1f20', overwrite=True)





#Put in desired root_id here!
root_id = '720575940625102224'



root_info = client.chunkedgraph.get_root_id(root_id)
print("Root info:", root_info)


#Get Children
#children = client.chunkedgraph.get_children(root_id)
#print("Children:", children)



#setup ff
flywire.set_default_dataset("public")


#Mesh Neuron and Plotting
meshy = flywire.get_mesh_neuron(root_id)

navis.plot3d(meshy, color='red', soma=True, connectors=True)




