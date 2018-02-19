Login-AzureRmAccount
Set-AzureRmContext -SubscriptionName "AEG DS Laboratory"
$appname = "mywebapp$(Get-Random)"
$sitename = "lawebdemo696961313"
$location = "southcentralus"
$rgName = "lawebapprg1"
$sub = "AEG DS Laboratory"
$gitRepo = "https://github.com/Azure-Samples/app-service-web-dotnet-get-started.git"
New-AzureRmResourceGroup -Name $rgName -Location $location
New-AzureRmAppServicePlan -Name $appname -Location $location -ResourceGroupName $rgName -Tier Standard
New-AzureRmWebApp -Name $appname -Location $location -AppServicePlan $appname -ResourceGroupName $rgName
New-AzureRmWebAppSlot -Name $appname -ResourceGroupName $rgName -Slot staging
$PropertiesObject = @{ "RepoUrl" = "$gitrepo"; "Branch" = "master"; "IsManualIntegration" = "true"; }
Set-AzureRmResource -Properties $propertiesObject -ResourceGroupName "lawebapprg1" -ResourceType "Microsoft.web/sites/slots/sourcecontrols" -ResourceName "$appname/staging/web" -ApiVersion 2015-08-01 -Force
