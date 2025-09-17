#!/usr/bin/env python3
"""
Simple script to fetch neuron partners and save to CSV
"""

import requests
import pandas as pd

def fetch_and_save_partners(cell_type, output_file=None):
    """
    Fetch neuron partners from API and save to CSV
    
    Args:
        cell_type (str): The cell type to fetch partners for
        output_file (str, optional): Output CSV filename
    """
    # API endpoint
    url = f"http://localhost:8002/neuron_partners/{cell_type}"
    
    try:
        print(f"Fetching partners for {cell_type}...")
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Create CSV data
        csv_rows = []
        
        # Add upstream partners
        for partner in data.get("upstream_partners", []):
            csv_rows.append({
                "neuron_id": data["root_id"],
                "neuron_type": cell_type,
                "partner_id": partner,
                "connection_type": "upstream"
            })
        
        # Add downstream partners
        for partner in data.get("downstream_partners", []):
            csv_rows.append({
                "neuron_id": data["root_id"],
                "neuron_type": cell_type,
                "partner_id": partner,
                "connection_type": "downstream"
            })
        
        # Create DataFrame and save
        df = pd.DataFrame(csv_rows)
        
        if output_file is None:
            output_file = f"{cell_type}_partners.csv"
        
        df.to_csv(output_file, index=False)
        
        print(f"✅ Saved {len(df)} partner relationships to {output_file}")
        print(f"   - {len(data.get('upstream_partners', []))} upstream partners")
        print(f"   - {len(data.get('downstream_partners', []))} downstream partners")
        
        return output_file
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Make sure your FastAPI server is running on localhost:8002")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Example usage
if __name__ == "__main__":
    # Test with a cell type
    cell_type = "DNp32"  # Change this to your desired cell type
    result = fetch_and_save_partners(cell_type)
    
    if result:
        print(f"\n🎉 Success! Check the file: {result}")
    else:
        print("\n💥 Failed to create CSV file")
