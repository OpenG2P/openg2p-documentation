# 📄 Documents : S3 Bucket Integration

## Introduction

All the documents attached by the registrant, users or vendors will be saved in S3 bucket. This S3 bucket integration uses `storage_backend_s3` and `storage_file` package of Odoo which is further extended to make it easier to access.

## Pre-requisites

Module

* storage\_backend\_s3&#x20;
* storage\_file&#x20;

Python libraries

* Wkhtmltopdf
* boto3<=1.15.18
* python\_slugify

## Why MinIO not AWS Bucket?

Amazon limits buckets to \~100/ account, where each bucket has a globally unique DNS where MinIO does not have bucket limits.

## Configuration Parameters

**Backend Type:** Amazon S3

**Served By:** Odoo

**Is Public:** True

**Base Url:**&#x20;

**Filename Strategy:** Name and ID

**Directory Path:**&#x20;

**Url Include Directory Path:**&#x20;

**AWS Host:**&#x20;

**Access Key ID:** admin

**Secret Access Key:** $MORESECRET

**Bucket:** your-bucket-name

**Aws Cache Control:**

**Aws File Acl:**

**Region:**

