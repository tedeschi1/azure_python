
Install-Module AzureRM -AllowClobber -Force
clear
Add-AzureRmAccount
Set-AzureRmContext -SubscriptionName "AEG DS Laboratory"
$location = "westus"
$vmName = "psLabVM"
$resourceGroup = "labRG"
$securePassword = ConvertTo-SecureString 'Cisco123!' -AsPlainText -Force
$cred = New-Object System.Management.Automation.PSCredential ("pinhead", $securePassword)
$subnetConfig = New-AzureRmVirtualNetworkSubnetConfig -Name pcLabSubnet -AddressPrefix 192.168.0.0/24
New-AzureRmResourceGroup -Name $resourceGroup -Location $location
$vnet = New-AzureRmVirtualNetwork -ResourceGroupName $resourceGroup -Location $location -Name psLabVNet -AddressPrefix 192.168.0.0/16 -Subnet $subnetConfig
$pip = New-AzureRmPublicIpAddress -ResourceGroupName $resourceGroup -Location $location -Name "lapslab$(Get-Random)" -AllocationMethod Dynamic -IdleTimeoutInMinutes 4
$nsgRuleRDP = New-AzureRmNetworkSecurityRuleConfig -Name myNetworkSecurityGroupRuleRDp  -Protocol Tcp -Direction Inbound -Priority 1001 -SourcePortRange * -SourceAddressPrefix * -DestinationAddressPrefix * -DestinationPortRange 3389 -Access Allow
$nsgRuleSSH = New-AzureRmNetworkSecurityRuleConfig -Name myNetworkSecurityGroupRuleSSH  -Protocol Tcp -Direction Inbound -Priority 1000 -SourcePortRange * -SourceAddressPrefix * -DestinationAddressPrefix * -DestinationPortRange 22 -Access Allow
$nsg = New-AzureRmNetworkSecurityGroup -ResourceGroupName $resourceGroup -Location $location -Name psLabNSG -SecurityRules $nsgRuleSSH
$nic = New-AzureRmNetworkInterface -Name psLabNIC -ResourceGroupName $resourceGroup -Location $location -SubnetId $vnet.Subnets[0].Id -PublicIpAddressId $pip.Id -NetworkSecurityGroupId $nsg.Id
$vmConfig = New-AzureRmVMConfig -VMName $vmName -VMSize Standard_DS2 | Set-AzureRmVMOperatingSystem -Windows -ComputerName myVM -Credential $cred | `Set-AzureRmVMSourceImage -PublisherName MicrosoftWindowsServer -Offer WindowsServer -Skus 2016-Datacenter -Version latest | Add-AzureRmVMNetworkInterface -Id $nic.Id
New-AzureRmVM -ResourceGroupName $resourceGroup -Location $location -VM $vmConfig
Web site https://docs.microsoft.com/en-us/azure/virtual-machines/windows/quick-create-powershell?toc=%2Fazure%2Fvirtual-machines%2Fwindows%2Ftoc.json

Get-AzureRmVirtualNetworkGatewayLearnedRoute -VirtualNetworkGatewayName AEG-BI-VNet1GW -ResourceGroupName AEGBIPROD-USWEST-RG

$nsg = Get-AzureRmNetworkSecurityGroup -ResourceGroupName Lab-ResourceGroup -Name TestServer-nsg
Add-AzureRmNetworkSecurityRuleConfig -NetworkSecurityGroup $nsg -Name Allow-Target-Center_443  -Protocol Tcp -Direction Inbound -Priority 1160 -SourcePortRange * -SourceAddressPrefix 10.157.0.0/20 -DestinationAddressPrefix * -DestinationPortRange 443 -Access Allow

This line is to test github