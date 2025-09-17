#!/usr/bin/env python3
"""
Simple CSV Helper - Creates neuron-partner CSV files from existing CSV data
This version works without heavy scientific computing libraries
"""

import pandas as pd
import json
import os
import sys

def create_neuron_partner_csv_from_existing(neuron_type, input_csv_path=None, output_filename=None):
    """
    Create a CSV file with neurons of specified type and their partner neurons
    from existing CSV files.
    
    Args:
        neuron_type (str): The type of neurons to filter for
        input_csv_path (str, optional): Path to input CSV. If None, searches for CSV files
        output_filename (str, optional): Output filename. If None, uses f"{neuron_type}_partners.csv"
    
    Returns:
        str: The filename of the created CSV
    """
    try:
        # Find input CSV file if not provided
        if input_csv_path is None:
            csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
            if not csv_files:
                print("No CSV files found in current directory")
                return None
            
            # Use the first CSV file found
            input_csv_path = csv_files[0]
            print(f"Using input file: {input_csv_path}")
        
        # Read the CSV file
        print(f"Reading CSV file: {input_csv_path}")
        df = pd.read_csv(input_csv_path)
        
        if df.empty:
            print("CSV file is empty")
            return None
        
        print(f"Found {len(df)} total rows in CSV")
        
        # Filter for the specified neuron type
        if 'type' in df.columns:
            filtered_df = df[df['type'] == neuron_type]
        else:
            print("No 'type' column found in CSV")
            return None
        
        if filtered_df.empty:
            print(f"No neurons found of type: {neuron_type}")
            print(f"Available types: {df['type'].unique() if 'type' in df.columns else 'N/A'}")
            return None
        
        print(f"Found {len(filtered_df)} neurons of type {neuron_type}")
        
        # Create the partner neurons data
        partner_data = []
        
        for _, row in filtered_df.iterrows():
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
    """
    Main function to get user input and create CSV files
    """
    print("Simple Neuron Partner CSV Generator")
    print("=" * 40)
    
    # List available CSV files
    csv_files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if not csv_files:
        print("No CSV files found in current directory")
        return
    
    print(f"Available CSV files: {', '.join(csv_files)}")
    
    # Get input CSV file from user
    input_csv = input(f"Enter CSV filename (press Enter for '{csv_files[0]}'): ").strip()
    if not input_csv:
        input_csv = csv_files[0]
    
    if not os.path.exists(input_csv):
        print(f"File {input_csv} not found")
        return
    
    # Get neuron type from user
    neuron_type = input("Enter the neuron type (e.g., DNp32, SLP131, LHAD1g1): ").strip()
    
    if not neuron_type:
        print("No neuron type provided. Exiting.")
        return
    
    # Get optional output filename
    output_filename = input(f"Enter output filename (press Enter for '{neuron_type}_partners.csv'): ").strip()
    if not output_filename:
        output_filename = None
    
    # Create the CSV
    result = create_neuron_partner_csv_from_existing(neuron_type, input_csv, output_filename)
    
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
