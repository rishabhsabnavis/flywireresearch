import requests
import pandas as pd 
import csv
import json
import sys
import os

# Add parent directory to path to import neuron_helper
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from neuron_helper import get_neuron_by_type

def create_neuron_partner_csv(neuron_type, output_filename=None):
    """
    Create a CSV file with neurons of specified type and their partner neurons.
    
    Args:
        neuron_type (str): The type of neurons to fetch (e.g., "PN", "DNp32", etc.)
        output_filename (str, optional): Output filename. If None, uses f"{neuron_type}_partners.csv"
    
    Returns:
        str: The filename of the created CSV
    """
    try:
        # Get neuron data using the helper function
        print(f"Fetching neurons of type: {neuron_type}")
        neuron_data = get_neuron_by_type(neuron_type)
        
        if isinstance(neuron_data, dict) and "error" in neuron_data:
            print(f"Error fetching data: {neuron_data['error']}")
            return None
        
        # Convert to DataFrame if it's not already
        if not isinstance(neuron_data, pd.DataFrame):
            df = pd.DataFrame(neuron_data)
        else:
            df = neuron_data
        
        if df.empty:
            print(f"No neurons found for type: {neuron_type}")
            return None
        
        print(f"Found {len(df)} neurons of type {neuron_type}")
        
        # Create the partner neurons data
        partner_data = []
        
        for _, row in df.iterrows():
            neuron_id = row.get('id', '')
            neuron_type_name = row.get('type', neuron_type)
            
            # Extract partner neurons from the 'per_roi' column if it exists
            partner_neurons = []
            if 'per_roi' in row and pd.notna(row['per_roi']):
                try:
                    # Parse the JSON string in per_roi column
                    per_roi_data = json.loads(row['per_roi']) if isinstance(row['per_roi'], str) else row['per_roi']
                    
                    # Extract all partner neuron types from the per_roi data
                    if isinstance(per_roi_data, dict):
                        partner_neurons = list(per_roi_data.keys())
                except (json.JSONDecodeError, TypeError):
                    print(f"Warning: Could not parse per_roi data for neuron {neuron_id}")
                    partner_neurons = []
            
            # If no partners found in per_roi, try to extract from other columns
            if not partner_neurons:
                # Look for partner information in other columns
                for col in df.columns:
                    if col not in ['id', 'type', 'instance', 'status', 'weight', 'post', 'pre', 'size', 'per_roi']:
                        if pd.notna(row[col]) and row[col] != '':
                            partner_neurons.append(f"{col}:{row[col]}")
            
            # Join partner neurons with semicolon separator
            partner_neurons_str = '; '.join(partner_neurons) if partner_neurons else 'No partners found'
            
            partner_data.append({
                'neuron_id': neuron_id,
                'neuron_type': neuron_type_name,
                'partner_neurons': partner_neurons_str
            })
        
        # Create DataFrame for the output
        output_df = pd.DataFrame(partner_data)
        
        # Set output filename
        if output_filename is None:
            output_filename = f"{neuron_type}_partners.csv"
        



        # Save to CSV
        output_df.to_csv(output_filename, index=False)
        print(f"CSV file created: {output_filename}")
        print(f"File contains {len(output_df)} rows with neuron-partner relationships")





        return output_filename
        
    except Exception as e:
        print(f"Error creating CSV: {str(e)}")
        return None




def main():
    print("Neuron Partner CSV Generator")
    print("=" * 40)
    
    # Get neuron type from user
    neuron_type = input("Enter the neuron type (e.g., PN, DNp32, SLP131): ").strip()
    
    if not neuron_type:
        print("No neuron type provided. Exiting.")
        return
    
    # Get optional output filename
    output_filename = input(f"Enter output filename (press Enter for '{neuron_type}_partners.csv'): ").strip()
    if not output_filename:
        output_filename = None
    
    # Create the CSV
    result = create_neuron_partner_csv(neuron_type, output_filename)
    
    if result:
        print(f"\nSuccess! CSV file created: {result}")
        
        # Show a preview of the data
        try:
            preview_df = pd.read_csv(result)
            print(f"\nPreview of the data (first 5 rows):")
            print(preview_df.head())
        except Exception as e:
            print(f"Could not preview data: {e}")
    else:
        print("Failed to create CSV file.")

if __name__ == "__main__":
    main()