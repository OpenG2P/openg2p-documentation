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

**Objective:** Create 10 million ID-account mapping records in each run using multiple threads.

**Configuration Details:**

* **Total number of records to be linked:** 10 million
* **Number of threads:** 8, 10, 12, etc.
* **Payload size:** Configurable; used sizes are 1,000, 2,000, 5,000, and 10,000 records.

**Process:**

1. Each thread submits payloads to the link API.
2. Payload size (`n`) determines the number of records in each submission.

**Example Configuration:**

* **Threads:** 8
* **Payload Size:** 1,000

**Thread Allocation and Invocations:**

* Each thread processes (10 million / number of threads) records.
* **For 8 threads:**
  * Each thread processes 10 million / 8 = 1.25 million = 1.25 million records.
  * **Payload Size:** 1,000 records.

<mark style="color:orange;">**Thread 1:**</mark>

* **Total Records:** 1.25 million
* **Number of Invocations:** 1.25 million / 1,000 = 1,250 invocations
  * **Invocation 1:** Records 1 to 1,000
  * **Invocation 2:** Records 1,001 to 2,000
  * ...
  * **Invocation 1,250:** Records 1,249,001 to 1,250,000

<mark style="color:orange;">**Thread 2:**</mark>

* **Total Records:** 1.25 million
* **Number of Invocations:** 1,250
  * **Invocation 1:** Records 1,250,001 to 1,251,000
  * **Invocation 2:** Records 1,251,001 to 1,252,000
  * ...

**Subsequent Threads:**

* <mark style="color:orange;">**Thread 3**</mark>**:** Records 2,500,001 to 3,750,000 (1,250 invocations)
* <mark style="color:orange;">**Thread 4**</mark>**:** Records 3,750,001 to 5,000,000 (1,250 invocations)
* ...
* <mark style="color:orange;">**Thread 8**</mark>**:** Records 8,750,001 to 10,000,000 (1,250 invocations)

**Summary:**

* Each thread processes 1.25 million records.
* The number of invocations per thread is determined by the payload size.
* Example run with 8 threads and a payload size of 1,000 results in 1,250 invocations per thread.

## Test script

The test script can be found [here](https://github.com/OpenG2P/openg2p-spar-mapper-test/tree/1.1.0/load-test). The table - id\_fa\_mapping - needs to be truncated before each run. The following values are configurable and need to be modified suitably.

total\_number\_of\_records = 10,000,000

number\_of\_threads = 8

payload\_size = 1,000



## Readings before test

## Test scenarios

<mark style="color:green;">**threads = 8, payload size = 1,000, 1 second ramp up time per thread**</mark>
