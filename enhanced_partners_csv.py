#!/usr/bin/env python3
"""
Enhanced script to fetch neuron partners with cell types and save to CSV
"""



import requests
import pandas as pd
import time
from collections import defaultdict

def get_partner_info(partner_id, base_url="http://localhost:8002"):
    """
    Get information about a partner neuron
    
    Args:
        partner_id (int): The ID of the partner neuron
        base_url (str): Base URL of the FastAPI server
        
    Returns:
        dict: Partner neuron information
    """
    try:
        url = f"{base_url}/neuron_info/{partner_id}"
        response = requests.get(url)
        response.raise_for_status()
        
        data = response.json()
        
        # Extract cell type from the response
        if isinstance(data, list) and len(data) > 0:
            return data[0]  # Return first item if it's a list
        return data
        
    except Exception as e:
        print(f"Warning: Could not fetch info for partner {partner_id}: {e}")
        return {"type": "unknown", "id": partner_id}

def fetch_and_save_partners_with_types(cell_type, output_file=None, include_partner_types=True):
    """
    Fetch neuron partners from API and save to CSV with partner cell types
    
    Args:
        cell_type (str): The cell type to fetch partners for
        output_file (str, optional): Output CSV filename
        include_partner_types (bool): Whether to fetch partner cell types (slower)
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
        
        # Get all unique partner IDs
        all_partners = set(data.get("upstream_partners", []) + data.get("downstream_partners", []))
        
        # Cache for partner info to avoid duplicate API calls
        partner_info_cache = {}
        
        if include_partner_types:
            print(f"Fetching cell types for {len(all_partners)} unique partners...")
            
            for i, partner_id in enumerate(all_partners):
                if i % 50 == 0:  # Progress indicator
                    print(f"  Progress: {i}/{len(all_partners)} partners processed...")
                
                partner_info = get_partner_info(partner_id)
                partner_info_cache[partner_id] = partner_info.get("type", "unknown")
                
                # Small delay to avoid overwhelming the API
                time.sleep(0.01)
        
        # Add upstream partners
        for partner in data.get("upstream_partners", []):
            partner_type = partner_info_cache.get(partner, "unknown") if include_partner_types else "unknown"
            csv_rows.append({
                "neuron_id": data["root_id"],
                "neuron_type": cell_type,
                "partner_id": partner,
                "partner_type": partner_type,
                "connection_type": "upstream"
            })
        
        # Add downstream partners
        for partner in data.get("downstream_partners", []):
            partner_type = partner_info_cache.get(partner, "unknown") if include_partner_types else "unknown"
            csv_rows.append({
                "neuron_id": data["root_id"],
                "neuron_type": cell_type,
                "partner_id": partner,
                "partner_type": partner_type,
                "connection_type": "downstream"
            })
        
        # Create DataFrame and save
        df = pd.DataFrame(csv_rows)
        
        if output_file is None:
            output_file = f"{cell_type}_partners_with_types.csv"
        
        df.to_csv(output_file, index=False)
        
        print(f"✅ Saved {len(df)} partner relationships to {output_file}")
        print(f"   - {len(data.get('upstream_partners', []))} upstream partners")
        print(f"   - {len(data.get('downstream_partners', []))} downstream partners")
        
        if include_partner_types:
            # Show partner type summary
            partner_type_counts = df['partner_type'].value_counts()
            print(f"\nPartner type summary:")
            for ptype, count in partner_type_counts.head(10).items():
                print(f"   - {ptype}: {count}")
        
        return output_file
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to API. Make sure your FastAPI server is running on localhost:8002")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def fetch_and_save_partners_fast(cell_type, output_file=None):
    """
    Fast version without partner types (for quick testing)
    """
    return fetch_and_save_partners_with_types(cell_type, output_file, include_partner_types=False)

def batch_fetch_partners(cell_types, include_partner_types=True):
    """
    Fetch partners for multiple cell types in batch
    
    Args:
        cell_types (list): List of cell types to process
        include_partner_types (bool): Whether to fetch partner cell types
    """
    results = []
    
    for i, cell_type in enumerate(cell_types):
        print(f"\n{'='*50}")
        print(f"Processing {i+1}/{len(cell_types)}: {cell_type}")
        print(f"{'='*50}")
        
        result = fetch_and_save_partners_with_types(cell_type, include_partner_types=include_partner_types)
        results.append(result)
        
        # Small delay between requests
        if i < len(cell_types) - 1:
            time.sleep(1)
    
    return results

# Example usage
if __name__ == "__main__":
    print("Enhanced Neuron Partners to CSV Generator")
    print("=" * 50)
    
    # Get cell type from user
    cell_type = input("Enter the cell type (e.g., DNp32, SLP131): ").strip()
    
    if not cell_type:
        print("No cell type provided. Exiting.")
        exit()
    
    # Get mode choice
    print("\nChoose processing mode:")
    print("1. Fast mode (no partner types) - Quick")
    print("2. Full mode (with partner types) - Slower but detailed")
    print("3. Batch mode (multiple cell types)")
    
    choice = input("Enter choice (1, 2, or 3): ").strip()
    
    if choice == "1":
        result = fetch_and_save_partners_fast(cell_type)
    elif choice == "2":
        result = fetch_and_save_partners_with_types(cell_type)
    elif choice == "3":
        # Batch mode
        cell_types_input = input("Enter cell types separated by commas: ").strip()
        cell_types = [ct.strip() for ct in cell_types_input.split(",") if ct.strip()]
        
        if not cell_types:
            print("No cell types provided.")
            exit()
        
        include_types = input("Include partner types? (y/n): ").strip().lower() == 'y'
        results = batch_fetch_partners(cell_types, include_types)
        
        print(f"\n🎉 Batch processing complete! Created {len([r for r in results if r])} files.")
        exit()
    else:
        print("Invalid choice. Using fast mode.")
        result = fetch_and_save_partners_fast(cell_type)
    
    if result:
        print(f"\n🎉 Success! Check the file: {result}")
    else:
        print("\n💥 Failed to create CSV file")
