#This script will look for NSG's that have port 443 open from the internet

import sys
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient

def check_nsgs_for_port_443_internet():
    """
    Checks all NSGs in the specified subscription for inbound rules 
    allowing port 443 access from the internet.
    """
    
    # --- ⚠️ REQUIRED: Specify your Azure Subscription ID here ⚠️ ---
    # Replace this placeholder with the actual ID of the subscription you want to audit.
    subscription_id = "cfdfe037-8667-4558-a4bb-20c6294c7378"
    
    if subscription_id == "YOUR_AZURE_SUBSCRIPTION_ID_HERE":
        print("Error: Please replace 'YOUR_AZURE_SUBSCRIPTION_ID_HERE' with your actual Azure Subscription ID in the script.")
        sys.exit(1)
    # ------------------------------------------------------------------

    # --- Configuration for the Audit ---
    TARGET_PORT = "443"
    INTERNET_SOURCES = ["*", "Internet", "0.0.0.0/0"]
    INBOUND_DIRECTION = "Inbound"
    ALLOW_ACCESS = "Allow"

    # Authenticate using the currently logged-in Azure CLI/PowerShell user
    try:
        credential = DefaultAzureCredential()
    except Exception as e:
        print("Error acquiring Azure credentials. Ensure you are logged in via 'az login' or have environment variables set.")
        print(f"Details: {e}")
        sys.exit(1)

    # Initialize the Network Management Client
    network_client = NetworkManagementClient(
        credential=credential,
        subscription_id=subscription_id
    )

    print(f"--- Azure NSG Audit for Inbound Port {TARGET_PORT} from Internet (Subscription ID: {subscription_id}) ---")
    print("-" * 80)
    
    found_vulnerabilities = False
    
    # List all NSGs in the subscription
    # The list_all() method is used to retrieve NSGs across all resource groups in the subscription.
    for nsg in network_client.network_security_groups.list_all():
        # Safely extract the resource group name from the NSG's ID
        resource_group_name = nsg.id.split('/resourceGroups/')[1].split('/')[0]
        
        # Check each security rule in the NSG
        for rule in nsg.security_rules:
            
            # 1. Check for: Direction is Inbound and Access is Allow
            if rule.direction == INBOUND_DIRECTION and rule.access == ALLOW_ACCESS:
                
                # 2. Check for: Source is the Internet (e.g., *, Internet, 0.0.0.0/0)
                is_internet_source = (
                    rule.source_address_prefix in INTERNET_SOURCES or
                    (rule.source_address_prefixes and any(p in INTERNET_SOURCES for p in rule.source_address_prefixes))
                )
                
                # 3. Check for: Destination port includes 443
                port_range_match = False
                
                # Check single port range property
                if rule.destination_port_range and (rule.destination_port_range == TARGET_PORT or rule.destination_port_range == "*"):
                    port_range_match = True
                
                # Check multiple port ranges property
                if rule.destination_port_ranges:
                    for port_range in rule.destination_port_ranges:
                        # Checks for exact match "443" or wildcard "*"
                        if TARGET_PORT in port_range or port_range == "*":
                            port_range_match = True
                            break

                if is_internet_source and port_range_match:
                    found_vulnerabilities = True
                    print(f"🚨 FOUND VULNERABILITY:")
                    print(f"  NSG Name: {nsg.name}")
                    print(f"  Resource Group: {resource_group_name}")
                    print(f"  Rule Name: {rule.name}")
                    print(f"  Priority: {rule.priority}")
                    print(f"  Source: {rule.source_address_prefix or rule.source_address_prefixes}")
                    print(f"  Destination Port: {rule.destination_port_range or rule.destination_port_ranges}")
                    print("-" * 80)
                    
    if not found_vulnerabilities:
        print("✅ No NSGs found with inbound 'Allow' rules for port 443 from the general internet.")

if __name__ == "__main__":
    check_nsgs_for_port_443_internet()
