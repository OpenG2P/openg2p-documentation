# Use Case Implementation

OpenG2P Registry provides a base platform to create a Registry but it still needs a manifestation specific to your use case.  A typical implementation will involve the following process.

### Phase 1:  Domain requirements

#### Purpose

In this phase we understand the use case and your requirements in as much detail as possible to map it the product and identify and gaps vis a vis what OpenG2P offers. In this phase we also understand the plan for doing a pilot or full rollout, the scale of the pilot/rollout, timelines and so on.

#### Information to collect

* Your country? -> "country"
* Your department/organisation that wants to use OpenG2P Registry.  -> "department"
* &#x20;What is your end2end use case — is this a benefit delivery program, if so what is the name of the program for which Registry is required? -> "program".  Or your mandate is just to create a registry like a National Social Registy or Farmer Registry, or Family Registry that will serve several programs, use cases and several departements? Desicribe the type of registry - like 'Social Registry', 'Workers Registry', 'Farmer Registry', 'Disability Registry', 'Family Registry', 'Students Registry', 'Health Workers Registry', 'Crop Registry', 'Land Registry', 'Vehicle Registry' etc -> "registry\_type"
* Describe your use case in detail. How will the data be consumed/used from this registry — who are the consumers. Would you like to share the data with other departments, systems, agencies, applications? -> "use\_case\_info".
* What is the process of registration? would it be online via portal, or offline via agents collecting information?  -> "offline\_registrations" (true/false)
* What kind of documents are required for registration? -> "documents"
* Is this a 'green field' implementation or 'brown field'. 'green field' means a fresh data colloection. While 'brown field' implies  you already have existing data that you would like to import. In which in what form is the data available - is it Excel sheets, or some database?  Or is this data available via APIs of some of other system.  -> "existing\_data\_import" (true/false)&#x20;
* What are the various functionalities you are looking for your use case that must be supported by OpenG2P Registry?
* Are you ok with having developement sandbox installed on a public cloud? -> "sandbox\_on\_cloud"  (true/false)
* Will your pilot and production system run on on-prem hardware or you are ok with running the same on cloud?  -> "production\_on\_cloud" (true/false)
* What is the number of primary records of the subjects (e.g. farmer, citizen, vehicles, families etc) expected the registry?  -> "n\_records"&#x20;
* Which ID(s) will be used for the records? "id\_types"
* Any specific interoperability requirements? -> "interoperability"

#### Completion criteria

* The phase can be considered completed when all the above information is available.&#x20;

#### Output

* Requirement analysis with mapping of features/functionality, and importantly gaps between what is required versus what is offered by OpenG2P. The gaps should be clearly marked out separately.&#x20;
* Guidance on the compute resources and other resource requirements for creating the setups for development, pilot and rollout

### Phase 2: Customization

#### Purpose

In this phase the configuration and code changes are done after obtaining fine grained details of registry like registry parameters, constraints, number of registers, number of tables etc. Changes to configurations and code and then done and artifacts created for deployments.

#### Information to collect &#x20;

* What the full name of your registry? Keep the name as short as possible. This will appear on all user interface text fields. Example 'Health Workers Registry'  -> "registry\_name"
* What is the registry name menemonic? Keep this very short. This is be used in code, file names, Docker name, Service name etc.  Suggested is lower case of registry name separated by hyphens, e.g. 'health-worker'. Do not add add 'registry' as a prefix or suffix to the name as it will be added automatically. -> "registry\_mnemonic".
* How many registers does it contain? Give name of each register. -> "registers\[]"&#x20;
* Give exact names of the database columns for each register. -> "register\[name, \[columns]".
* What are the various constraints between the tables (database contraints) -> "database\_constraints\[]"
* What is the number of digits required for your functional ID? -> "id\_length"

#### Actions

* Git clone the following repositories in your local machine in a "build folder". Make sure the "build folder" is created fresh everytime, and  is empty -  does not contain any previous repos or contents:
  * Repo 1: [https://github.com/OpenG2P/openg2p-registry-gen2-extensions](https://github.com/OpenG2P/openg2p-registry-gen2-extensions)  branch 'develop'
  * Repo 2: [https://github.com/OpenG2P/openg2p-registry-gen2-docker](https://github.com/OpenG2P/openg2p-registry-gen2-docker) branch 'develop'
* Inside Repo 1, in the root folder, make a copy of the entire folder `openg2p-registry-farmer-extension`  to `openg2p-registry-<registry_menomic>-extension`&#x20;
* Inside Repo 2 inside each of the following folders, create a copy of `farmer-develop.txt` file. Change the name to `<registry_menemonic>-develop.txt` .
  * staff-portal-api
  * partner-api
  * celery
* Inside each of `<registry_menemonic>-develop.txt`  in the above folders, apply the following changes
  * Replace the line `git://develop//https://github.com/openg2p/openg2p-registry-gen2-extensions#subdirectory=openg2p-registry-farmer-extension`  with `{{workDir}}/openg2p-registry-gen2-extensions/openg2p-registry-<registry_mneominic>-extension`   _(note there is no '#' or 'subdirectory' in this path)_.
  * In the first line which contains the Docker name, replace the word 'farmer' with `<registry_mnemonic>`.&#x20;
* From the root directory of Repo 2 run the follwing commands:
  * `scripts/build.sh staff-portal-api/<registry-menemonic>-develop.txt`&#x20;
  * `scripts/build.sh partner-api/<registry-menemonic>-develop.txt`
  * `scripts/build.sh celery/<registry-menemonic>-develop.txt`

### Phase 3: Sandbox

### Phase 4: Pilot&#x20;

### Phase 5: Full rollout

## &#x20;
