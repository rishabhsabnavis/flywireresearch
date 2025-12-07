#!/usr/bin/env python3


import pandas as pd
from fafbseg import flywire
import navis
import numpy as np
from typing import Optional, List, Dict

try:
    from caveclient import CAVEclient
except Exception:
    CAVEclient = None
from caveclient import CAVEclient

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


def get_comprehensive_partners_csv_caveclient(root_id, output_file=None, stream=""):
    """
    Get upstream/downstream neurons with comprehensive information using CAVECLIENT native functions
    
    Args:
        root_id (str): The root ID to get neurons for
        output_file (str, optional): Output CSV filename
        stream (str): "upstream" or "downstream"
    """
    try:
        from caveclient import CAVEclient
        import pandas as pd
        
        # Initialize CAVECLIENT
        client = CAVEclient("flywire_fafb_public")
        
        is_downstream = stream.strip().lower() == "downstream"
        direction = "downstream" if is_downstream else "upstream"
        
        print(f"Fetching comprehensive {direction} neuron data for root ID: {root_id}...")
        
        # Get connectivity data using CAVECLIENT
        if is_downstream:
            # For downstream: root_id is pre-synaptic
            conn_df = client.materialize.synapse_query(
                pre_ids=int(root_id),
                remove_autapses=True
            )
            partners = conn_df["post_pt_root_id"].unique().tolist()
        else:
            # For upstream: root_id is post-synaptic
            conn_df = client.materialize.synapse_query(
                post_ids=int(root_id),
                remove_autapses=True
            )
            partners = conn_df["pre_pt_root_id"].unique().tolist()
        
        partners = [int(x) for x in partners]
        
        if not partners:
            print("No connectivity data found for this root ID")
            return None
        
        print(f"Found {len(partners)} {direction} neurons")
        
        # Create synapse count lookup
        synapse_lookup = {}
        if is_downstream:
            synapse_counts = conn_df.groupby("post_pt_root_id").size()
            for partner_id in partners:
                synapse_lookup[partner_id] = synapse_counts.get(partner_id, 0)
        else:
            synapse_counts = conn_df.groupby("pre_pt_root_id").size()
            for partner_id in partners:
                synapse_lookup[partner_id] = synapse_counts.get(partner_id, 0)
        
        print("Fetching comprehensive neuron data...")
        
        # Get synapse counts for all partners using CAVECLIENT
        print("Fetching synapse counts for all partners...")
        try:
            # Query synapse counts for all partners
            all_synapses_df = client.materialize.synapse_query(
                pre_ids=partners,
                post_ids=partners,
                remove_autapses=True
            )
            
            # Calculate input/output synapse counts
            input_counts = all_synapses_df.groupby("post_pt_root_id").size()
            output_counts = all_synapses_df.groupby("pre_pt_root_id").size()
            
        except Exception as e:
            print(f"Warning: Could not fetch synapse counts: {e}")
            input_counts = pd.Series(dtype=int)
            output_counts = pd.Series(dtype=int)
        
        # Create CSV data
        csv_rows = []
        
        for i, partner_id in enumerate(partners):
            if i % 25 == 0:
                print(f"  Progress: {i}/{len(partners)} neurons processed...")
            
            # Get synapse count for this pair
            syn_count = synapse_lookup.get(partner_id, 0)
            
            # Get comprehensive neuron information using CAVECLIENT
            try:
                # Query the annotation table for this neuron
                # You'll need to know the specific annotation table name
                # Common ones are: "neuron_information", "cell_metadata", etc.
                annotation_df = client.materialize.query_table(
                    table="neuron_information",  # Adjust table name as needed
                    filter_equal_dict={"root_id": partner_id}
                )
                
                if not annotation_df.empty:
                    info = annotation_df.iloc[0]
                    
                    # Extract fields - adjust column names based on your annotation table
                    nt_type = info.get('top_nt', '') if pd.notna(info.get('top_nt')) else ''
                    flow = info.get('flow', '') if pd.notna(info.get('flow')) else ''
                    super_class = info.get('super_class', '') if pd.notna(info.get('super_class')) else ''
                    cell_class = info.get('cell_class', '') if pd.notna(info.get('cell_class')) else ''
                    sub_class = info.get('cell_sub_class', '') if pd.notna(info.get('cell_sub_class')) else ''
                    
                    # Try hemibrain_type first, then cell_type
                    if pd.notna(info.get('hemibrain_type')):
                        cell_type = info['hemibrain_type']
                    elif pd.notna(info.get('cell_type')):
                        cell_type = info['cell_type']
                    else:
                        cell_type = ''
                    
                    hemilineage = info.get('ito_lee_hemilineage', '') if pd.notna(info.get('ito_lee_hemilineage')) else ''
                    nerve = info.get('nerve', '') if pd.notna(info.get('nerve')) else ''
                    side = info.get('side', '') if pd.notna(info.get('side')) else ''
                    
                    # Get input/output synapse counts
                    input_synapses = int(input_counts.get(partner_id, 0))
                    output_synapses = int(output_counts.get(partner_id, 0))
                    
                else:
                    # Default values if no annotation found
                    nt_type = flow = super_class = cell_class = sub_class = ''
                    cell_type = hemilineage = nerve = side = ''
                    input_synapses = output_synapses = 0
                    
            except Exception as e:
                print(f"Warning: Error fetching data for neuron {partner_id}: {e}")
                # Default values on error
                nt_type = flow = super_class = cell_class = sub_class = ''
                cell_type = hemilineage = nerve = side = ''
                input_synapses = output_synapses = 0
            
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
        print(f"   - With cell type info: {len(df[df['cell_type'] != ''])}")
        print(f"   - Left hemisphere: {len(df[df['side'] == 'left'])}")
        print(f"   - Right hemisphere: {len(df[df['side'] == 'right'])}")
        
        # Show top cell types
        cell_type_counts = df['cell_type'].value_counts()
        print(f"\nTop cell types:")
        for ctype, count in cell_type_counts.head(10).items():
            if ctype != '':
                print(f"   - {ctype}: {count}")
        
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
            output_file = f"{direction}_neurons_comprehensivefafbseg_{root_id}.csv"
        
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

def get_comprehensive_partners_csv_caveclient(root_id, output_file: Optional[str] = None, stream: str = "", datastack: str = "flywire_fafb_public"):
    """
    Comprehensive partners CSV using CAVECLIENT native functions (no FAFBseg).

    Args:
        root_id (str|int): The root ID to get neurons for.
        output_file (str, optional): Output CSV filename.
        stream (str): "upstream" or "downstream" (default upstream).
        datastack (str): CAVE datastack name. Defaults to "flywire_fafb_public".
    """
    if CAVEclient is None:
        print("❌ Error: caveclient not installed/available")
        return None

    try:
        is_downstream = stream.strip().lower() == "downstream"
        direction = "downstream" if is_downstream else "upstream"

        # Initialize client (will use most recent version by default)
        client = CAVEclient(datastack)
        
        # Get the most recent version for display
        try:
            materialization_version = client.materialize.most_recent_version()
            print(f"Using materialization version: {materialization_version}")
        except Exception as e:
            print(f"⚠️  Warning: Could not determine most recent version: {e}")
            materialization_version = None

        # Use synapses_v3_neuropil_v6_merge_view view
        view_name = "synapses_v3_neuropil_v6_merge_view"
        
        # Verify the view exists
        try:
            views = client.materialize.get_views()
            if view_name not in views:
                print(f"⚠️  Warning: View '{view_name}' not found in available views.")
                print(f"   Available views: {sorted(views)[:10]}...")  # Show first 10
                print(f"❌ Error: Could not find view '{view_name}'.")
                return None
            print(f"   Using view: {view_name}")
        except Exception as e:
            print(f"⚠️  Warning: Could not verify view existence: {e}")
            print(f"   Proceeding with view name: {view_name}")

        version_str = f"version={materialization_version}" if materialization_version else "latest version"
        print(f"Fetching comprehensive {direction} neuron data for root ID: {root_id} (view={view_name}, {version_str})...")

        root_id = int(root_id)

        # Query synapses for connectivity and partner extraction using view
        try:
            if is_downstream:
                # For downstream: root_id is pre-synaptic, filter by pre_pt_root_id
                syn_df = client.materialize.query_view(
                    view_name=view_name,
                    filter_equal_dict={"pre_pt_root_id": root_id},
                    split_positions=False,
                )
                partner_col = "post_pt_root_id"
            else:
                # For upstream: root_id is post-synaptic, filter by post_pt_root_id
                syn_df = client.materialize.query_view(
                    view_name=view_name,
                    filter_equal_dict={"post_pt_root_id": root_id},
                    split_positions=False,
                )
                partner_col = "pre_pt_root_id"
        except Exception as e:
            # Try alternative column names if the primary ones fail
            print(f"   ⚠️  Error with primary column names: {e}")
            print(f"   Trying alternative column names...")
            try:
                if is_downstream:
                    syn_df = client.materialize.query_view(
                        view_name=view_name,
                        filter_equal_dict={"pre_root_id": root_id},
                        split_positions=False,
                    )
                    partner_col = "post_root_id"
                else:
                    syn_df = client.materialize.query_view(
                        view_name=view_name,
                        filter_equal_dict={"post_root_id": root_id},
                        split_positions=False,
                    )
                    partner_col = "pre_root_id"
            except Exception as e2:
                print(f"❌ Error querying view: {e2}")
                return None

        if syn_df is None or syn_df.empty:
            print("No connectivity data found for this root ID")
            return None

        if partner_col not in syn_df.columns:
            print(f"❌ Error: Expected partner column not found in view (missing {partner_col}).")
            print(f"   Available columns: {list(syn_df.columns)}")
            return None
        
        # Remove autapses (where pre == post) if present
        if "pre_pt_root_id" in syn_df.columns and "post_pt_root_id" in syn_df.columns:
            syn_df = syn_df[syn_df["pre_pt_root_id"] != syn_df["post_pt_root_id"]]
        elif "pre_root_id" in syn_df.columns and "post_root_id" in syn_df.columns:
            syn_df = syn_df[syn_df["pre_root_id"] != syn_df["post_root_id"]]

        partners: List[int] = sorted({int(x) for x in syn_df[partner_col].dropna().astype(int).tolist() if int(x) != 0 and int(x) != root_id})

        print(f"Found {len(partners)} {direction} neurons")

        # Pairwise synapse counts from root -> partner (or partner -> root)
        synapse_lookup: Dict[int, int] = {}
        counts_series = syn_df.groupby(partner_col).size()
        for pid in partners:
            synapse_lookup[pid] = int(counts_series.get(pid, 0))

        print("Fetching input/output synapse totals for all partners (this may take time)...")
        # Get totals per partner (all outgoing and incoming). We can do two queries:
        # - outputs: pre_ids=partners (where pre is in partners list)
        # - inputs: post_ids=partners (where post is in partners list)
        try:
            # For outputs: query where pre_pt_root_id is in partners list
            outs_df = client.materialize.query_view(
                view_name=view_name,
                filter_in_dict={"pre_pt_root_id": partners},
                split_positions=False,
                limit=None,  # Get all results
            )
            # Remove autapses
            if "pre_pt_root_id" in outs_df.columns and "post_pt_root_id" in outs_df.columns:
                outs_df = outs_df[outs_df["pre_pt_root_id"] != outs_df["post_pt_root_id"]]
            out_partner_col = "pre_pt_root_id" if "pre_pt_root_id" in outs_df.columns else "pre_root_id"
            output_counts = outs_df.groupby(out_partner_col).size() if not outs_df.empty else pd.Series(dtype=int)
        except Exception as e:
            print(f"   ⚠️  Warning: Could not fetch output synapse counts: {e}")
            output_counts = pd.Series(dtype=int)

        try:
            # For inputs: query where post_pt_root_id is in partners list
            ins_df = client.materialize.query_view(
                view_name=view_name,
                filter_in_dict={"post_pt_root_id": partners},
                split_positions=False,
                limit=None,  # Get all results
            )
            # Remove autapses
            if "pre_pt_root_id" in ins_df.columns and "post_pt_root_id" in ins_df.columns:
                ins_df = ins_df[ins_df["pre_pt_root_id"] != ins_df["post_pt_root_id"]]
            in_partner_col = "post_pt_root_id" if "post_pt_root_id" in ins_df.columns else "post_root_id"
            input_counts = ins_df.groupby(in_partner_col).size() if not ins_df.empty else pd.Series(dtype=int)
        except Exception as e:
            print(f"   ⚠️  Warning: Could not fetch input synapse counts: {e}")
            input_counts = pd.Series(dtype=int)

        print("Fetching annotation metadata for partners (best effort)...")
        # Try to locate a neuron metadata table and pull fields if available
        try:
            tables = client.materialize.get_tables()
        except Exception:
            tables = []

        # Heuristic: pick a table that likely contains neuron metadata
        preferred_tables = [
            "flywire_neuron_information",
            "neuron_information",
            "flywire_neurons",
            "cell_metadata",
        ]
        meta_table = next((t for t in preferred_tables if t in tables), None)

        # Columns we hope to find
        wanted_cols = [
            "top_nt", "flow", "super_class", "cell_class", "cell_sub_class",
            "hemibrain_type", "cell_type", "ito_lee_hemilineage", "nerve", "side",
        ]

        # Build CSV rows
        csv_rows = []
        for i, partner_id in enumerate(partners):
            if i % 25 == 0:
                print(f"  Progress: {i}/{len(partners)} neurons processed...")

            syn_count = int(synapse_lookup.get(partner_id, 0))

            nt_type = ""; flow = ""; super_class = ""; cell_class = ""; sub_class = ""
            cell_type = ""; hemilineage = ""; nerve = ""; side = ""
            input_synapses = int(input_counts.get(partner_id, 0))
            output_synapses = int(output_counts.get(partner_id, 0))

            # Try to fetch metadata if table is known
            if meta_table:
                try:
                    meta_df = client.materialize.query_table(
                        table=meta_table,
                        filter_equal_dict={"root_id": partner_id},
                        limit=1,
                    )
                    if meta_df is not None and not meta_df.empty:
                        info = meta_df.iloc[0]
                        def get_val(k: str) -> str:
                            return info[k] if (k in info and pd.notna(info[k])) else ""
                        nt_type = get_val("top_nt")
                        flow = get_val("flow")
                        super_class = get_val("super_class")
                        cell_class = get_val("cell_class")
                        sub_class = get_val("cell_sub_class")
                        # prefer hemibrain_type, then cell_type
                        hb = get_val("hemibrain_type")
                        ct = get_val("cell_type")
                        cell_type = hb if hb else ct
                        hemilineage = get_val("ito_lee_hemilineage")
                        nerve = get_val("nerve")
                        side = get_val("side")
                except Exception:
                    pass

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

        df = pd.DataFrame(csv_rows)
        
        # Sort by synapse count (Syn column) in descending order (most synapses first)
        if "Syn" in df.columns:
            df = df.sort_values(by="Syn", ascending=False).reset_index(drop=True)
            print(f"   Sorted {len(df)} neurons by synapse count (most to least)")
        
        if output_file is None:
            output_file = f"{direction}_neurons_comprehensivecaveclient_{root_id}.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Saved {len(df)} {direction} neurons to {output_file}")

        # Brief summary
        print(f"\n{direction.capitalize()} neuron summary:")
        print(f"   - Total neurons: {len(df)}")
        print(f"   - With cell type info: {len(df[df['cell_type'] != ''])}")
        print(f"   - Left hemisphere: {len(df[df['side'] == 'left'])}")
        print(f"   - Right hemisphere: {len(df[df['side'] == 'right'])}")

        return output_file

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def get_comprehensive_partners_csv_caveclient_example_format(root_id, output_file: Optional[str] = None, stream: str = "", datastack: str = "flywire_fafb_public"):
    """
    Comprehensive partners CSV using CAVECLIENT that matches the example CSV format exactly.
    Excludes label, name, and connectivity_tag columns but matches all other formatting.

    Args:
        root_id (str|int): The root ID to get neurons for.
        output_file (str, optional): Output CSV filename.
        stream (str): "upstream" or "downstream" (default upstream).
        datastack (str): CAVE datastack name. Defaults to "flywire_fafb_public".
    """
    if CAVEclient is None:
        print("❌ Error: caveclient not installed/available")
        return None

    try:
        is_downstream = stream.strip().lower() == "downstream"
        direction = "downstream" if is_downstream else "upstream"

        client = CAVEclient(datastack)

        # Ensure synapse table is defined
        ds_info = client.info.get_datastack_info()
        default_syn_table = ds_info.get("synapse_table")
        if not default_syn_table:
            try:
                tables = client.materialize.get_tables()
            except Exception:
                tables = []
            syn_candidates = [t for t in tables if "synapse" in t or "synapses" in t]
            synapse_table = syn_candidates[0] if syn_candidates else None
        else:
            synapse_table = default_syn_table

        if not synapse_table:
            print("❌ Error: Could not determine synapse table for this datastack.")
            return None

        print(f"Fetching comprehensive {direction} neuron data for root ID: {root_id} (table={synapse_table})...")

        root_id = int(root_id)

        # Query synapses for connectivity
        if is_downstream:
            syn_df = client.materialize.synapse_query(
                pre_ids=root_id,
                remove_autapses=True,
                synapse_table=synapse_table,
                split_positions=False,
            )
            partner_col = "post_pt_root_id" if "post_pt_root_id" in syn_df.columns else "post_root_id"
        else:
            syn_df = client.materialize.synapse_query(
                post_ids=root_id,
                remove_autapses=True,
                synapse_table=synapse_table,
                split_positions=False,
            )
            partner_col = "pre_pt_root_id" if "pre_pt_root_id" in syn_df.columns else "pre_root_id"

        if syn_df is None or syn_df.empty:
            print("No connectivity data found for this root ID")
            return None

        if partner_col not in syn_df.columns:
            print(f"❌ Error: Expected partner column not found in synapse table (missing {partner_col}).")
            return None

        # Get partners sorted by synapse count (highest to lowest)
        counts_series = syn_df.groupby(partner_col).size()
        # Filter out root_id and 0, then sort by synapse count descending
        valid_partners = [(int(pid), count) for pid, count in counts_series.items() 
                         if int(pid) != 0 and int(pid) != root_id]
        valid_partners.sort(key=lambda x: x[1], reverse=True)  # Sort by count, highest first
        partners: List[int] = [pid for pid, count in valid_partners]
        
        # Create synapse lookup
        synapse_lookup: Dict[int, int] = {pid: count for pid, count in valid_partners}

        print(f"Found {len(partners)} {direction} neurons (sorted by synapse count)")

        # We only need the pairwise synapse counts (root_id <-> partner)
        # No need to fetch total input/output synapses for partners

        print("Fetching annotation metadata for partners...")
        
        # Try to find the right annotation table
        try:
            tables = client.materialize.get_tables()
        except Exception:
            tables = []

        preferred_tables = [
            "flywire_neuron_information",
            "neuron_information", 
            "flywire_neurons",
            "cell_metadata",
        ]
        meta_table = next((t for t in preferred_tables if t in tables), None)

        # Build CSV rows matching example format exactly
        csv_rows = []
        for i, partner_id in enumerate(partners):
            if i % 25 == 0:
                print(f"  Progress: {i}/{len(partners)} neurons processed...")

            syn_count = int(synapse_lookup.get(partner_id, 0))

            # Initialize with empty strings to match example format
            nt_type = ""; flow = ""; super_class = ""; cell_class = ""; sub_class = ""
            cell_type = ""; hemilineage = ""; nerve = ""; side = ""
            # We only care about pairwise synapses, not total input/output
            input_synapses = 0
            output_synapses = 0

            # Try to fetch metadata
            if meta_table:
                try:
                    meta_df = client.materialize.query_table(
                        table=meta_table,
                        filter_equal_dict={"root_id": partner_id},
                        limit=1,
                    )
                    if meta_df is not None and not meta_df.empty:
                        info = meta_df.iloc[0]
                        
                        # Map fields to match example format
                        def get_val(k: str, default: str = "") -> str:
                            val = info.get(k, default) if k in info else default
                            return str(val) if pd.notna(val) else default
                        
                        # Map neurotransmitter type (convert to lowercase to match example)
                        nt_val = get_val("top_nt")
                        if nt_val:
                            nt_type = nt_val.lower()
                        
                        # Map flow
                        flow = get_val("flow")
                        
                        # Map super_class
                        super_class = get_val("super_class")
                        
                        # Map class (cell_class -> class)
                        cell_class = get_val("cell_class")
                        
                        # Map sub_class (cell_sub_class -> sub_class)
                        sub_class = get_val("cell_sub_class")
                        
                        # Map cell_type (prefer hemibrain_type, then cell_type)
                        hb_type = get_val("hemibrain_type")
                        ct_type = get_val("cell_type")
                        if hb_type:
                            cell_type = hb_type
                        elif ct_type:
                            cell_type = ct_type
                        
                        # Map hemilineage
                        hemilineage = get_val("ito_lee_hemilineage")
                        
                        # Map nerve
                        nerve = get_val("nerve")
                        
                        # Map side
                        side = get_val("side")
                        
                except Exception:
                    pass

            # Create row matching example format exactly (without label, name, connectivity_tag)
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

        df = pd.DataFrame(csv_rows)
        if output_file is None:
            output_file = f"{direction}_neurons_comprehensivecaveclient_{root_id}.csv"
        df.to_csv(output_file, index=False)
        print(f"✅ Saved {len(df)} {direction} neurons to {output_file}")

        # Summary
        print(f"\n{direction.capitalize()} neuron summary:")
        print(f"   - Total neurons: {len(df)}")
        print(f"   - With cell type info: {len(df[df['cell_type'] != ''])}")
        print(f"   - Left hemisphere: {len(df[df['side'] == 'left'])}")
        print(f"   - Right hemisphere: {len(df[df['side'] == 'right'])}")

        return output_file

    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_partners_data(root_id, stream: str = "", datastack: str = "flywire_fafb_public", top_n: int = 10):
    """
    Tester function to verify partner neuron data and synapse counts.
    Tests ALL available synapse tables and views, showing data from each.
    
    Args:
        root_id (str|int): The root ID to get neurons for.
        stream (str): "upstream" or "downstream" (default upstream).
        datastack (str): CAVE datastack name. Defaults to "flywire_fafb_public".
        top_n (int): Number of top partners to display. Defaults to 10.
    
    Returns:
        Dictionary with results from all tested tables/views
    """
    if CAVEclient is None:
        print("❌ Error: caveclient not installed/available")
        return None

    try:
        is_downstream = stream.strip().lower() == "downstream"
        direction = "downstream" if is_downstream else "upstream"
        root_id = int(root_id)

        # Initialize client (will use most recent version by default)
        client = CAVEclient(datastack)
        
        # Get the most recent version for display
        try:
            materialization_version = client.materialize.most_recent_version()
            print(f"✅ Using materialization version: {materialization_version}")
        except Exception as e:
            print(f"⚠️  Warning: Could not determine most recent version: {e}")
            materialization_version = None

        version_str = f"version={materialization_version}" if materialization_version else "latest version"
        print(f"\n📊 Testing {direction} neuron data for root ID: {root_id} ({version_str})...")
        print("="*80)

        # Get all available tables and views
        print("\n🔍 Discovering available tables and views...")
        try:
            all_tables = client.materialize.get_tables()
            synapse_tables = [t for t in all_tables if "synapse" in t.lower()]
            print(f"   Found {len(all_tables)} total tables")
            print(f"   Found {len(synapse_tables)} synapse-related tables")
            
            all_views = client.materialize.get_views()
            synapse_views = [v for v in all_views if "synapse" in v.lower()]
            print(f"   Found {len(all_views)} total views")
            print(f"   Found {len(synapse_views)} synapse-related views")
            
            print(f"\n   Synapse tables: {synapse_tables}")
            print(f"   Synapse views: {synapse_views}")
            
        except Exception as e:
            print(f"⚠️  Warning: Could not check tables/views: {e}")
            synapse_tables = []
            synapse_views = []
            return None

        # Results storage
        results = {}
        
        # Test all tables
        print("\n" + "="*80)
        print("📋 TESTING ALL SYNAPSE TABLES")
        print("="*80)
        
        for i, table_name in enumerate(synapse_tables, 1):
            print(f"\n{'─'*80}")
            print(f"TABLE {i}/{len(synapse_tables)}: {table_name}")
            print(f"{'─'*80}")
            
            try:
                # Try to query using synapse_query
                if is_downstream:
                    syn_df = client.materialize.synapse_query(
                        pre_ids=root_id,
                        remove_autapses=True,
                        synapse_table=table_name,
                        split_positions=False,
                    )
                    partner_col = "post_pt_root_id" if "post_pt_root_id" in syn_df.columns else "post_root_id"
                else:
                    syn_df = client.materialize.synapse_query(
                        post_ids=root_id,
                        remove_autapses=True,
                        synapse_table=table_name,
                        split_positions=False,
                    )
                    partner_col = "pre_pt_root_id" if "pre_pt_root_id" in syn_df.columns else "pre_root_id"
                
                if syn_df is not None and not syn_df.empty:
                    # Get partner data
                    partners_data = syn_df.groupby(partner_col).size().reset_index(name='synapse_count')
                    partners_data = partners_data[
                        (partners_data[partner_col] != 0) & 
                        (partners_data[partner_col] != root_id)
                    ].copy()
                    
                    partners_data = partners_data.sort_values('synapse_count', ascending=False)
                    partners_data.columns = ['partner_id', 'synapse_count']
                    
                    print(f"   ✅ Success! Retrieved {len(syn_df)} synapses")
                    print(f"   📊 Columns: {list(syn_df.columns)}")
                    print(f"   🔗 Found {len(partners_data)} unique partners")
                    print(f"   📈 Total synapses: {partners_data['synapse_count'].sum():,}")
                    print(f"   📊 Top {min(top_n, len(partners_data))} partners:")
                    
                    for idx, row in partners_data.head(top_n).iterrows():
                        print(f"      {row['partner_id']:>20} | {row['synapse_count']:>6} synapses")
                    
                    # Show sample data
                    print(f"   📄 Sample data (first 3 rows):")
                    print(syn_df.head(3).to_string())
                    
                    results[table_name] = {
                        "type": "table",
                        "success": True,
                        "columns": list(syn_df.columns),
                        "num_synapses": len(syn_df),
                        "num_partners": len(partners_data),
                        "total_synapses": partners_data['synapse_count'].sum(),
                        "top_partners": partners_data.head(top_n).to_dict('records'),
                        "sample_data": syn_df.head(3).to_dict('records')
                    }
                else:
                    print(f"   ⚠️  No data returned (empty result)")
                    results[table_name] = {"type": "table", "success": False, "error": "Empty result"}
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:200]}")  # Truncate long errors
                results[table_name] = {"type": "table", "success": False, "error": str(e)[:200]}

        # Test all views
        print("\n\n" + "="*80)
        print("👁️  TESTING ALL SYNAPSE VIEWS")
        print("="*80)
        
        for i, view_name in enumerate(synapse_views, 1):
            print(f"\n{'─'*80}")
            print(f"VIEW {i}/{len(synapse_views)}: {view_name}")
            print(f"{'─'*80}")
            
            try:
                # Try to query using query_view
                if is_downstream:
                    # Try different column name variations
                    for col_name in ["pre_pt_root_id", "pre_root_id", "pre"]:
                        try:
                            syn_df = client.materialize.query_view(
                                view_name=view_name,
                                filter_equal_dict={col_name: root_id},
                                split_positions=False,
                                limit=10000,  # Limit to avoid huge results
                            )
                            if syn_df is not None and not syn_df.empty:
                                # Determine partner column
                                partner_col = "post_pt_root_id" if "post_pt_root_id" in syn_df.columns else \
                                            "post_root_id" if "post_root_id" in syn_df.columns else \
                                            "post" if "post" in syn_df.columns else None
                                break
                        except Exception:
                            continue
                else:
                    # Try different column name variations
                    for col_name in ["post_pt_root_id", "post_root_id", "post"]:
                        try:
                            syn_df = client.materialize.query_view(
                                view_name=view_name,
                                filter_equal_dict={col_name: root_id},
                                split_positions=False,
                                limit=10000,
                            )
                            if syn_df is not None and not syn_df.empty:
                                # Determine partner column
                                partner_col = "pre_pt_root_id" if "pre_pt_root_id" in syn_df.columns else \
                                            "pre_root_id" if "pre_root_id" in syn_df.columns else \
                                            "pre" if "pre" in syn_df.columns else None
                                break
                        except Exception:
                            continue
                
                if syn_df is not None and not syn_df.empty and partner_col:
                    # Get partner data
                    partners_data = syn_df.groupby(partner_col).size().reset_index(name='synapse_count')
                    partners_data = partners_data[
                        (partners_data[partner_col] != 0) & 
                        (partners_data[partner_col] != root_id)
                    ].copy()
                    
                    partners_data = partners_data.sort_values('synapse_count', ascending=False)
                    partners_data.columns = ['partner_id', 'synapse_count']
                    
                    print(f"   ✅ Success! Retrieved {len(syn_df)} synapses")
                    print(f"   📊 Columns: {list(syn_df.columns)}")
                    print(f"   🔗 Found {len(partners_data)} unique partners")
                    print(f"   📈 Total synapses: {partners_data['synapse_count'].sum():,}")
                    print(f"   📊 Top {min(top_n, len(partners_data))} partners:")
                    
                    for idx, row in partners_data.head(top_n).iterrows():
                        print(f"      {row['partner_id']:>20} | {row['synapse_count']:>6} synapses")
                    
                    # Show sample data
                    print(f"   📄 Sample data (first 3 rows):")
                    print(syn_df.head(3).to_string())
                    
                    results[view_name] = {
                        "type": "view",
                        "success": True,
                        "columns": list(syn_df.columns),
                        "num_synapses": len(syn_df),
                        "num_partners": len(partners_data),
                        "total_synapses": partners_data['synapse_count'].sum(),
                        "top_partners": partners_data.head(top_n).to_dict('records'),
                        "sample_data": syn_df.head(3).to_dict('records')
                    }
                else:
                    print(f"   ⚠️  Could not query or no data returned")
                    if syn_df is None or syn_df.empty:
                        error_msg = "Empty result"
                    else:
                        error_msg = f"Partner column not found. Available: {list(syn_df.columns) if syn_df is not None else 'N/A'}"
                    results[view_name] = {"type": "view", "success": False, "error": error_msg}
                    
            except Exception as e:
                print(f"   ❌ Error: {str(e)[:200]}")
                results[view_name] = {"type": "view", "success": False, "error": str(e)[:200]}

        # Summary
        print("\n\n" + "="*80)
        print("📊 SUMMARY OF ALL TESTS")
        print("="*80)
        
        successful_tables = [name for name, res in results.items() if res.get("success") and res.get("type") == "table"]
        successful_views = [name for name, res in results.items() if res.get("success") and res.get("type") == "view"]
        
        print(f"\n✅ Successful tables ({len(successful_tables)}):")
        for name in successful_tables:
            res = results[name]
            print(f"   - {name}")
            print(f"     Partners: {res.get('num_partners', 0)}, Synapses: {res.get('num_synapses', 0):,}")
        
        print(f"\n✅ Successful views ({len(successful_views)}):")
        for name in successful_views:
            res = results[name]
            print(f"   - {name}")
            print(f"     Partners: {res.get('num_partners', 0)}, Synapses: {res.get('num_synapses', 0):,}")
        
        failed = [name for name, res in results.items() if not res.get("success")]
        if failed:
            print(f"\n❌ Failed ({len(failed)}):")
            for name in failed:
                print(f"   - {name}: {results[name].get('error', 'Unknown error')}")
        
        print("\n" + "="*80)
        print("✅ Testing completed!")
        print("="*80)
        
        return results

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return None

# Example usage
if __name__ == "__main__":
    print("Upstream/Downstream Neurons CSV Generator")
    print("=" * 40)
    
    # First choice: Test mode or full analysis
    print("\nChoose mode:")
    print("1. Test mode (quick verification - shows top partners with synapse counts)")
    print("2. Full analysis (generate comprehensive CSV file)")
    
    mode_choice = input("Enter choice (1 or 2): ").strip()
    
    if mode_choice not in ["1", "2"]:
        print("Invalid choice. Please enter 1 or 2.")
        exit()
    
    # Get root ID from user
    root_id = input("\nEnter the root ID: ").strip()
    
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
    
    if mode_choice == "1":
        # TEST MODE
        print("\n" + "="*80)
        print("🧪 TEST MODE - Quick Data Verification")
        print("="*80)
        
        top_n_input = input("\nHow many top partners to display? (default: 10): ").strip()
        try:
            top_n = int(top_n_input) if top_n_input else 10
        except ValueError:
            top_n = 10
            print(f"   Invalid input, using default: {top_n}")
        
        result = test_partners_data(root_id, stream=stream, top_n=top_n)
        
        if result is not None:
            print("\n✅ Test completed successfully!")
        else:
            print("\n❌ Test failed")
    else:
        # FULL ANALYSIS MODE
        print("\n" + "="*80)
        print("📊 FULL ANALYSIS MODE - Generating Comprehensive CSV")
        print("="*80)
        
        # Get mode choice
        print("\nChoose processing mode:")
        print("1. Simple mode (just partner neuron IDs) - Fast")
        print("2. Detailed mode (with cell types) - Slower")
        print("3. Comprehensive mode (matching example CSV format) - Slowest")
        print("4. CAVECLIENT comprehensive mode (no FAFBseg) - Slowest")
        
        choice = input("Enter choice (1, 2, 3, or 4): ").strip()
        
        if choice == "4":
            result = get_comprehensive_partners_csv_caveclient(root_id, stream=stream)
        elif choice == "3":
            result = get_comprehensive_partners_csv(root_id, stream=stream)
        elif choice == "2":
            result = get_upstream_with_types_csv(root_id, stream=stream)
        else:
            result = get_upstream_neurons_csv(root_id, stream=stream)
        
        if result:
            print(f"\n🎉 Success! Check the file: {result}")
        else:
            print("\n💥 Failed to create CSV file")








#720575940621777391

