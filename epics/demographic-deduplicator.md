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



## Folder Structure

<figure><img src="../.gitbook/assets/Screenshot from 2023-12-12 14-13-13.png" alt=""><figcaption></figcaption></figure>

Before using the application, make sure you have all these folders and files.

## Training

To use this service, you first need to train the dedupe object. There is directory called [training](https://github.com/manoharsuggula/openg2p-demodedupe/tree/main/training). It contains the training files for the csv and db. Before using the service, you need to run these files separately. The whole training will take place in memory.&#x20;

### CSV

To train the csv deduplicator,  you need to change 2 lines in the code ([csv\_training.py](https://github.com/manoharsuggula/openg2p-demodedupe/blob/main/training/csv\_training.py)). In the main, you need to add the path to the csv file in the input\_file variable. then you need to fill the fields variable. They are the fields of interest for deduplication. You need to make sure that the fields you mention here are the columns of the csv file. There is an example in the [file](https://github.com/manoharsuggula/openg2p-demodedupe/blob/main/training/csv\_training.py) for your reference.&#x20;

After you fill these, you can just run the file.&#x20;

It will read the csv data and trains the dedupe object on the data. Then it will cross check the training with the user as shown.&#x20;

```
Phone :  2850617
Address :  3801 s. wabash
Zip : 26012
Site name :  ada s. mckinley st. thomas cdc

Phone :  2850617
Address :  3801 s wabash ave
Zip : 26012
Site name :  ada s. mckinley community services - mckinley - st. thomas

Do these records refer to the same thing?
(y)es / (n)o / (u)nsure / (f)inished
```

If you think they both are duplicates, press 'y' else press 'n'.&#x20;

The more labelled examples you give it, the better the deduplication results will be. At minimum, you should provide **10 positive matches (yes)** and **10 negative matches (no)**. After completing the labelling, you need to press 'f' to finish the training.&#x20;

After the process is done, code will output a settings\_file and training.json file. You will be needing the **settings\_file** for later. You need to add that file in the [configurations](https://github.com/manoharsuggula/openg2p-demodedupe/tree/main/configurations) folder. If there is an existing file, replace it.&#x20;

### JSON

JSON training is same as the csv training. In fact you can use the same training files of CSV for JSON, if the fields are same.&#x20;

### Database

Database deduplication training is also a bit similar to that of CSV.&#x20;

To train the db deduplicator,  you need to change a few lines in the code ([db\_training.py](https://github.com/manoharsuggula/openg2p-demodedupe/blob/main/training/db\_training.py)). You need to fill in the "db\_conf" variable. There is an example about how to fill db\_conf in the file for your reference. Then you need to fill in the fields variable. They are the fields of interest for deduplication. You need to make sure that the fields you mention here are the columns of the database table. you also need to edit the SELECT\_QUERY variable. You need to write a query in such a way that the output of the query should contain the id\_field and the fields of interest. There is an example in the [file](https://github.com/manoharsuggula/openg2p-demodedupe/blob/main/training/db\_training.py) for your reference.&#x20;

Similar to [CSV training](demographic-deduplicator.md#csv), here also, user will be asked to crosscheck the training. After the process is done, code will output a db\_settings and db\_training.json file. You will be needing the **db\_settings** for later. You need to add that file in the [configurations](https://github.com/manoharsuggula/openg2p-demodedupe/tree/main/configurations) folder. If there is an existing file, replace it.&#x20;

### Limitations:

There are a few limitations in training. The process is getting killed if we provide data more than 1500 rows for DB training. It is because, we are training in the memory. So, try to train on data less than 1500 rows. For CSV training, it is 3500 rows.&#x20;

## Deduplication

To use this, you first need to complete [training](demographic-deduplicator.md#training). Now that you have the training available, you can now use deduplicator on the data. First things first, before starting the server, add the settings\_file to the configurations folder as told earlier.&#x20;

Now give the path of the setting\_file as an argument to the below API according to csv/db deduplication in the [app.py](https://github.com/manoharsuggula/openg2p-demodedupe/blob/main/src/app.py) file.&#x20;

<pre class="language-python"><code class="lang-python"><a data-footnote-ref href="#user-content-fn-1">load_file_on_startup</a>
</code></pre>

When the server starts, it loads the file and creates the deduper global object. It is later used for deduplication.&#x20;

For the db deduplication, we need to fill in the [db\_conf.json](https://github.com/manoharsuggula/openg2p-demodedupe/blob/main/configurations/db\_conf.json) file in the configurations folder. The file is already filled with an example. Change it accordingly.

```python
Fill the db_conf.json file with the db configuration
The file should contain the following fields:
	 NAME: Name of the database
	 USER: Username of the database
	 PASSWORD: Password of the database
	 HOST: Host of the database
	 PORT: Port of the database
	 table: Table name to be used
	 id_field: Primary key of the table
	 fields: List of fields to be used for deduplication
```

The db connections are made when the server starts.&#x20;

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

Here, we need to upload the csv file on which computation needs to be done. This file should have all the fields mentioned/used in the training. We also need to give the threshold. It will now create an async task, with a txn\_id, which will call the process function which does all the deduplication. It will also add the txn\_id to csv\_queue dict. It will assign "processing" tag to this txn\_id. The async task will run simultaneously. When the async task is completed, the tag of the txn\_id is changed to "completed".&#x20;

```python
async def csv_deduplicate_status(txn_id):
```

It is used to check if the txn\_id tag is "processing" or "completed".

```python
async def csv_deduplicate_download(txn_id):
```

When the status is completed, we can download the output csv from this api. If the status is processing, it return a message saying status is processing.

The downloaded file will contain all the original columns and 2 extra columns: "cluster\_id" and "confidence score". All the records with same cluster\_id are duplicates. &#x20;

#### Note:&#x20;

Before using csv deduplication, you need to make sure if there are folders named csv\_input and csv\_output. If there aren't any create them.&#x20;

### Database

The database connections will be made according to [db\_conf.json](https://github.com/manoharsuggula/openg2p-demodedupe/blob/main/configurations/db\_conf.json) file. We will use the following APIs &#x20;

```
APIs:
/db_deduplicate/
```

```python
async def db_deduplicate(threshold:float):
```

There is nothing special we need to do here. The [db\_conf.json](https://github.com/manoharsuggula/openg2p-demodedupe/blob/main/configurations/db\_conf.json) file is the key here. The API will use that information and deduplicates the data. After the process is done, 2 extra tables will be added in the database namely: "blocking\_map" and "entity\_map". The entity\_map is the output table. It will have 3 columns: "id", "canon\_id" and "score". The id column is the id of the record. The conon\_id is the cluster id, and the score is the confidence score.&#x20;

To explain it in simple terms: All the ids which have the same canon\_id are duplicate records with the corresponding confidence score.&#x20;

#### Limitations:

This process will take around 1hr or even 2hrs to complete.

## Future Work

Divide the code into different files.&#x20;

Explore if we can complete this in less time.&#x20;

Explore different parameters of dedupe library.



[^1]: 
