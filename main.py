import os
from fafbseg import flywire
import navis
from caveclient_helper import connect_to_cave, token_setup
from fastapi import FastAPI
import uvicorn
import numpy as np
from neuron_helper import fetch_neuron, get_neuron_by_type
from fastapi.middleware.cors import CORSMiddleware
from fastapi import HTTPException
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

@app.get("/get_neuron_by_type_endpoint/{neuron_type}")
async def get_neuron_by_type_endpoint(neuron_type: str):
    try:
        neuron_info = get_neuron_by_type(neuron_type)
        return neuron_info
    except Exception as e:
        return {"error": str(e), "neuron_type": neuron_type}


#@app.get("/get_annotations_by_type/{neuron_type}")
#async def get_annotations_by_type(neuron_type: str): 
 



@app.get("/neuron_partners/{cell_type}")
async def neuron_partners(cell_type: str):
    # 1. Find neuron(s) matching the cell type


    neurons = flywire.search_annotations(cell_type, exact = True)

    if neurons.empty:
        raise HTTPException(status_code=404, detail="Cell type not found")
    


    root_id = neurons.iloc[0]['root_id']  # Choose the first match, or loop for all

    # 2. Get connectivity
    conn_df = flywire.synapses.get_connectivity(root_id)
    if conn_df.empty:
        return {"upstream": [], "downstream": []}

    # 3. Extract partners
    upstream = conn_df[conn_df["post"] == root_id]["pre"].unique().tolist()
    downstream = conn_df[conn_df["pre"] == root_id]["post"].unique().tolist()
    
    # Convert numpy types to Python types for JSON serialization
    upstream = [int(x) for x in upstream]
    downstream = [int(x) for x in downstream]
    
    return {
        "root_id": int(root_id),
        "upstream_partners": upstream,
        "downstream_partners": downstream
    }



@app.get("/get_neuron_type/{root_id}")
async def get_neuron_type(root_id: str):
    try:
        neuron_info = flywire.search_community_annotations(root_id)
        return neuron_info
    except Exception as e:
        return {"error": str(e), "root_id": root_id}

@app.get("/neuron_info/{root_id}")
async def neuron_info(root_id: str):
    try:
        neuron_info = fetch_neuron(root_id)  # No need to pass client
        return neuron_info
    except Exception as e:
        return {"error": str(e), "root_id": root_id}

#Cave Setup and Connection



app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



#Put in desired root_id here!
root_id = '720575940625102224'








#setup Flywire & Fafbseg
flywire.set_default_dataset("public")

#Mesh Neuron and Plotting
#meshy = flywire.get_mesh_neuron(root_id)

#navis.plot3d(meshy, color='red', soma=True, connectors=True)


uvicorn.run(app, port = 8002)