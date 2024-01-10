# PostgreSQL Server

## Introduction

This guide provides instructions to install PostgreSQL Server on the Kubernetes cluster. However, if you already have PostgresSQL server installed, or are using Cloud hosted Postgres, then you may skip the server installation. The instructions to initialize OpenG2P component databases are provided as part of the component installation instructions.

## Databases

Module/component-wise listing of databases is given below

| Module/Component         | Database Name  |
| ------------------------ | -------------- |
| PBMS                     | `openg2pdb`    |
| Keycloak                 | `keycloakdb`   |
| ODK                      | `odkdb`        |
| SPAR                     | `spardb`       |
| G2P Cash Transfer Bridge | `gctbdb`       |
| MOSIP Key Manager        | `mosip_keymgr` |

