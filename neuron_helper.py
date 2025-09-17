from fafbseg import flywire
import navis
import numpy as np
from fafbseg.flywire import NeuronCriteria as NC
def fetch_neuron(root_id, client=None):
    """
    Fetch neuron information using the FlyWire API.
    The client parameter is kept for compatibility but not used.
    """
    try:
        # Get neuron annotations using the correct FlyWire function
        neuron_info = flywire.search_annotations(root_id)
        
        if neuron_info.empty:
            # Return basic info if no annotations found
            return [{
                'id': root_id,
                'name': root_id,
                'type': 'unknown',
                'status': 'unknown',
                'size': 0,
                'soma_location': None,
                'timestamp': None,
                'error': 'No annotations found for this neuron'
            }]
        
        # Convert the first row to a dictionary
        result = neuron_info.iloc[0].to_dict()
        
        # Handle NaN values - convert them to None for JSON serialization
        for key, value in result.items():
            if isinstance(value, float) and np.isnan(value):
                result[key] = None
        
        # Add the root_id to ensure it's included
        result['id'] = root_id
        
        return [result]  # Return as list to match original format
    except Exception as e:
        # Fallback to basic info if detailed info fails
        return [{
            'id': root_id,
            'name': root_id,
            'type': 'unknown',
            'status': 'unknown',
            'size': 0,
            'soma_location': None,
            'timestamp': None,
            'error': str(e)
        }]



def get_neuron_by_type(neuron_type: str):
     try:
        neuron_info = flywire.search_annotations(NC.type(neuron_type))
        return neuron_info
     except Exception as e:
        return {"error": str(e), "neuron_type": neuron_type}


