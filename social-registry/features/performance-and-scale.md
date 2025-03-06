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

# Performance & Scale

**Data Overview**

The main registry table - 'res\_partner" was populated with 50,000,000 (50 million) records. This 50 million records consisted of  40,000,000 (40 million) individuals and 10,000,000 million groups.

**User Interface (UI) Performance**

* Inserts and Updates: The current system handles record inserts and updates effectively with no significant delay or latency.
* Search Performance:
  * **Default Index:** The search using the complete\_name index performs well when exact matches are searched (e.g., complete\_name = '...').
  * **Partial Matches:** For substring searches (e.g., complete\_name containing a value), the default index does not suffice.
  * We created a **trigram index** (using the **pg\_trgm** extension) This improves search functionality dramatically. Both LIKE '%CARL%' and LIKE 'CARL%' queries leverage this index effectively, providing results within approximately one second. This also ensured UI search responses remain quick - typically within one to two seconds.
  * We added an index on res\_partner.email – Similar performance observed (similar to complete\_name mentioned above) – both from UI as well as SQL Query sessions.

**Aadhaar ID Search Performance**

* We created an index on **g2p\_reg\_id.value** column. UI Search for ID\_VALUE = ‘123456789012” and ID\_TYPE = ‘AADHAAR’. The resulting Query is

&#x20;SELECT "res\_partner"."id", "res\_partner"."name", "res\_partner"."address", "res\_partner"."phone", "res\_partner"."birthdate", "res\_partner"."registration\_date", "res\_partner"."disabled" FROM "res\_partner" WHERE ((((("res\_partner"."active" = true) AND ("res\_partner"."is\_registrant" = TRUE)) AND ("res\_partner"."is\_group" IS NULL OR "res\_partner"."is\_group" = FALSE)) AND&#x20;

<mark style="color:orange;">**("res\_partner"."id" IN (SELECT "g2p\_reg\_id"."partner\_id" FROM "g2p\_reg\_id" WHERE ("g2p\_reg\_id"."value" = '1870938943'))))**</mark>&#x20;

<mark style="color:orange;">**AND ("res\_partner"."id" IN (SELECT "g2p\_reg\_id"."partner\_id" FROM "g2p\_reg\_id"**</mark>&#x20;

<mark style="color:orange;">**WHERE ("g2p\_reg\_id"."id\_type" IN (SELECT "g2p\_id\_type"."id"**</mark>&#x20;

<mark style="color:orange;">**FROM "g2p\_id\_type" WHERE ("g2p\_id\_type"."id" = '2'))))))**</mark> \


AND (("res\_partner"."partner\_share" IS NULL OR "res\_partner"."partner\_share" = FALSE) OR (("res\_partner"."company\_id" IN (1)) OR "res\_partner"."company\_id" IS NULL)) ORDER BY "res\_partner"."complete\_name" ASC , "res\_partner"."id" DESC  LIMIT 80

* Nested queries executed by the Odoo UI are suboptimal and do not utilize the index on g2p\_reg\_id.value – Queries are always on “res\_partner” with nested subqueries on child tables

**ID Generation and Deduplication Challenges**

* MOSIP ID Generator: The current ID generation process does not function as required. With multiple attempts, we were able to generate the ID only for a handful of records. Neither could we run the CRON job reliably nor could we make it work with even 10,000 records.
* Deduplication: We could not make Deduplication work with this volume of records in the system.

DBZM and OpenSearch

* Encountered frequent space issues in DBZM-Kafka and unreliability in the pipeline due to high volumes.

**Postgres Parallel Queries - Measurements**\
Queries were fired in parallel on the Postgres database to measure the performance of the postgres database server.&#x20;

**CPU Measurements - Idle time**

\
LIKE query on Non Indexed Text Column:&#x20;

Number of Parallel threads: 20 (from a client machine that supports 20 threads - 10 Cores with 2 threads per core)\
\`

SELECT "res\_partner"."id", "res\_partner"."name", "res\_partner"."address", "res\_partner"."phone", "res\_partner"."birthdate", "res\_partner"."registration\_date", "res\_partner"."disabled"

FROM "res\_partner"

WHERE (((("res\_partner"."active" = true) AND ("res\_partner"."is\_registrant" = TRUE)) AND ("res\_partner"."is\_group" IS NULL OR "res\_partner"."is\_group" = FALSE)) AND ("res\_partner"."name"::text ILIKE $1)) AND (("res\_partner"."partner\_share" IS NULL OR "res\_partner"."partner\_share" = FALSE) OR (("res\_partner"."company\_id" IN (1)) OR "res\_partner"."company\_id" IS NULL)) ORDER BY "res\_partner"."name" ASC, "res\_partner"."id" DESC

LIMIT 80;

\`

CPU Utilizations:\
![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXe2251itbFax3LhdwLR71AvhCqXD0-ETDqXPrsFthA1UZdLAjrNEVkswjyRayMipIXhFZPjhfwyUj4Pi-d6afe_ukUoLBups1kcIXJ63LfJLSf83GL5eFS3-5TveBMXyLYv4_9-Jg?key=WPy1A4mzx1kgXmuFyH2Q6hBe)\
Total execution time: 3m 39.881448458s\
\


LIKE query on Indexed Text Column:&#x20;

Number of Parallel threads: 20 (from a client machine that supports 20 threads - 10 Cores with 2 threads per core)\
\
\`

SELECT "res\_partner"."id", "res\_partner"."name", "res\_partner"."address", "res\_partner"."phone", "res\_partner"."birthdate", "res\_partner"."registration\_date", "res\_partner"."disabled"

FROM "res\_partner"

WHERE (((("res\_partner"."active" = true) AND ("res\_partner"."is\_registrant" = TRUE)) AND ("res\_partner"."is\_group" IS NULL OR "res\_partner"."is\_group" = FALSE)) AND ("res\_partner"."complete\_name"::text ILIKE $1)) AND (("res\_partner"."partner\_share" IS NULL OR "res\_partner"."partner\_share" = FALSE) OR (("res\_partner"."company\_id" IN (1)) OR "res\_partner"."company\_id" IS NULL) ORDER BY "res\_partner"."complete\_name" ASC, "res\_partner"."id" DESC

LIMIT 80;

\`

CPU Utilizations:

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXc_Xp52DutQJH6yLzpLxXqFtjzan-pXxuR3Fys8vBa4dLdcCFiRXhWy2xBp5RmCNF7Lvnppc4jipW7NGm80DEZUdYuZR4sBfIJWFStN7CzBOywcYT6lYKg4BC6aUWRgmEbqxWwNWg?key=WPy1A4mzx1kgXmuFyH2Q6hBe)\
Total execution time: 1.714154125s\
\


LIKE query on Non Indexed Text Column:&#x20;

Number of Parallel threads: 100 (from a client machine that supports 20 threads - 10 Cores with 2 threads per core)&#x20;

\
CPU Utilizations:\
![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXemZZmaOhemQaM5tyr2MA7TCw1T_2VggGzzGXXLN4_7FAzsPxsSWSJ1Vrqe0hgqr1oB6qFfmAgZP7-y79uAbGYuQ9SYEH9G50mHaw9S2zNABI_zpO9ninzYY76QnEXcO68iHQv-ZA?key=WPy1A4mzx1kgXmuFyH2Q6hBe)

Total execution time: 2.435852958s\
\
LIKE query on Non Indexed Text Column:&#x20;

Number of Parallel threads: 500 (from a client machine that supports 20 threads - 10 Cores with 2 threads per core)\
\


CPU Utilizations:\
![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXef7VaUhb9yTFTUJsJwyQLRoWM2f9CxWjefyuLdWrDyMd4mJqrByCn8ZrZK8SyCYDI99hKrnVVA-qp1ugdzKaJV_gjgjW3CmMqpXM2IwlwsOJpA2S3BPNUWaqdHOg8dThj6gzSd?key=WPy1A4mzx1kgXmuFyH2Q6hBe)\
Total execution time: 5.696620167s

\
\


DB Storage - Tables

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXdazqqUfW72NBdBjhH5GfGoYAZ5UW6jZNNifNBZMG2gRDRU80BKMwbOhZ829udgdzLLZilbtqNEJgzg5yx5NtQv7B5asUQemENS3lPwWZo2mmEA6HY4FtD4wxpnZaB1mOlcPN67?key=WPy1A4mzx1kgXmuFyH2Q6hBe)

\


DB Storage - Indexes

![](https://lh7-rt.googleusercontent.com/docsz/AD_4nXfoxRIqc-737NZovoAyXqBeIdWMIeKOsF1QlRZ-wB9IvhCKCK4U0VC3nNepotvQ2wYuqb5fwO1e4Yvpd_GXAroVjfGX9nUExIww8zRejz7QdHRf9gWwTDeApvRzcu4btj-vlaoJKA?key=WPy1A4mzx1kgXmuFyH2Q6hBe)

#### Action Points

1. Leverage pg\_trgm extension and trigram indexes for text substring searches to improve postgres text searches&#x20;
2. Odoo Search - Explore if we can insert custom queries for Aadhaar ID lookups (child tables) instead of relying on Odoo’s generic ORM queries. If this is not possible, then we will have to bring these columns (AADHAAR) into the res\_partner table itself.
3. Re-Design the ID generation module
4. Re-Design Deduplication module
5. Populate Open Search directly during Migration. Use Bulk Insertion into OpenSearch - Not Record by Record - Use DBZM for incremental production volumes.

\
