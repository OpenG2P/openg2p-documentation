# Performance Testing

## **Data Overview**

The main registry table - 'res\_partner" was populated with 50,000,000 (50 million) records. This 50 million records consisted of 40,000,000 (40 million) individuals and 10,000,000 million groups.

## **User Interface (UI) Performance**

* Inserts and Updates: The current system handles record inserts and updates effectively with no significant delay or latency.
* Search Performance:
  * **Default Index:** The search using the complete\_name index performs well when exact matches are searched (e.g., complete\_name = '...').
  * **Partial Matches:** For substring searches (e.g., complete\_name containing a value), the default index does not suffice.
  * We created a **trigram index** (using the **pg\_trgm** extension) This improves search functionality dramatically. Both LIKE '%CARL%' and LIKE 'CARL%' queries leverage this index effectively, providing results within approximately one second. This also ensured UI search responses remain quick - typically within one to two seconds.
  * We added an index on res\_partner.email – Similar performance observed (similar to complete\_name mentioned above) – both from UI as well as SQL Query sessions.

## **Unique ID (like Aadhaar ID) Search Performance**

* We created an index on **g2p\_reg\_id.value** column. UI Search for ID\_VALUE = ‘123456789012” and ID\_TYPE = ‘AADHAAR’. The resulting Query is

`SELECT "res_partner"."id", "res_partner"."name", "res_partner"."address", "res_partner"."phone", "res_partner"."birthdate", "res_partner"."registration_date", "res_partner"."disabled" FROM "res_partner" WHERE ((((("res_partner"."active" = true) AND ("res_partner"."is_registrant" = TRUE)) AND ("res_partner"."is_group" IS NULL OR "res_partner"."is_group" = FALSE)) AND`

<mark style="color:orange;">**`("res_partner"."id" IN (SELECT "g2p_reg_id"."partner_id" FROM "g2p_reg_id" WHERE ("g2p_reg_id"."value" = '1870938943'))))`**</mark>

<mark style="color:orange;">**`AND ("res_partner"."id" IN (SELECT "g2p_reg_id"."partner_id" FROM "g2p_reg_id"`**</mark>

<mark style="color:orange;">**`WHERE ("g2p_reg_id"."id_type" IN (SELECT "g2p_id_type"."id" FROM "g2p_id_type" WHERE ("g2p_id_type"."id" = '2'))))))`**</mark>

`AND (("res_partner"."partner_share" IS NULL OR "res_partner"."partner_share" = FALSE) OR (("res_partner"."company_id" IN (1)) OR "res_partner"."company_id" IS NULL)) ORDER BY "res_partner"."complete_name" ASC , "res_partner"."id" DESC LIMIT 80`

* Nested queries executed by the Odoo UI are suboptimal and do not utilize the index on g2p\_reg\_id.value – Queries are always on “res\_partner” with nested subqueries on child tables

**Postgres Parallel Queries - Measurements**<br>
------------------------------------------------

Queries were fired in parallel on the Postgres database to measure the performance of the postgres database server.

### **Idle Time**

#### **CPU Measurements**

<figure><img src="../../../../../.gitbook/assets/SR-Scale-Postgres-CPU-Idle-Time.001.jpeg" alt=""><figcaption></figcaption></figure>

### **LIKE query on Non Indexed Text Column (20 threads):**

Number of Parallel threads: 20 (from a client machine that supports 20 threads - 10 Cores with 2 threads per core)

`SELECT "res_partner"."id", "res_partner"."name", "res_partner"."address", "res_partner"."phone", "res_partner"."birthdate", "res_partner"."registration_date", "res_partner"."disabled"`

`FROM "res_partner"`

`WHERE (((("res_partner"."active" = true) AND ("res_partner"."is_registrant" = TRUE)) AND ("res_partner"."is_group" IS NULL OR "res_partner"."is_group" = FALSE)) AND ("res_partner"."name"::text ILIKE $1)) AND (("res_partner"."partner_share" IS NULL OR "res_partner"."partner_share" = FALSE) OR (("res_partner"."company_id" IN (1)) OR "res_partner"."company_id" IS NULL)) ORDER BY "res_partner"."name" ASC, "res_partner"."id" DESC`

`LIMIT 80;`

#### **CPU Utilizations**

<figure><img src="../../../../../.gitbook/assets/SR-Scale-Postgres-CPU-Like-Q-NIC-20.jpg" alt=""><figcaption><p>Total execution time: 3m 39.881448458s</p></figcaption></figure>

### LIKE query on Indexed Text Column (20 threads):

Number of Parallel threads: 20 (from a client machine that supports 20 threads - 10 Cores with 2 threads per core)<br>

`SELECT "res_partner"."id", "res_partner"."name", "res_partner"."address", "res_partner"."phone", "res_partner"."birthdate", "res_partner"."registration_date", "res_partner"."disabled"`

`FROM "res_partner"`

`WHERE (((("res_partner"."active" = true) AND ("res_partner"."is_registrant" = TRUE)) AND ("res_partner"."is_group" IS NULL OR "res_partner"."is_group" = FALSE)) AND ("res_partner"."complete_name"::text ILIKE $1)) AND (("res_partner"."partner_share" IS NULL OR "res_partner"."partner_share" = FALSE) OR (("res_partner"."company_id" IN (1)) OR "res_partner"."company_id" IS NULL) ORDER BY "res_partner"."complete_name" ASC, "res_partner"."id" DESC`

`LIMIT 80;`

#### CPU Utilizations:

<figure><img src="../../../../../.gitbook/assets/SR-Scale-Postgres-CPU-Like-Q-IC-20.jpg" alt=""><figcaption><p>Total execution time: 1.714154125s</p></figcaption></figure>

### LIKE query on Non Indexed Text Column (100 threads):

Number of Parallel threads: 100 (from a client machine that supports 20 threads - 10 Cores with 2 threads per core)

#### CPU Utilizations:

<figure><img src="../../../../../.gitbook/assets/SR-Scale-Postgres-CPU-Like-Q-NIC-100-Threads.jpg" alt=""><figcaption><p>Total execution time: 5.696620167s</p></figcaption></figure>

### LIKE query on Indexed Text Column (100 threads):

Number of Parallel threads: 100 (from a client machine that supports 20 threads - 10 Cores with 2 threads per core)

#### CPU Utilizations:

<figure><img src="../../../../../.gitbook/assets/SR-Scale-Postgres-CPU-Like-Q-IC-100-Threads.jpg" alt=""><figcaption><p>Total execution time: 2.435852958s</p></figcaption></figure>

## DB Storage (Tables)

<figure><img src="../../../../../.gitbook/assets/SR-Scale-Postgres-DB-Storage-Tables.jpg" alt=""><figcaption></figcaption></figure>

## DB Storage (Indexes)

<figure><img src="../../../../../.gitbook/assets/SR-Scale-Postgres-DB-Storage-Indexes.jpg" alt=""><figcaption></figcaption></figure>

## Recommendations

1. Leverage pg\_trgm extension and trigram indexes for text substring searches to improve postgres text searches
2. Odoo Search - Explore if we can insert custom queries for "unique\_id" lookups (implemented as child tables) instead of relying on Odoo’s generic ORM queries. If this is not possible, then it is recommended to add these columns (like unique\_id, aadhaar\_id) into the res\_partner table itself.
3. The ID generation and De-duplication modules need to be implemented using a Celery Background Worker framework.
4. During data migration of large datasets, populate Open Search directly during Migration as in independent task, using Bulk Insertion into OpenSearch. Use Debezium only for production where data will flow in increments rather than bulk.
