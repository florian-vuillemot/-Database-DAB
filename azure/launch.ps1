$resourceGroupName = $args[0]
$resourceGroupLocation = $args[1]
$databaseType = $args[2]

$vnetName = "vnet"
$vnetTemplateFile = "vnet.json"
$vnetParametersFilename = "vnet.parameters.json"

$vmTemplateFile = "vm.json"


$vms = if ($databaseType.ToUpper()[0] -eq 'P') {
    # PostgreSQL
    @(
        "Sub0pSQL0", "Sub0pSQL1", # Cluster
        "Sub1pSQL0"   # Backup
    )        
} else {
    # MongoDB
    @(
        "Sub0MDB0", "Sub0MDB1",     # Cluster
        "Sub1MDB0"                  # Backup
    )
}

function CreateResourceGroup {
    param (
        [string]$name,
        [string]$location
    )

    $resourceGroupExist = Invoke-Expression "az group exists --name $name"
    $resourceGroupExist = [System.Convert]::ToBoolean($resourceGroupExist)

    if (-Not $resourceGroupExist) {
        Invoke-Expression "az group create --name $name --location $location"
    }    
}

function CreateResource {
    param (
        [string]$name,
        [string]$resourceGroupeName,
        [string]$templateFile,
        [string]$parametersFilename
    )
    
    Invoke-Expression "az group deployment create --name create-$name --resource-group $resourceGroupeName --template-file $templateFile --parameters $parametersFilename"
}

function GetIpsAddress {
    param (
        [string]$ResourceGroupName
    )
    
    $networkResources = Invoke-Expression "az network public-ip list" | ConvertFrom-Json
    $masterIps = @()
    $slaveIps = @()

    foreach ($networkResource in $networkResources) {
        if ($networkResource.resourceGroup -eq $ResourceGroupName) {
            $ip = $networkResource.ipAddress
            
            if ($networkResource.tags.Name -eq "Master") {
                $masterIps += $ip
            }
            else {
                $slaveIps += $ip
            }
        }
    }
    @{
        'masters'=$masterIps;
        'slaves'=$slaveIps
    }
}


CreateResourceGroup -name $resourceGroupName -location $resourceGroupLocation

CreateResource  -name $vnetName `
                -resourceGroupeName $resourceGroupName `
                -templateFile $vnetTemplateFile `
                -parametersFilename $vnetParametersFilename


foreach ($vm in $vms) {
    CreateResource  -name $vm `
                    -resourceGroupeName $resourceGroupName `
                    -templateFile $vmTemplateFile `
                    -parametersFilename "$vm.parameters.json"
}    

$ips = GetIpsAddress -ResourceGroupName $resourceGroupName
Write-Host "IP of masters: $ips.masters"
Write-Host "IP of Slaves: $ips.slaves"
