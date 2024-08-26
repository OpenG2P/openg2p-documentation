---
description: >-
  All documentation relating to load testing of REST APIs of the SPAR (Social
  Protection Account Registry - aka Account Mapper) module
---

# spar-load-test

The corresponding repository in github can be found here -> [https://github.com/OpenG2P/spar-load-test.git](https://github.com/OpenG2P/spar-load-test.git)

## Organisation of files

We use **JMeter** to perform the load testing of the APIs. The SPAR module consists of two independent microservices.&#x20;

1. spar-mapper microservice - this deals with maintenance (insert/delete) and lookup (resolution) of the account registry (id - to - account mapper).
2. spar-self-service microservice - this caters to the self service aspect of this module. APIs in this microservice target the end beneficiary who logs in into the self-service-ui application and updates his/her account into the registry.

Accordingly, there are two JMX files (files where all the end-points and their necessary Request/Response objects (JSONs) in this repository.

1. spar-mapper.jmx
2. spar-self-service.jmx

Apart from these two JMX files, the repository also contains the following files

1. **script-generate-id-fa-mapper.py** - This file generates a CSV file named - sample-data.csv. This csv file contains data that can be inserted into the table - "id\_fa\_mapping". This table is owned by the spar-mapper microservice. This table contains the final mapping between a beneficiary identifier and the beneficiary's account address (aka financial address). Right now this python script generates 1000 records in the csv file. Use this generated csv file to insert records manually into the id\_fa\_mapping table.
2. **script-generate-requestbody-mapper-apis.py** - Once we have the data into ther id\_fa\_mapping table, the mapper resolve API, which retrieves the financial address for a given beneficiary Id, takes a list of beneficiary id in its request body. This script reads the data from the id\_fa\_mapping table and generates the array containing the beneficiary ids. You have to take this array object and use it in the request body of the spar-mapper/resolve API. This API will then retrieve the financial addreess (account address or account details) for these beneficiary ids. The spar-mapper.jmx file currently already contains 1000 beneficiary ids. You have to use these python files, if you wish to conduct tests with different load scenarios.
3. sample-data.csv - This file is the output of "script-generate-id-fa-mapper.py". As mentioned above, currently this csv file contains 1000 records for id\_fa\_mapping.

## End Points covered in load test

The following end points have been covered in our load test.

1. **spar-mapper.jmx (spar-mapper microservice)**
   1. resolve
   2. update
   3. abc...
2. **spar-self-service.jmx (spar-self-service microservice)**
   1. get-id-fa-mapping
   2. xyz
   3. abc...

## Approach to testing

## Testing measurements and outcome

## Recommended deployment

