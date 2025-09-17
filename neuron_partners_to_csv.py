#!/usr/bin/env python3


import requests
import pandas as pd
import json
import sys
import os

def get_neuron_partners_from_api(cell_type, base_url="http://localhost:8002"):
    """
    Fetch neuron partners data from the FastAPI endpoint
    
    Args:
        cell_type (str): The type of neuron to get partners for
        base_url (str): Base URL of the FastAPI server
        
    Returns:
        dict: Response data from the API
    """
    try:
        url = f"{base_url}/neuron_partners/{cell_type}"
        print(f"Fetching data from: {url}")
        
        response = requests.get(url)
        response.raise_for_status()  # Raises an HTTPError for bad responses
        
        return response.json()
        
    except requests.exceptions.ConnectionError:
        print(f"Error: Could not connect to {base_url}. Make sure your FastAPI server is running.")
        return None
    except requests.exceptions.HTTPError as e:
        print(f"HTTP Error: {e}")
        return None
    except Exception as e:
        print(f"Error fetching data: {e}")
        return None

def create_partners_csv(cell_type, output_filename=None, base_url="http://localhost:8002"):
    """
    Create a CSV file with neuron partners data from the API
    
    Args:
        cell_type (str): The type of neuron to get partners for
        output_filename (str, optional): Output filename. If None, uses f"{cell_type}_partners.csv"
        base_url (str): Base URL of the FastAPI server
        
    Returns:
        str: The filename of the created CSV
    """
    try:
        # Get data from API
        data = get_neuron_partners_from_api(cell_type, base_url)
        
        if not data:
            print("Failed to fetch data from API")
            return None
        
        # Check if we got an error response
        if "error" in data:
            print(f"API Error: {data['error']}")
            return None
        
        # Prepare data for CSV
        csv_data = []
        
        # Add upstream partners
        for partner_id in data.get("upstream_partners", []):
            csv_data.append({
                "neuron_id": data.get("root_id"),
                "neuron_type": cell_type,
                "partner_id": partner_id,
                "connection_type": "upstream"
            })
        
        # Add downstream partners
        for partner_id in data.get("downstream_partners", []):
            csv_data.append({
                "neuron_id": data.get("root_id"),
                "neuron_type": cell_type,
                "partner_id": partner_id,
                "connection_type": "downstream"
            })
        
        if not csv_data:
            print("No partner data found")
            return None
        
        # Create DataFrame
        df = pd.DataFrame(csv_data)
        
        # Set output filename
        if output_filename is None:
            output_filename = f"{cell_type}_partners.csv"
        
        # Save to CSV
        df.to_csv(output_filename, index=False)
        print(f"CSV file created: {output_filename}")
        print(f"File contains {len(df)} partner relationships")
        
        # Show summary
        upstream_count = len(data.get("upstream_partners", []))
        downstream_count = len(data.get("downstream_partners", []))
        print(f"Summary: {upstream_count} upstream partners, {downstream_count} downstream partners")
        
        return output_filename
        
    except Exception as e:
        print(f"Error creating CSV: {str(e)}")
        return None

def main():
    """
    Main function to get user input and create CSV files
    """
    print("Neuron Partners to CSV Generator")
    print("=" * 40)
    
    # Get cell type from user
    cell_type = input("Enter the cell type (e.g., DNp32, SLP131, LHAD1g1): ").strip()
    
    if not cell_type:
        print("No cell type provided. Exiting.")
        return
    
    # Get optional output filename
    output_filename = input(f"Enter output filename (press Enter for '{cell_type}_partners.csv'): ").strip()
    if not output_filename:
        output_filename = None
    
    # Get optional base URL
    base_url = input("Enter API base URL (press Enter for 'http://localhost:8002'): ").strip()
    if not base_url:
        base_url = "http://localhost:8002"
    
    # Create the CSV
    result = create_partners_csv(cell_type, output_filename, base_url)
    
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
