import os
from fafbseg import flywire
import navis
from caveclient_helper import connect_to_cave, token_setup
from fastapi import FastAPI
import uvicorn
import numpy as np
from neuron_helper import fetch_neuron
app = FastAPI()
client = connect_to_cave()


@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/mesh_neuron/{root_id}")
async def mesh_neuron(root_id: str):
    try:
        meshy = flywire.get_mesh_neuron(root_id)
        
        # Convert mesh data to JSON-serializable format
        mesh_data = {
            "root_id": root_id,
            "vertices": meshy.vertices.tolist() if hasattr(meshy, 'vertices') else [],
            "faces": meshy.faces.tolist() if hasattr(meshy, 'faces') else [],
            "soma": meshy.soma.tolist() if hasattr(meshy, 'soma') else None,
            "connectors": meshy.connectors.to_dict('records') if hasattr(meshy, 'connectors') and meshy.connectors is not None else [],
            "n_vertices": int(meshy.n_vertices) if hasattr(meshy, 'n_vertices') else 0,
            "n_faces": int(meshy.n_faces) if hasattr(meshy, 'n_faces') else 0,
            "name": str(meshy.name) if hasattr(meshy, 'name') else root_id
        }
        
        return mesh_data
    except Exception as e:
        return {"error": str(e), "root_id": root_id}



@app.get("/neuron_info/{root_id}")
async def neuron_info(root_id: str):
    try:
        neuron_info = fetch_neuron(root_id, client)
        return neuron_info
    except Exception as e:
        return {"error": str(e), "root_id": root_id}

#Cave Setup and Connection







#Put in desired root_id here!
root_id = '720575940625102224'








#setup Flywire & Fafbseg
flywire.set_default_dataset("public")

#Mesh Neuron and Plotting
#meshy = flywire.get_mesh_neuron(root_id)

#navis.plot3d(meshy, color='red', soma=True, connectors=True)


uvicorn.run(app, port = 8002)