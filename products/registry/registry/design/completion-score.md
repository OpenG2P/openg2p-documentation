---
description: Register Completion Score Design Document
---

# Completion Score

### 1. Overview

This document specifies the design for calculating and tracking completion scores for registers within a registry instance. The completion score indicates the percentage of required fields filled across a register's sections.

### 2. Concepts

#### 2.1 Register Structure

A **Register** consists of multiple **Sections**:

* Sections belong to either the main **REGISTER TABLE** or child tables
* Each Section contains multiple **Fields**
* A **LIST SECTION** is a child section containing multiple records

#### 2.2 Completion Score Calculation

**Section Score Calculation:**

* Each section has a **weightage index**
* Section Score = (Filled Fields / Total Fields) × Section Weightage
* For list sections: Total Fields = (fields per record) × (number of records)

**Register Completion Score:**

* Sum of all section scores
* Ideal Score = Sum of all section weightages
* Actual Score = Sum of all computed section scores

**Example:**

* 2 sections with weightages 10 and 15
* Ideal Score = 25
* Actual Score = partial sum based on filled fields

#### 2.3 List Section Scoring

For a list section with multiple records:

* Total Fields = (fields per record) × (number of records)
* Filled Fields = sum of filled fields across all records
* Section Score = (Filled Fields / Total Fields) × Section Weightage

**Example:**

* 4 fields per record, 2 records total
* Record 1: 4/4 fields filled
* Record 2: 2/4 fields filled
* Section Score = \[(4+2)/(4×2)] × Weightage = \[6/8] × Weightage

### 3. Constraints

1. **Parent Register Exclusion:** PARENT-REGISTER sections are excluded from completion score calculations
2. **List Section Calculation:** For list sections, calculate total available fields as (fields per record × number of records)

### 4. Data Models

#### 4.1 New Model: g2p\_register\_section\_completion\_score

<table><thead><tr><th width="317.52386474609375">Field</th><th>Type</th><th>Description</th></tr></thead><tbody><tr><td>register_id</td><td>Integer</td><td>Identifies the register</td></tr><tr><td>internal_record_id</td><td>String</td><td>Unique record identifier within register</td></tr><tr><td>section_id</td><td>Integer</td><td>Identifies the section</td></tr><tr><td>computed_section_completion_score</td><td>Float</td><td>Calculated section score</td></tr><tr><td>computed_timestamp</td><td>DateTime</td><td>Timestamp of calculation</td></tr></tbody></table>

#### 4.2 Enhanced Model: g2p\_register\_section

**New Attribute:**

* `section_weightage` (Float) - Weight assigned to this section in completion calculation

#### 4.3 Enhanced Model: g2p\_register\_definition

**New Attribute:**

* `completion_score_required` (Boolean) - Indicates if completion score tracking is required

### 5. Processing Architecture

#### 5.1 Trigger Events

Completion score computation is triggered when:

* A new REGISTER-RECORD is created (via approval or INTAKE\_FORM)
* A REGISTER-RECORD is updated (via approved CHANGE\_REQUEST)
* Condition: `g2p_register_definition.completion_score_required = TRUE`

#### 5.2 Queue Model: g2p\_completion\_score\_computation\_queue

| Field                         | Type     | Description         |
| ----------------------------- | -------- | ------------------- |
| internal\_record\_id          | String   | Record to compute   |
| register\_id                  | Integer  | Associated register |
| section\_id                   | Integer  | Section to compute  |
| compute\_status               | String   | Processing status   |
| compute\_processed\_timestamp | DateTime | Last processed time |
| compute\_number\_of\_attempts | Integer  | Retry counter       |

#### 5.3 Processing Pipeline

1. **Celery Beat Producer:** Retrieves items from queue
2. **Celery Worker:**
   * Computes section completion scores
   * Inserts/updates `g2p_register_section_completion_score`
   * Updates queue status and timestamp

### 6. API Specifications

#### 6.1 Configuration APIs (Staff API)

**Register Section Weightage Configuration**

* **Endpoint:** Configure section weightage values
* **Resource:** `g2p_register_section`

**Register Definition Configuration**

* **Endpoint:** Set completion\_score\_required flag
* **Resource:** `g2p_register_definition`

#### 6.2 Metadata APIs

**get\_ideal\_completion\_score\_for\_register**

* **Input:** `register_id`
* **Output:** Sum of all section weightages for the register

**get\_ideal\_completion\_score\_for\_section**

* **Input:** `section_id`
* **Output:** Weightage value of the section

#### 6.3 Data APIs

**get\_computed\_completion\_score\_for\_section**

* **Input:** `internal_record_id`, `register_id`
* **Output:** List of section scores with computed values

**get\_computed\_completion\_score\_for\_record**

* **Input:** `internal_record_id`, `register_id`
* **Output:** Total completion score for the record

### 7. User Interface

#### 7.1 UI Components

**WIDGET\_COMPLETION\_SCORE\_SECTION**

* Displays section-level progress
* Format: `7.5 / 10` (computed score / ideal score)
* Placement: Within relevant sections in UI schemas

**WIDGET\_COMPLETION\_SCORE\_REGISTER**

* Displays register-level progress
* Format: `56.5 / 80` (computed score / ideal score)
* Placement: Header section of register view

#### 7.2 Data Flow

1. UI calls Metadata APIs to retrieve ideal scores
2. UI calls Data APIs to retrieve computed scores
3. Widgets render progress indicators for sections and registers
4. Display format: `Computed Score / Ideal Score`

### 8. Implementation Summary

| Component        | Technology           | Purpose                     |
| ---------------- | -------------------- | --------------------------- |
| Queue Management | Django Model         | Track pending computations  |
| Task Processing  | Celery Beat + Worker | Async score computation     |
| Data Retrieval   | REST APIs            | Metadata and data access    |
| UI Rendering     | Widgets              | Display completion progress |
