#!/usr/bin/env python3
"""
Test script for the updated csv_helper.py functionality
"""

from csv_helper import create_neuron_partner_csv

def test_csv_generation():
    """
    Test the CSV generation functionality with different neuron types
    """
    print("Testing CSV Helper Functionality")
    print("=" * 50)
    
    # Test with different neuron types
    test_types = ["PN", "DNp32", "SLP131"]
    
    for neuron_type in test_types:
        print(f"\nTesting with neuron type: {neuron_type}")
        print("-" * 30)
        
        try:
            result = create_neuron_partner_csv(neuron_type)
            if result:
                print(f"✓ Successfully created: {result}")
            else:
                print(f"✗ Failed to create CSV for {neuron_type}")
        except Exception as e:
            print(f"✗ Error testing {neuron_type}: {e}")

if __name__ == "__main__":
    test_csv_generation()
