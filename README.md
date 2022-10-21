# Using Cloudify as a Manager of Managers  (a.k.a  MoM or Spire)

<figure>
    <img src="/images/spire.png"
         alt="Using Cloudify as a Manager of Managers">
    <figcaption>Using Cloudify as a Manager of Managers</figcaption>
</figure>

The Cloudify managers of managers (Spire) feature allows control of several managers (*local managers*) from one manager (*Spire*) via the deploy-on feature.
The deploy-on feature allows users to deploy services on the discovered environments.
The deploy-on feature also provides a means to deploy the same service on multiple environments using a single command. Users can group the environments based on location, tagging and filters.
The following guide provides a step by step guide on how to install submanagers , add them to a central manager using a discovery mechanism , and deploy and application on multiple managers through a single command.


## 1. Installation Cloudify Spire Manager

To install the ***MAIN Manager (Spire)***, please refer to the [Cloudify official documentation.](https://docs.cloudify.co/latest/install_maintain/installation/installing-manager/)

You can also check [Cloudify EC2 Provisioning](https://github.com/cloudify-community/cloudify-catalog/tree/6.4.0-build/cloudify_manager/ec2). It is the package for installing the *Cloudify Manager* on an ec2 AWS instance.

## 2. Installation submanagers

You can install a sub-manager in the same way as the _main manager (Spire)_. The most important thing is to make sure that your network is set up correctly (all local managers must be available for Spire Manager).

## 3. Exposing submanagers in Spire Manager

***To use local managers in Spire, you need to expose informations about them in Spire via deployment.***


### Install 
First step is to deploy [manager_discovery.yaml](/submanager_discovery/manager_discovery.yaml) with proper inputs:
- ***endpoint*** - ip of submanager 
- ***tenant*** - name of submanagar tenant
- ***protocol*** - protocol used by submanager
- ***port*** - number of port which submanager is exposed

#### Installation via User Interface
[Upload](https://docs.cloudify.co/latest/working_with/console/widgets/blueprintuploadbutton/) [manager_discovery.yaml](/submanager_discovery/manager_discovery.yaml) to Spire Manager.

Next, click ***Deploy*** under the blueprint tile. Instead of this, you can also click on blueprint name and next ***[Create deployment](https://docs.cloudify.co/latest/working_with/console/widgets/blueprintactionbuttons/)***

After that, the following window will appear
![This is an image](/images/submanager_exposition.png)
Fill all neccessary information and click ***Install*** button at the bottom of dialog to start ***Install*** workflow.
To make sure if *Environment* is installed successfully, check ***Verification of Installation*** chapter in the following part.

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
    -d '{"blueprint_id": "submanager_blueprint", "inputs": {"cloudify_username": "admin", "cloudify_manager_ip": "10.0.10.10", "cloudify_port": "80", "cloudify_protocol": "http", "cloudify_tenant": "default_tenant"}, "visibility": "tenant", "site_name": "LONDON", "labels": [{"customer": "EXL"}]}' \
    "http://localhost/api/v3.1/deployments/submanager1?_include=id"
```

##### Install example
```
curl -X POST \
    --header "Tenant: default_tenant" \
    --header "Content-Type: application/json" \
    -u admin:admin \
    -d '{"deployment_id":"submanager1", "workflow_id":"install"}' \
    "http://localhost/api/v3.1/deployments/submanager1?_include=id"
```
#### Another option to install: cloudify CLI.

To proceed with CLI installtion, refere to [official documentation](https://docs.cloudify.co/latest/cli/orch_cli/).

[Upload blueprint](https://docs.cloudify.co/latest/cli/orch_cli/blueprints/) and then install it.
There is two ways of installation:
- [Create deployment](https://docs.cloudify.co/latest/cli/orch_cli/deployments/) and next [start install workflow with executions](https://docs.cloudify.co/latest/cli/orch_cli/executions/)
- [install command](https://docs.cloudify.co/latest/cli/orch_cli/install/)

### Verification of Installation
To verify if submanager Environment is created properly, go to [Environments tab](https://docs.cloudify.co/latest/working_with/console/pages/environments-page/) and Click on created submanager.
*Execution Task Graph* must contain **Install completed** tile. You can also check if all task finish with success in *Deployment Events/Logs*.
![This is an image2](/images/verify_part1.png)
*Deployment Info* tab contains [DEPLOYMENT OUTPUTS/CAPABILITIES](https://docs.cloudify.co/latest/working_with/console/widgets/outputs/) part with information about the submanager. Check if all informations are correct.
![This is an image3](/images/verify_part2.png)

### Required secrets

To perform correct managemen, you need to create also proper [secret](https://docs.cloudify.co/latest/cli/orch_cli/secrets/) about your **all** submanagers in Spire. There are two ways to connect Spire with submanagers:
- _token_ - contains proper value of [cloudify token](https://docs.cloudify.co/latest/cli/orch_cli/tokens/). Token can be created with command ***cfy token create***
- _user password_ and _username_- contains value of password and name of user.
![This is an image4](/images/secrets.png)

***Name of secrets must be compatible with secrets as inputs used in “Deploy on” mechanism.***

## 4. “Deploy on” mechanism.

Depending on connection type you can deploy the proper blueprint:
- authentication with token -> [deploy_on_token.yaml](/deploy_on_blueprints/deploy_on_token.yaml)
- authentication with user and password -> [deploy_on_user_password.yaml](/deploy_on_blueprints/deploy_on_user_password.yaml)

The current version of [deploy_on_token.yaml](/deploy_on_blueprints/deploy_on_token.yaml)/[deploy_on_user_password.yaml](/deploy_on_blueprints/deploy_on_user_password.yaml) supporting public repo, to use *private repo* or *local blueprint* check chapter **7. Resource Config**.

Upload the blueprint to *SPIRE MANAGER*.
Filter (refere to chapter _6. Filters, Location and Labels_) *Environments* and click the action [**“Deploy on”**](https://docs.cloudify.co/latest/working_with/console/widgets/deploymentsview/) from **Bulk action**. The dialog appears. Select proper blueprint and after that the inputs are visible.

![This is an image5](/images/deploy_on.png)

Inputs description:
- Required:
    - *blueprint_archive* - url to zip which contains all necessary files, the source must be available from submanager. You can find [examples here](/blueprint_examples/)
    - *blueprint_id* - name of blueprint with which the file is to be uploaded
    - *main_file_name* - name of blueprint file in zip package
    - *trust_all* - is value of ***CLOUDIFY_SSL_TRUST_ALL*** (true if certificate is not valid or for testing purpose)
- optional (depends on authentication type):
    - *cloudify_secret_token* - name of secret which contains token value
    - *cloudify_password_secret_name* and *cloudify_user_secret_name*- name of secret which contains password value

## 5. Verification “Deploy on” mechanism
To check if deployments are deployed on local managers, follow the example below/
The examples use uploaded [blueprint](/deploy_on_blueprints/sources/deploy_on_local_blueprint.yaml) with id *blueprint_on_submanager*.
The used inputs to *"Deploy on"* mechanism:
- *blueprint_id*=*blueprint_on_submanager* ***Must be uploaded to local!!!***
- *cloudify_password_secret_name*=*admin_password*
- *main_file_name*=*blueprint.yaml*
- *name_of_deployment*=*local_deployment1*
- *trust_all*=*true*
- *value_of_hello*=*MyWorld*

Go to the *Services* by clicking on button
![This is an image7](/images/subservices.png)
Verify if ***install completed*** tile is visible in *Execution Task Graph*.
![This is an image8](/images/subservice.png)
You can also go to the local manager and check if deployment is installed in *Services* tab.
![This is an image9](/images/submanger_deployment.png)
***Optional [Only when inputs are exposed in Capabilities] !!!***
In case of this blueprint, inputs are exposed. You can check the value of capabilities
![This is an image10](/images/local_capabilities.png)
## 6. Filters, Location and Labels

### Filters
Bulk action **"Deploy on"** perform actions on all accesible Environments. If you would like to select only specific *submanager*, you can use [Filters](https://docs.cloudify.co/latest/working_with/console/widgets/filters/).
You can click **Filter** button (next to _Bulk actions_), after that the dialog appears
![This is an image6](/images/filter.png)
Fill it and click _Apply_

### Location
The *site* can be set in *Deployment Metadata* of **Deploy** dialog.
![This is an image6](/images/setsite.png)

To view location of selected _Environment_, you can click **Map** button (next to _Bulk actions_ and _Filter_), after that the dialog appears.
![This is an image6](/images/map.png)

### Labels
The user can specify [*Labels*](https://docs.cloudify.co/latest/developer/blueprints/spec-labels/) in *Deployment Metadata* tile. Labels can be also set via *blueprint*.
Current *Labels* are present in *Deployment Info*
![This is an image6](/images/labels.png)
The user can add label by clicking on *Add* button.

## 7. Resource Config

Node **_cloudify.nodes.Component_** allow to create deployment based on blueprint which can be uploaded to target manager (submanager) from 3 types of resources:
- *public repo* - no additional step - [example here](/deploy_on_blueprints/sources/deploy_on_from_public_repo.yaml)
- *private repo* - create two secret: *github_user* and [*github_token*](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token) - [example here](/deploy_on_blueprints/sources/deploy_on_from_private_repo.yaml)
- *local blueprint* - upload blueprint (from examples) to target submanager and proceed with **Deploy on** on main manager - [example here](/deploy_on_blueprints/sources/deploy_on_local_blueprint.yaml)

You can also specify inputs of deployments ([example here](/deploy_on_blueprints/sources/deploy_on_local_blueprint.yaml)) :
```
deployment:
  inputs:
    input0: test
    input1: {get_input: value1}
    input2: {get_secret: sec1}
```
If you use *get_secret: secret1*, you have to check if *secret1* is created.


