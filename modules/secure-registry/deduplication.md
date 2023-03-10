# Deduplication

## Introduction

Deduplication refers to the process of removing duplicate entries in the registry, thus avoiding double-dipping, and merging all the demographic fields associated with an individual or a group into a single record.&#x20;

## Deduplication of individuals

Individuals are deduplicated by any of the below methods or a combination of these:

### Unique foundational ID

If a country has issued unique foundational IDs (like [MOSIP](https://mosip.io)) then deduplication is trivial -- there is only one record associated with an ID. For privacy, the foundational ID itself is not stored in the registry. Instead, a ['token'](https://docs.mosip.io/1.2.0/id-lifecycle-management/identifiers#token-id) or [virtual ID](https://docs.mosip.io/1.2.0/id-lifecycle-management/identifiers#vid) associated with the ID is stored.

### Functional IDs

If functional IDs like driver's license, tax number, student ID etc. are accepted while registration, then deduplication across IDs is somewhat challenging if a link between these is not already established and available to the OpenG2P system. In this case, heuristics are applied to demographic data to detect potential duplicates.

### No ID

In case registrants were onboarded without an ID, the deduplication is performed using heuristics on demographic data.

{% hint style="success" %}
OpenG2P is guided by the principle of **inclusion.** The system does not prevent registrations of persons who do not have an ID. This is especially applicable during emergency relief like floods, war, and other calamities.
{% endhint %}

## Deduplication of groups

Deduplication of groups refers to removing duplicate groups within a type of group like a family, or household. The deduplication method is context-dependent and is configured via rules. For example, if the same family has registered itself twice, it will be flagged as a duplicate. However, there are more complex scenarios - say, an individual appears in two different households while other members are different. Such cases will be flagged based on the configured rules.&#x20;

## Manual adjudication

Resolution of duplicates is generally done via a manual adjudication process, where an authority is visually able to inspect the data and reason for duplication. The authority can then decide whether the case is a duplicate or not based on the process set by the country/department/ministry.
