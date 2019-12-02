# Create Azure infrastructure

## Requirement

- Powershell
- Az Cli
- A Azure Subscription

## How to run

Launch `createInfra.ps1` with Powershell and the following argument (replace by what you want):
`pwsh createInfra.ps1 {ResourceGroup} {location} {mongodb|postgresql}`

### Where
- ResourceGroup is the resource group with your resources
- location is the Azure datacenter location
- mongodb|postgresql is the type of database that you want create

**Note:**
- The only think that change between mongdb and postgresql installation it's the naming.
- You have to login you on Azure before

## How it's worl
`createInfra.ps1` is a script that allow you to create the infrastructure on Azure. It's only a orchestrator that take resource template and provide argument.

It's use the template `vm.json` and `vnet.json` template file to generate the Virtual Network and the Virtual Machine Template.

There template need arguments, there are provide in the `*.parameters.json` files. 
