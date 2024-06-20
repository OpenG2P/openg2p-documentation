---
layout:
  title:
    visible: true
  description:
    visible: false
  tableOfContents:
    visible: true
  outline:
    visible: true
  pagination:
    visible: true
---

# Link API

## Approach

10 million id-account mapping records will be created in each run. These 10 million records can be created in multiple threads - 8, 10, 12 etc.  Each thread submits the payload to the link API. The payload consists of "n" number of records. "n" is called the payload size. We can configure the value of "n". In our experiments, we have used 1,000, 2,000, 5,000 and 10,000 as the payload size.&#x20;

For example, if run with 8 threads and a payload size of 1,000

**Thread 1**&#x20;

* Thread 1 will be allocated 10 M divided by 8 = 1.25 M records
* Invocation 1 -> Payload will contain 1 to 1000 records
* Invocation 2 -> Payload will contain 1001 to 2000 records ....and so on
* Number of invocations in Thread 1 = 1.25M / 1000 = 1250 invocations
* The 1,250th invocation will contain records 1,249,001 to 1,250,000

Similarly, Thread 2 will do 1,250 invocations with 1000 records per invocation. Thread 2 will process records 1,250,001 to 2,500,000.

Thread 3 ...and so on....

## Test Script

The test script can be found here.

The following values have to be adjusted before each run.

Total number of records = 10,000,000 (10 Million)

Payload size = 1,000, 2,000, 5,000, 10,000 (number of records per API submission)

Number of threads = 1, 4, 8, 10, 12, 14

## Readings before test

## Test scenarios

<mark style="color:green;">**8 concurrent users, 1000 requests per API, 1 second ramp up time per user**</mark>
