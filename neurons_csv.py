#!/usr/bin/env python3


import pandas as pd
from fafbseg import flywire
import navis
import numpy as np

def get_upstream_neurons_csv(root_id, output_file=None, stream=""):
   
    try:
        is_downstream = stream.strip().lower() == "downstream"
        direction = "downstream" if is_downstream else "upstream"
        
        print(f"Fetching {direction} neurons for root ID: {root_id}...")
        #flywire.set_default_dataset("production")

        if is_downstream:
            conn_df = flywire.synapses.get_connectivity(int(root_id), upstream=False, downstream=True)
        else:
            conn_df = flywire.synapses.get_connectivity(int(root_id), upstream=True, downstream=False)

        if conn_df.empty:
            print("No connectivity data found for this root ID")
            return None
        
        # Extract partner neurons based on direction
        if is_downstream:
            # For downstream: root_id is pre, partners are post
            partners = conn_df[conn_df["pre"] == int(root_id)]["post"].unique().tolist()
            partner_connections = conn_df[conn_df["pre"] == int(root_id)]
        else:
            # For upstream: root_id is post, partners are pre
            partners = conn_df[conn_df["post"] == int(root_id)]["pre"].unique().tolist()
            partner_connections = conn_df[conn_df["post"] == int(root_id)]
        
        partners = [int(x) for x in partners]
        
        print(f"Found {len(partners)} {direction} neurons")
        print("Fetching synapse counts...")
        
        # Create a lookup dictionary for synapse counts from connectivity data
        synapse_lookup = {}
        for _, row in partner_connections.iterrows():
            if is_downstream:
                synapse_lookup[int(row["post"])] = int(row["weight"])
            else:
                synapse_lookup[int(row["pre"])] = int(row["weight"])
        
        # Create CSV data
        csv_rows = []
        
        for partner_id in partners:
            # Get synapse count for this pair from the lookup
            synapse_count = synapse_lookup.get(partner_id, 0)
            
            csv_rows.append({
                "partner_neuron_id": partner_id,
                "synapse_count": synapse_count,
                "connection_type": direction
            })
        
        # Create DataFrame and save
        df = pd.DataFrame(csv_rows)
        
        if output_file is None:
            output_file = f"{direction}_neurons_{root_id}.csv"
        
        df.to_csv(output_file, index=False)
        
        print(f"✅ Saved {len(df)} {direction} neurons to {output_file}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_upstream_with_types_csv(root_id, output_file=None, stream=""):
    """
    Get upstream/downstream neurons with their cell types and save to CSV
    
    Args:
        root_id (str): The root ID to get neurons for
        output_file (str, optional): Output CSV filename
        stream (str): "upstream" or "downstream"
    """
    try:
        is_downstream = stream.strip().lower() == "downstream"
        direction = "downstream" if is_downstream else "upstream"
        
        print(f"Fetching {direction} neurons with types for root ID: {root_id}...")
        
        if is_downstream:
            conn_df = flywire.synapses.get_connectivity(int(root_id), upstream=False, downstream=True)
        else:
            conn_df = flywire.synapses.get_connectivity(int(root_id), upstream=True, downstream=False)

        if conn_df.empty:
            print("No connectivity data found for this root ID")
            return None
        
        # Extract partner neurons based on direction
        if is_downstream:
            # For downstream: root_id is pre, partners are post
            partners = conn_df[conn_df["pre"] == int(root_id)]["post"].unique().tolist()
            partner_connections = conn_df[conn_df["pre"] == int(root_id)]
        else:
            # For upstream: root_id is post, partners are pre
            partners = conn_df[conn_df["post"] == int(root_id)]["pre"].unique().tolist()
            partner_connections = conn_df[conn_df["post"] == int(root_id)]
        
        partners = [int(x) for x in partners]
        
        print(f"Found {len(partners)} {direction} neurons")
        print("Fetching synapse counts...")
        
        # Create a lookup dictionary for synapse counts from connectivity data
        synapse_lookup = {}
        for _, row in partner_connections.iterrows():
            if is_downstream:
                synapse_lookup[int(row["post"])] = int(row["weight"])
            else:
                synapse_lookup[int(row["pre"])] = int(row["weight"])
        
        print(f"Fetching cell types for {direction} neurons...")
        
        # Create CSV data
        csv_rows = []
        
        for i, partner_id in enumerate(partners):
            if i % 50 == 0:  # Progress indicator
                print(f"  Progress: {i}/{len(partners)} neurons processed...")
            
            # Get synapse count for this pair from the lookup
            synapse_count = synapse_lookup.get(partner_id, 0)
            
            # Get cell type and brain side for this partner
            try:
                partner_info = flywire.search_annotations(str(partner_id))
                if not partner_info.empty:
                    # Get cell type - try hemibrain_type first, then cell_type
                    cell_type = partner_info.iloc[0].get('hemibrain_type', 
                               partner_info.iloc[0].get('cell_type', 'unknown'))
                    if pd.isna(cell_type):
                        cell_type = 'unknown'
                    
                    # Get brain side
                    brain_side = partner_info.iloc[0].get('side', 'unknown')
                    if pd.isna(brain_side):
                        brain_side = 'unknown'
                else:
                    cell_type = 'unknown'
                    brain_side = 'unknown'
            except:
                cell_type = 'unknown'
                brain_side = 'unknown'
            
            csv_rows.append({
                "partner_neuron_id": partner_id,
                "synapse_count": synapse_count,
                "partner_cell_type": cell_type,
                "partner_brain_side": brain_side,
                "connection_type": direction
            })
        
        # Create DataFrame and save
        df = pd.DataFrame(csv_rows)
        
        if output_file is None:
            output_file = f"{direction}_neurons_with_types_{root_id}.csv"
        
        df.to_csv(output_file, index=False)
        
        print(f"✅ Saved {len(df)} {direction} neurons to {output_file}")
        
        # Show cell type and brain side summary
        cell_type_counts = df['partner_cell_type'].value_counts()
        brain_side_counts = df['partner_brain_side'].value_counts()
        
        print(f"\n{direction.capitalize()} cell type summary:")
        for ctype, count in cell_type_counts.head(10).items():
            print(f"   - {ctype}: {count}")
        
        print(f"\n{direction.capitalize()} brain side summary:")
        for side, count in brain_side_counts.items():
            print(f"   - {side}: {count}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_comprehensive_partners_csv(root_id, output_file=None, stream=""):
    """
    Get upstream/downstream neurons with comprehensive information matching the example CSV format
    
    Args:
        root_id (str): The root ID to get neurons for
        output_file (str, optional): Output CSV filename
        stream (str): "upstream" or "downstream"
    """
    try:
        is_downstream = stream.strip().lower() == "downstream"
        direction = "downstream" if is_downstream else "upstream"

        
        
        print(f"Fetching comprehensive {direction} neuron data for root ID: {root_id}...")
        
        if is_downstream:
            conn_df = flywire.synapses.get_connectivity(int(root_id), upstream=False, downstream=True)
        else:
            conn_df = flywire.synapses.get_connectivity(int(root_id), upstream=True, downstream=False)

        if conn_df.empty:
            print("No connectivity data found for this root ID")
            return None
        
        # Extract partner neurons based on direction
        if is_downstream:
            # For downstream: root_id is pre, partners are post
            partners = conn_df[conn_df["pre"] == int(root_id)]["post"].unique().tolist()
            partner_connections = conn_df[conn_df["pre"] == int(root_id)]
        else:
            # For upstream: root_id is post, partners are pre
            partners = conn_df[conn_df["post"] == int(root_id)]["pre"].unique().tolist()
            partner_connections = conn_df[conn_df["post"] == int(root_id)]
        
        partners = [int(x) for x in partners]
        
        print(f"Found {len(partners)} {direction} neurons")
        print("Fetching comprehensive neuron data...")
        
        # Create a lookup dictionary for synapse counts from connectivity data
        synapse_lookup = {}
        for _, row in partner_connections.iterrows():
            if is_downstream:
                synapse_lookup[int(row["post"])] = int(row["weight"])
            else:
                synapse_lookup[int(row["pre"])] = int(row["weight"])
        
        # Get synapse counts for all partners at once
        print("Fetching synapse counts for all partners...")
        try:
            synapse_counts_df = flywire.synapses.get_synapse_counts(partners)
        except Exception as e:
            print(f"Warning: Could not fetch synapse counts: {e}")
            synapse_counts_df = None
        
        # Create CSV data
        csv_rows = []
        
        for i, partner_id in enumerate(partners):
            if i % 25 == 0:  # Progress indicator (more frequent since this is slower)
                print(f"  Progress: {i}/{len(partners)} neurons processed...")
            
            # Get synapse count for this pair from the lookup
            syn_count = synapse_lookup.get(partner_id, 0)
            
            # Get comprehensive neuron information
            try:
                partner_info = flywire.search_annotations(str(partner_id), verbose=False)
                if not partner_info.empty:
                    info = partner_info.iloc[0]
                    
                    # Extract all the fields from the standard annotations
                    # Use direct bracket access instead of .get()
                    nt_type = info['top_nt'] if pd.notna(info['top_nt']) else ''
                    flow = info['flow'] if pd.notna(info['flow']) else ''
                    super_class = info['super_class'] if pd.notna(info['super_class']) else ''
                    cell_class = info['cell_class'] if pd.notna(info['cell_class']) else ''
                    sub_class = info['cell_sub_class'] if pd.notna(info['cell_sub_class']) else ''
                    
                    # Try hemibrain_type first, then cell_type
                    if pd.notna(info['hemibrain_type']):
                        cell_type = info['hemibrain_type']
                    elif pd.notna(info['cell_type']):
                        cell_type = info['cell_type']
                    else:
                        cell_type = ''
                    
                    hemilineage = info['ito_lee_hemilineage'] if pd.notna(info['ito_lee_hemilineage']) else ''
                    nerve = info['nerve'] if pd.notna(info['nerve']) else ''
                    side = info['side'] if pd.notna(info['side']) else ''
                    
                    # Get input/output synapse counts
                    input_synapses = 0
                    output_synapses = 0
                    if synapse_counts_df is not None and partner_id in synapse_counts_df.index:
                        input_synapses = int(synapse_counts_df.loc[partner_id, 'post'])
                        output_synapses = int(synapse_counts_df.loc[partner_id, 'pre'])
                    
                else:
                    # Default values if no annotation found
                    nt_type = ''
                    flow = ''
                    super_class = ''
                    cell_class = ''
                    sub_class = ''
                    cell_type = ''
                    hemilineage = ''
                    nerve = ''
                    side = ''
                    input_synapses = 0
                    output_synapses = 0
                    
            except Exception as e:
                print(f"Warning: Error fetching data for neuron {partner_id}: {e}")
                # Default values on error
                nt_type = ''
                flow = ''
                super_class = ''
                cell_class = ''
                sub_class = ''
                cell_type = ''
                hemilineage = ''
                nerve = ''
                side = ''
                input_synapses = 0
                output_synapses = 0
            
            csv_rows.append({
                "root_id": partner_id,
                "nt_type": nt_type,
                "flow": flow,
                "super_class": super_class,
                "class": cell_class,
                "sub_class": sub_class,
                "cell_type": cell_type,
                "hemilineage": hemilineage,
                "nerve": nerve,
                "side": side,
                "input_synapses": input_synapses,
                "output_synapses": output_synapses,
                "Syn": syn_count
            })
        
        # Create DataFrame and save
        df = pd.DataFrame(csv_rows)
        
        if output_file is None:
            output_file = f"{direction}_neurons_comprehensive_{root_id}.csv"
        
        df.to_csv(output_file, index=False)
        
        print(f"✅ Saved {len(df)} {direction} neurons to {output_file}")
        
        # Show summary statistics
        print(f"\n{direction.capitalize()} neuron summary:")
        print(f"   - Total neurons: {len(df)}")
        print(f"   - With cell type info: {len(df[df['cell_type'] != 'unknown'])}")
        print(f"   - Left hemisphere: {len(df[df['side'] == 'left'])}")
        print(f"   - Right hemisphere: {len(df[df['side'] == 'right'])}")
        
        # Show top cell types
        cell_type_counts = df['cell_type'].value_counts()
        print(f"\nTop cell types:")
        for ctype, count in cell_type_counts.head(10).items():
            if ctype != 'unknown':
                print(f"   - {ctype}: {count}")
        
        return output_file
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

# Example usage
if __name__ == "__main__":
    print("Upstream/Downstream Neurons CSV Generator")
    print("=" * 40)
    
    # Get root ID from user
    root_id = input("Enter the root ID: ").strip()
    
    if not root_id:
        print("No root ID provided. Exiting.")
        exit()
    

    # stream direction choice
    print("\nChoose stream direction:")
    print("1. Upstream")
    print("2. Downstream")
    stream = input("Enter choice (1 or 2): ").strip()
    
    if stream == "2":
        stream = "downstream"
    else:
        stream = "upstream"

    # Get mode choice
    print("\nChoose processing mode:")
    print("1. Simple mode (just partner neuron IDs) - Fast")
    print("2. Detailed mode (with cell types) - Slower")
    print("3. Comprehensive mode (matching example CSV format) - Slowest")
    
    choice = input("Enter choice (1, 2, or 3): ").strip()
    
    if choice == "3":
        result = get_comprehensive_partners_csv(root_id, stream=stream)
    elif choice == "2":
        result = get_upstream_with_types_csv(root_id, stream=stream)
    else:
        result = get_upstream_neurons_csv(root_id, stream=stream)
    
    if result:
        print(f"\n🎉 Success! Check the file: {result}")
    else:
        print("\n💥 Failed to create CSV file")
