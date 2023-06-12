# Eligibility

## Introduction

A given program will have certain criteria to consider individuals eligible for that program. Assuming that eligibility can be expressed unambiguously based on an individual's demographic data, a program manager can easily run the criteria on the registry to create a beneficiary list using domain filters and eligibility plugins.

## Eligibility definition

Program eligibility could be defined as simple filters on the data collected for individuals (residing in the registry) or could be more sophisticated like [Proxy Means Test.](https://olc.worldbank.org/sites/default/files/1.pdf) Default filters and plugins are provided that would meet most of the eligibility definitions. For complex eligibility criteria, custom plugins can be written and added to the [Eligibility Manager](broken-reference).&#x20;

## Eligibility Manager

In OpenG2P, Eligibility Manager is a separate software module where the eligibility of a program is configured. If custom plugins are written, they are added to the Eligibility Manager.

Note that one eligibility manager can be associated with only one program. Each program should have its own eligibility manager created and configured.

## Domain filters

## Custom eligibility plugins

Example: Proxy Means Test
