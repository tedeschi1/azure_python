#Must install prior to running "pip install azure-identity azure-mgmt-network"

import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from typing import List, Dict

# --- Configuration ---
# IMPORTANT: Replace with the Subscription ID you want to report on
SUBSCRIPTION_ID = "cfdfe037-8667-4558-a4bb-20c6294c7378"

def get_vnet_address_space_report(subscription_id: str) -> List[Dict]:
    """
    Retrieves a report of all VNet address spaces in an Azure subscription.
    
    Args:
        subscription_id: The ID of the Azure subscription to query.

    Returns:
        A list of dictionaries, each representing a VNet with its address spaces.
    """
    print("Authenticating to Azure...")
    try:
        # Authenticate using DefaultAzureCredential (supports Azure CLI, VS Code, Environment Variables, etc.)
        credential = DefaultAzureCredential()
    except Exception as e:
        print(f"Error during authentication: {e}")
        print("Please ensure you are logged in via 'az login' or have appropriate environment variables/credentials set.")
        return []

    print(f"Connecting to Network Management Client for Subscription: {subscription_id}")
    network_client = NetworkManagementClient(
        credential=credential,
        subscription_id=subscription_id
    )

    report = []

    try:
        # List all virtual networks in the subscription
        vnet_list = network_client.virtual_networks.list_all()
        
        print("Fetching VNet details...")
        for vnet in vnet_list:
            vnet_data = {
                "Name": vnet.name,
                "Location": vnet.location,
                "AddressPrefixes": []
            }
            
            # Check if addressSpace exists and has prefixes
            if vnet.address_space and vnet.address_space.address_prefixes:
                vnet_data["AddressPrefixes"] = vnet.address_space.address_prefixes
            
            report.append(vnet_data)
            
        return report

    except Exception as e:
        print(f"An error occurred while fetching VNet data: {e}")
        return []

def print_report(report_data: List[Dict]):
    """Prints the VNet address space report in a readable format."""
    
    if not report_data:
        print("\n*** Report is empty. Could not retrieve VNet data. ***")
        return
        
    print("\n--- Azure VNet Address Space Report ---")
    print(f"Total VNets Found: {len(report_data)}")
    print("-" * 40)
    
    for vnet in report_data:
        address_spaces = ", ".join(vnet["AddressPrefixes"]) if vnet["AddressPrefixes"] else "None Defined"
        
        print(f"## {vnet['Name']} ({vnet['Location']})")
        print(f"  - Address Space(s): {address_spaces}")
        # Note: You can also iterate and print subnets if needed (e.g., vnet.subnets)
        print("-" * 40)

# --- Main Execution ---
if __name__ == "__main__":
    if SUBSCRIPTION_ID == "YOUR_AZURE_SUBSCRIPTION_ID":
        print("ERROR: Please update the SUBSCRIPTION_ID variable in the script with your actual Azure Subscription ID.")
    else:
        report = get_vnet_address_space_report(SUBSCRIPTION_ID)
        print_report(report)
