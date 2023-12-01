# Demographic Deduplicator

## Introduction

This is the description of how to use the new demographic deduplicator engine. The new deduplicator is based on the dedupe library of python. It can find the duplicate entries of a given data based on a given threshold value. We can use this on&#x20;

1. csv&#x20;
2. json &#x20;
3. Database

### Pre-requisites:

To use this service, you need to have some libraries. They are mentioned in requirements.txt file. They are as follows

```pip-requirements
dedupe
psycopg2>=2.5.4
unidecode>=0.04.16
requests
aiofiles
asyncio
uuid
itertools
```

&#x20;Other than these, you also need PostgreSQL in your machine for the database deduplication.&#x20;



## Training

To use this service, you first need to train the dedupe object. There is directory called training. It contains the training files for the csv, json and db. Before using the service, you need to run these files separately. The whole training will take place in memory.&#x20;

### CSV

To train the csv deduplicator,  you need to change 2 lines in the code (csv\_training.py). You need to add the path to the csv file in the input file variable. Then you need to specify the fields of interest as explained in the file. You need to make sure that the fields you mention are the columns of the csv file. After you fill these, you can just run the file.&#x20;

It will read the csv data and trains the dedupe object on the data. Then it will cross check the training with the user as shown.&#x20;

```
Phone :  2850617
Address :  3801 s. wabash
Zip :
Site name :  ada s. mckinley st. thomas cdc

Phone :  2850617
Address :  3801 s wabash ave
Zip :
Site name :  ada s. mckinley community services - mckinley - st. thomas

Do these records refer to the same thing?
(y)es / (n)o / (u)nsure / (f)inished
```

The more labelled examples you give it, the better the deduplication results will be. At minimum, you should try to provide **10 positive matches** and **10 negative matches**. After completing the labelling, you need to press 'f' to finish the training.&#x20;

After the process is done, you will get a settings\_file and training.json file. You will be needing the **settings\_file** for later.&#x20;

### JSON

JSON training is same as the csv training. In fact you can use the same training files of CSV for JSON, if the fields are same.&#x20;

### Database

Database deduplication training is also a bit similar to that of CSV. The difference is that here, you need to mention the db configuration instead of providing csv file. You need to fill in the db\_conf dictionary and field of interest as mentioned in the file. Similar to CSV training, here also, user will be asked to crosscheck the training.&#x20;

### Limitations:

There are a few limitations here. The process is getting killed if we provide data more than 1500 rows for DB training. It is because, we are training in the memory. So, try to train on data less than 1500 rows. For CSV, it is 3500 rows.&#x20;



## Deduplication

Now that you have the training available, you now deduplicate the data. First things first, before starting the server, add the settings\_file to the configurations folder. Now give the path of the setting\_file to the below API according to csv/db deduplication. &#x20;

```python
load_file_on_startup
```

When the server starts, it loads the file and creates the dedupe global object. It is later used for deduplication.&#x20;

For the db deduplication, we need to fill in the db\_conf.json file in the configurations folder. The db connections are made when the server starts.&#x20;

We also need to specify the threshold value every where. The dedupe will cluster the similar records. It computes a confidence score(similarity score) for every two records. Then it will cluster the records if their confidence score is more than the threshold value. So, if the threshold value is less, then less similar records get clustered. So, we need to set the threshold value appropriately. &#x20;

### JSON

```python
API: json_deduplicate
```

```python
async def json_deduplicate(threshold:float,input_data: DictInput):
```

We give the whole data as a json. It will return a json in the following format:

```python
Output format - {cluster_id:[list of similar/duplicate ids]}
```

All the ids in the lists are duplicate records.

### CSV

```python
APIs:
/csv_deduplicate/
/csv_deduplicate_status/{txn_id}
/csv_deduplicate_download/{txn_id}
```

```python
async def csv_deduplicate(threshold:float, in_file: UploadFile):
```

Here, we need to upload the csv file on which computation needs to be done. This file should have all the fields mentioned/used in the training. We also need to give the threshold. It will now create an async task, with a txn\_id, which will call the process function which does all the deduplication. It will also add the txn\_id to a queue. It will assign "processing" tag to this txn\_id. The async task will run simultaneously. When the async task is completed, the tag of the txn\_id is changed to "completed".&#x20;

```python
async def csv_deduplicate_status(txn_id):
```

It is used to check if the txn\_id tag is "processing" or "completed".

```python
async def csv_deduplicate_download(txn_id):
```

When the status is completed, we can download the output csv from this api. If the status is processing, it return a message saying status is processing.

### Database

