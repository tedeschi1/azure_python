# must run pip install azure-mgmt-network azure-identity netaddr
# use az login to authenticate to your azure subscription

import os
from azure.identity import DefaultAzureCredential
from azure.mgmt.network import NetworkManagementClient
from netaddr import IPSet, IPNetwork

# --- CONFIGURATION ---
# Add your VNet Resource IDs to this list
VNET_IDS = [
    "/subscriptions/xxxxxx-xxxx-xxx-xxxxxx-xxxxxx/resourceGroups/rg-av-vnet-xxxxxxx/providers/Microsoft.Network/virtualNetworks/vnet-xxxxxxxx"
]
SUBNET_NAME = "aviatrix-gateways"
NEW_PREFIX_LENGTH = 28

def find_available_prefix(vnet, prefix_length):
    """Calculates an available CIDR block within the VNet address space."""
    vnet_spaces = IPSet([IPNetwork(space) for space in vnet.address_space.address_prefixes])
    
    # Remove existing subnet spaces from the available VNet pool
    if vnet.subnets:
        for subnet in vnet.subnets:
            vnet_spaces.remove(IPNetwork(subnet.address_prefix))
    
    # Look for the first block that fits the desired prefix length
    for available_range in vnet_spaces.iter_cidrs():
        if available_range.prefixlen <= prefix_length:
            # Sub-divide the available range to get a /28
            new_subnet = list(available_range.subnet(prefix_length))[0]
            return str(new_subnet)
    
    return None

def main():
    # Authenticates using environment variables, CLI, or Managed Identity
    credential = DefaultAzureCredential()
    
    for vnet_id in VNET_IDS:
        # Parse VNet ID components
        parts = vnet_id.split('/')
        sub_id = parts[2]
        rg_name = parts[4]
        vnet_name = parts[8]
        
        network_client = NetworkManagementClient(credential, sub_id)
        
        print(f"Processing VNet: {vnet_name}...")
        
        # 1. Fetch VNet details
        vnet = network_client.virtual_networks.get(rg_name, vnet_name)
        
        # 2. Find a /28 hole in the address space
        new_cidr = find_available_prefix(vnet, NEW_PREFIX_LENGTH)
        
        if not new_cidr:
            print(f"  [!] No available /{NEW_PREFIX_LENGTH} space found in {vnet_name}.")
            continue
            
        print(f"  [+] Found available CIDR: {new_cidr}")
        
        # 3. Create the subnet
        try:
            async_subnet_creation = network_client.subnets.begin_create_or_update(
                rg_name,
                vnet_name,
                SUBNET_NAME,
                {"address_prefix": new_cidr}
            )
            async_subnet_creation.result()
            print(f"  [OK] Subnet '{SUBNET_NAME}' created successfully.")
        except Exception as e:
            print(f"  [ERROR] Failed to create subnet: {e}")

if __name__ == "__main__":
    main()
