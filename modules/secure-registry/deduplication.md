# Deduplication

## Introduction

Deduplication refers to the process of removing duplicate entries in the registry and merging all the parameters associated with an individual or a group into a single record.

## Deduplication of individuals

Individuals are deduplicated by any of the below methods or a combination of these:

### Unique foundational ID

If a country has issued unique foundational IDs (like [MOSIP](https://mosip.io)) then deduplication is trivial -- there is only one record associated with an ID. For privacy, the foundational ID itself is not stored in the registry. Instead a ['token'](https://docs.mosip.io/1.2.0/id-lifecycle-management/identifiers#token-id) or [virtual ID](https://docs.mosip.io/1.2.0/id-lifecycle-management/identifiers#vid) associated with the ID is stored.

### Foundational IDs

If various foundations IDs like driving license, tax number, student ID etc. are accepted while registration, then deduplication across the IDs is somewhat challenging if a link between these is not already established and available to OpenG2P system. In this case, heuristics are applied on demographic data to detect potential duplicates.

### [No ID](#user-content-fn-1)[^1]

In cases registrants were onboarded without any ID, the deduplication is performed using heuristics on demographic data.

## Deduplication of groups

The deduplication method for groups is context dependent. For eg. if a group of individuals register&#x20;

## Manual adjudication

[^1]: Example annotation
