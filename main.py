import os
from fafbseg import flywire
import navis
from caveclient_helper import connect_to_cave, token_setup

#Cave Setup and Connection
connect_to_cave()






#Put in desired root_id here!
root_id = '720575940625102224'








#setup Flywire & Fafbseg
flywire.set_default_dataset("public")

#Mesh Neuron and Plotting
meshy = flywire.get_mesh_neuron(root_id)

#navis.plot3d(meshy, color='red', soma=True, connectors=True)

print(meshy)


