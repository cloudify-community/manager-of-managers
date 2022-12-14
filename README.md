# Using Cloudify as a Manager of Managers  (a.k.a  MoM or Spire)

![Using Cloudify as a Manager of Managers](/images/spire.png "Using Cloudify as a Manager of Managers")  
*Using Cloudify as a Manager of Managers*

The Cloudify managers of managers (Spire) feature allows control of several managers (*local managers*) from one manager (*Spire*) via the deploy-on feature.
The deploy-on feature allows users to deploy services on the discovered environments.
The deploy-on feature also provides a means to deploy the same service on multiple environments using a single command. Users can group the environments based on location, tagging and filters.
The following guide provides a step by step guide on how to install sub managers, add them to a central manager using a discovery mechanism, and deploy an application on multiple managers through a single command.

## 1. Installation Cloudify Spire Manager

To install the ***MAIN Manager (Spire)***, please refer to the [Cloudify official documentation.](https://docs.cloudify.co/latest/install_maintain/installation/installing-manager/)

You can also check [Cloudify EC2 Provisioning](https://github.com/cloudify-community/cloudify-catalog/tree/6.4.0-build/cloudify_manager/ec2). It is the package for installing the *Cloudify Manager* on an ec2 AWS instance.

## 2. Installation of sub-managers

You can install a sub-manager in the same way as the _main manager (Spire)_. The most important thing is to make sure that your network is set up correctly (all local managers must be available for Spire Manager).

## 3. Exposing sub managers in Spire Manager

***To use local managers through the central Spire manager, you need to expose information about them in Spire via discovery blueprint. The discovery blueprint automate the process of exposing the relevant configuration properties for each manager and placing them as an environment in the Spire manager.***


### Adding sub-manager through the discovery blueprint
First step is to deploy [manager_discovery.yaml](/submanager_discovery/manager_discovery.yaml) with proper inputs:
- ***endpoint*** - ip of sub manager 
- ***tenant*** - name of submanagar tenant
- ***protocol*** - protocol used by sub manager
- ***port*** - number of port which sub manager is exposed

#### Installation via User Interface
[Upload](https://docs.cloudify.co/latest/working_with/console/widgets/blueprintuploadbutton/) [manager_discovery.yaml](/submanager_discovery/manager_discovery.yaml) to Spire Manager.

Next, click ***Deploy*** under the blueprint tile. Instead of this, you can also click on the blueprint name and next ***[Create deployment](https://docs.cloudify.co/latest/working_with/console/widgets/blueprintactionbuttons/)***

After that, the following window will appear:
![This is an image](/images/submanager_exposition.png)

Fill all necessary information and click ***Install*** button at the bottom of the dialog to start the ***Install*** workflow.
To make sure if *Environment* is installed successfully, check the ***Verification of Installation*** chapter in the following part.

#### Installation with API Call

To use Cloudify API, you can refer to [official API documentation.](https://docs.cloudify.co/latest/developer/apis/rest-service/)

##### Uploading example

```
curl -X PUT \
    --header "Tenant: default_tenant" \
    --header "Content-Type: application/json" \
    -u admin:adminpw \
    "http://localhost/api/v3.1/blueprints/submanager_blueprint?application_file_name=blueprint.yaml&visibility=tenant&blueprint_archive_url=https://url/to/archive/master.zip&labels=customer=EXL"
```

##### Create deployment example
```
curl -X PUT \
    --header "Tenant: default_tenant" \
    --header "Content-Type: application/json" \
    -u admin:adminpw \
    -d '{"blueprint_id": "sub manager_blueprint", "inputs": {"cloudify_username": "admin", "cloudify_manager_ip": "10.0.10.10", "cloudify_port": "80", "cloudify_protocol": "http", "cloudify_tenant": "default_tenant"}, "visibility": "tenant", "site_name": "LONDON", "labels": [{"customer": "EXL"}]}' \
    "http://localhost/api/v3.1/deployments/submanager1?_include=id"
```

##### Install example
```
curl -X POST \
    --header "Tenant: default_tenant" \
    --header "Content-Type: application/json" \
    -u admin:admin \
    -d '{"deployment_id":"sub manager1", "workflow_id":"install"}' \
    "http://localhost/api/v3.1/deployments/submanager1?_include=id"
```
#### Another option to install: cloudify CLI.

To proceed with CLI installation, refer to [official documentation](https://docs.cloudify.co/latest/cli/orch_cli/).

[Upload the blueprint](https://docs.cloudify.co/latest/cli/orch_cli/blueprints/) and then install it.
There are two ways to install:
- [Create deployment](https://docs.cloudify.co/latest/cli/orch_cli/deployments/) and next [start install workflow with executions](https://docs.cloudify.co/latest/cli/orch_cli/executions/)
- [install command](https://docs.cloudify.co/latest/cli/orch_cli/install/)

### Verification of Installation
To verify if the sub manager Environment is created properly, go to the [Environments tab](https://docs.cloudify.co/latest/working_with/console/pages/environments-page/) and Click on created sub manager.
*Execution Task Graph* must contain **Install completed** tile. You can also check if all  tasks are finished with success in *Deployment Events/Logs*.
![This is an image2](/images/verify_part1.png)
*Deployment Info* tab contains [DEPLOYMENT OUTPUTS/CAPABILITIES](https://docs.cloudify.co/latest/working_with/console/widgets/outputs/) part with information about the sub manager. Check if the information is correct.

![This is an image3](/images/verify_part2.png)



### Required secrets

To perform correct management, you need to create also a proper [secret](https://docs.cloudify.co/latest/cli/orch_cli/secrets/) about your **all** sub managers in Spire central manager. There are two ways to connect Spire with sub managers:
- _Token_ - contains the proper value of [Cloudify token](https://docs.cloudify.co/latest/cli/orch_cli/tokens/). The token can be created with command ***cfy token create***
- _User password_ and _username_- contains the value of password and name of the user
![This is an image4](/images/secrets.png)

***The name of secrets must be compatible with the secrets as inputs used in ???Deploy on??? mechanism.***

## 4. ???Deploy on??? mechanism

Depending on the connection type you can deploy the proper blueprint:
- authentication with token -> [deploy_on_token.yaml](/deploy_on_blueprints/deploy_on_token.yaml)
- authentication with user and password -> [deploy_on_user_password.yaml](/deploy_on_blueprints/deploy_on_user_password.yaml)

The current version of [deploy_on_token.yaml](/deploy_on_blueprints/deploy_on_token.yaml)/[deploy_on_user_password.yaml](/deploy_on_blueprints/deploy_on_user_password.yaml) supports public repo, to use *private repo* or *local blueprint* check chapter **7. Resource Config**.

Upload the blueprint to *SPIRE MANAGER*.
Filter (refer to chapter _6. Filters, Location and Labels_) *Environments* and click the action [**???Deploy on???**](https://docs.cloudify.co/latest/working_with/console/widgets/deploymentsview/) from **Bulk action**. The dialog appears. Select the proper blueprint and after that the inputs are visible.

![This is an image5](/images/deploy_on.png)

Inputs description:
- Required:
    - *blueprint_archive* - the URL to zip which contains all necessary files, the source must be available from the sub manager. You can find [examples here](https://github.com/cloudify-community/manager-of-managers/tree/main/blueprint_examples)
    - *blueprint_id* - the name of the blueprint with which the file is to be uploaded
    - *main_file_name* - the name of the blueprint file in zip package
    - *trust_all* - the value of ***CLOUDIFY_SSL_TRUST_ALL*** (true if the certificate is not valid or for testing purpose)
- optional (depends on authentication type):
    - *cloudify_secret_token* - the name of the secret which contains token value
    - *cloudify_password_secret_name* and *cloudify_user_secret_name*- the name of the secret which contains value of the password and the user name of Cloudify user. 

## 5. Verification ???Deploy on??? mechanism
To check if deployments are deployed on local managers, follow the example below/
The examples use uploaded [blueprint](/deploy_on_blueprints/sources/deploy_on_local_blueprint.yaml) with id *blueprint_on_sub manager*.
The used inputs to *"Deploy on"* mechanism:
- *blueprint_id*=*blueprint_on_sub manager* ***Must be uploaded to local!!!***
- *cloudify_password_secret_name*=*admin_password*
- *main_file_name*=*blueprint.yaml*
- *name_of_deployment*=*local_deployment1*
- *trust_all*=*true*
- *value_of_hello*=*MyWorld*

Go to the *Services* by clicking on the button.

![This is an image7](/images/subservices.png)

Verify if the ***install completed*** tile is visible in *Execution Task Graph*.

![This is an image8](/images/subservice.png)

You can also go to the local manager and check if deployment is installed in the *Services* tab.

![This is an image9](/images/submanger_deployment.png)
***Optional [Only when inputs are exposed in Capabilities] !!!***
In this blueprint, inputs are exposed. You can check the value of capabilities.
![This is an image10](/images/local_capabilities.png)
## 6. Filters, Location and Labels

### Filters
Bulk action **"Deploy on"** perform actions on all accesible Environments. If you would like to select only specific *sub manager*, you can use [Filters](https://docs.cloudify.co/latest/working_with/console/widgets/filters/).
You can click **Filter** button (next to _Bulk actions_), and after that, the dialog appears.

![This is an image6](/images/filter.png)
Fill it in and click _Apply_

### Location
The *site* can be set in the *Deployment Metadata* of **Deploy** dialog.
![This is an image6](/images/setsite.png)

To view the location of the selected _Environment_, you can click **Map** button (next to _Bulk actions_ and _Filter_), and after that the dialog appears.

![This is an image6](/images/map.png)

### Labels
The user can specify [*Labels*](https://docs.cloudify.co/latest/developer/blueprints/spec-labels/) in *Deployment Metadata* tile. Labels can be also set via *blueprint*.
Current *Labels* are present in *Deployment Info*.

![This is an image6](/images/labels.png)

The user can add a label by clicking on *Add* button.

## 7. Resource Config

Node **_cloudify.nodes.Component_** allow to create deployment based on the blueprint which can be uploaded to the target manager (sub manager) from 3 types of resources:
- *public repo* - no additional step - [example here](/deploy_on_blueprints/sources/deploy_on_from_public_repo.yaml)
- *private repo* - create two secret: *github_user* and [*github_token*](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) - [example here](/deploy_on_blueprints/sources/deploy_on_from_private_repo.yaml)
- *local blueprint* - upload blueprint (from examples) to target sub manager and proceed with **"Deploy on"** on the main manager - [example here](/deploy_on_blueprints/sources/deploy_on_local_blueprint.yaml)

You can also specify inputs of deployments ([example here](/deploy_on_blueprints/sources/deploy_on_local_blueprint.yaml)) :
```
deployment:
  inputs:
    input0: test
    input1: {get_input: value1}
    input2: {get_secret: sec1}
```
If you use *get_secret: secret1*, you have to check if *secret1* is created.


