#!/usr/bin/env python3
"""
Version Control Script for CAVE Materialization Versions

This script queries and displays all available materialization versions
for a given datastack, including their metadata, tables, and views.

Based on CAVEclient API documentation:
https://www.caveconnecto.me/CAVEclient/api/materialize/
"""

from caveclient import CAVEclient
import pandas as pd
from typing import Optional, List, Dict
from datetime import datetime


def get_all_versions_info(datastack: str = "flywire_fafb_public", include_expired: bool = True):
    """
    Get comprehensive information about all available materialization versions.
    
    Args:
        datastack: Name of the datastack to query
        include_expired: Whether to include expired versions
    
    Returns:
        Dictionary containing version information
    """
    print(f"🔍 Connecting to datastack: {datastack}")
    client = CAVEclient(datastack)
    
    # Get all available versions
    print("\n📋 Fetching available versions...")
    versions = client.materialize.get_versions(expired=include_expired)
    print(f"   Found {len(versions)} version(s)")
    
    # Get most recent version
    try:
        most_recent = client.materialize.most_recent_version()
        print(f"   Most recent version: {most_recent}")
    except Exception as e:
        print(f"   ⚠️  Could not determine most recent version: {e}")
        most_recent = None
    
    # Get metadata for all versions
    print("\n📊 Fetching metadata for all versions...")
    try:
        versions_metadata = client.materialize.get_versions_metadata(expired=include_expired)
        print(f"   Retrieved metadata for {len(versions_metadata)} version(s)")
    except Exception as e:
        print(f"   ⚠️  Error fetching versions metadata: {e}")
        versions_metadata = []
    
    return {
        "client": client,
        "versions": versions,
        "most_recent": most_recent,
        "versions_metadata": versions_metadata,
        "datastack": datastack
    }


def get_version_details(client: CAVEclient, version: int, datastack: str):
    """
    Get detailed information about a specific version.
    
    Args:
        client: CAVEclient instance
        version: Version number to query
        datastack: Datastack name
    
    Returns:
        Dictionary with version details
    """
    details = {
        "version": version,
        "metadata": None,
        "tables": [],
        "views": [],
        "timestamp": None,
        "error": None
    }
    
    try:
        # Get version metadata
        details["metadata"] = client.materialize.get_version_metadata(version=version)
        details["timestamp"] = client.materialize.get_timestamp(version=version)
        
        # Get tables for this version
        try:
            details["tables"] = client.materialize.get_tables(version=version)
        except Exception as e:
            details["error"] = f"Error getting tables: {e}"
        
        # Get views for this version
        try:
            details["views"] = client.materialize.get_views(version=version)
        except Exception as e:
            if details["error"]:
                details["error"] += f"; Error getting views: {e}"
            else:
                details["error"] = f"Error getting views: {e}"
                
    except Exception as e:
        details["error"] = str(e)
    
    return details


def display_versions_summary(info: Dict):
    """
    Display a summary of all available versions.
    
    Args:
        info: Dictionary returned from get_all_versions_info()
    """
    print("\n" + "="*80)
    print(f"MATERIALIZATION VERSIONS SUMMARY - {info['datastack']}")
    print("="*80)
    
    versions = sorted(info['versions'])
    most_recent = info['most_recent']
    
    print(f"\n📌 Total versions available: {len(versions)}")
    if most_recent:
        print(f"📌 Most recent version: {most_recent}")
    print(f"📌 Version range: {min(versions)} - {max(versions)}")
    
    # Display versions list
    print(f"\n📋 Available versions:")
    for i, v in enumerate(versions, 1):
        marker = " ⭐ (most recent)" if v == most_recent else ""
        print(f"   {i}. Version {v}{marker}")
    
    return versions


def display_version_metadata(info: Dict, versions_to_show: Optional[List[int]] = None):
    """
    Display detailed metadata for versions.
    
    Args:
        info: Dictionary returned from get_all_versions_info()
        versions_to_show: List of specific versions to show. If None, shows all.
    """
    print("\n" + "="*80)
    print("VERSION METADATA DETAILS")
    print("="*80)
    
    versions = sorted(info['versions'])
    if versions_to_show:
        versions = [v for v in versions if v in versions_to_show]
    
    metadata_list = info['versions_metadata']
    
    # Create a DataFrame for easier viewing
    if metadata_list:
        df = pd.DataFrame(metadata_list)
        if 'version' in df.columns:
            df = df.sort_values('version', ascending=False)
            print("\n📊 Version Metadata Table:")
            print(df.to_string(index=False))
        else:
            print("\n📊 Version Metadata (raw):")
            for meta in metadata_list:
                print(f"\n   {meta}")
    else:
        print("\n⚠️  No metadata available")
    
    # Display individual version details
    print("\n" + "="*80)
    print("DETAILED VERSION INFORMATION")
    print("="*80)
    
    for version in versions:
        print(f"\n{'─'*80}")
        print(f"VERSION {version}")
        print(f"{'─'*80}")
        
        details = get_version_details(info['client'], version, info['datastack'])
        
        if details['error']:
            print(f"   ❌ Error: {details['error']}")
            continue
        
        # Display metadata
        if details['metadata']:
            print(f"\n   📋 Metadata:")
            for key, value in details['metadata'].items():
                if isinstance(value, datetime):
                    print(f"      {key}: {value.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"      {key}: {value}")
        
        # Display timestamp
        if details['timestamp']:
            print(f"\n   🕐 Timestamp: {details['timestamp']}")
        
        # Display tables
        if details['tables']:
            print(f"\n   📊 Tables ({len(details['tables'])}):")
            for table in sorted(details['tables']):
                print(f"      - {table}")
        else:
            print(f"\n   📊 Tables: None found")
        
        # Display views
        if details['views']:
            print(f"\n   👁️  Views ({len(details['views'])}):")
            for view in sorted(details['views']):
                print(f"      - {view}")
        else:
            print(f"\n   👁️  Views: None found")


def check_specific_version(datastack: str, version: int):
    """
    Check if a specific version exists and is accessible.
    
    Args:
        datastack: Datastack name
        version: Version number to check
    
    Returns:
        Boolean indicating if version is available
    """
    try:
        client = CAVEclient(datastack)
        versions = client.materialize.get_versions(expired=True)
        
        if version in versions:
            print(f"✅ Version {version} is available for datastack '{datastack}'")
            details = get_version_details(client, version, datastack)
            if details['tables']:
                print(f"   Tables available: {len(details['tables'])}")
            if details['views']:
                print(f"   Views available: {len(details['views'])}")
            return True
        else:
            print(f"❌ Version {version} is NOT available for datastack '{datastack}'")
            print(f"   Available versions: {sorted(versions)}")
            return False
    except Exception as e:
        print(f"❌ Error checking version {version}: {e}")
        return False


def export_versions_to_csv(info: Dict, filename: str = "materialization_versions.csv"):
    """
    Export version information to a CSV file.
    
    Args:
        info: Dictionary returned from get_all_versions_info()
        filename: Output CSV filename
    """
    try:
        metadata_list = info['versions_metadata']
        if metadata_list:
            df = pd.DataFrame(metadata_list)
            if 'version' in df.columns:
                df = df.sort_values('version', ascending=False)
            df.to_csv(filename, index=False)
            print(f"\n💾 Exported version metadata to: {filename}")
        else:
            print("\n⚠️  No metadata to export")
    except Exception as e:
        print(f"\n❌ Error exporting to CSV: {e}")


def main():
    """
    Main function to run the version control script.
    """
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Query and display CAVE materialization version information",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Show all versions for default datastack
  python versioncontrol.py
  
  # Check specific version
  python versioncontrol.py --check-version 3
  
  # Show versions for different datastack
  python versioncontrol.py --datastack my_datastack
  
  # Export to CSV
  python versioncontrol.py --export versions.csv
        """
    )
    
    parser.add_argument(
        "--datastack",
        type=str,
        default="flywire_fafb_public",
        help="Datastack name (default: flywire_fafb_public)"
    )
    
    parser.add_argument(
        "--include-expired",
        action="store_true",
        help="Include expired versions in the results"
    )
    
    parser.add_argument(
        "--check-version",
        type=int,
        help="Check if a specific version exists"
    )
    
    parser.add_argument(
        "--export",
        type=str,
        help="Export version metadata to CSV file"
    )
    
    parser.add_argument(
        "--detailed",
        action="store_true",
        help="Show detailed information for each version (tables, views)"
    )
    
    args = parser.parse_args()
    
    # Check specific version if requested
    if args.check_version:
        check_specific_version(args.datastack, args.check_version)
        return
    
    # Get all version information
    info = get_all_versions_info(
        datastack=args.datastack,
        include_expired=args.include_expired
    )
    
    # Display summary
    versions = display_versions_summary(info)
    
    # Display detailed information if requested
    if args.detailed:
        display_version_metadata(info)
    else:
        # Show metadata summary
        display_version_metadata(info, versions_to_show=versions[:10])  # Show first 10 by default
        if len(versions) > 10:
            print(f"\n💡 Tip: Use --detailed flag to see all {len(versions)} versions with full details")
    
    # Export if requested
    if args.export:
        export_versions_to_csv(info, args.export)
    
    print("\n" + "="*80)
    print("✅ Version control query complete!")
    print("="*80)


if __name__ == "__main__":
    main()

