# Automation Framework

## &#x20;1. Introduction

### 1.1 Overview

The purpose of data-driven testing with Selenium automation is to enhance the efficiency, effectiveness, and coverage of your testing efforts by systematically testing your application with multiple sets of input data.

### 1.2 Purpose

Below points are the purposes for using a data-driven testing framework

1. Increased Test coverage
2. Efficiency and Reusability
3. Regression Testing
4. Validation of Input Data
5. Scalability
6. Exploratory Testing Support
7. Parameterization
8. Maintaining Test Data Separately
9. Consistency and Reproducibility
10. Compliance and Regulation Testing\


### 1.3 Technologies and Tools&#x20;

1. Selenium WebDriver - This provides a programming interface to interact with web elements and automate tasks in web applications
2. Java -&#x20;
3. Maven - This is being used as a Dependency Management tool.
4. TestNG - TestNG is used as a framework and as a reporting tool as well.
5. Log4j - It's used to log messages within software and has the ability to communicate with other services on a system.
6. Apache POI - provides stream-based processing, that is suitable for large files and requires less memory. Apache POI is able to handle both XLS and XLSX formats of spreadsheets.
7. Webdriver Manager - WebDriverManager can automatically download and manage WebDriver dependencies for different browsers such as Chrome, Firefox, Safari, and Edge.
8. ReportNG -&#x20;





## 2. Prerequisites

### 2.1 Test Framework Setup

Step 1: Set Up a Maven Project

Step 2: Add below mentioned Dependencies

* &#x20;Selenium Webdriver

```
selenium-java
```

* Apache POI

```
poi
```

```
poi-ooxml
```

```
poi-ooxml-schemas
```

```
xmlbeans
```

```
commons-collections4
```

* TestNG

```
testng
```

* Webdriver Manager

```
webdrivermanager
```

* log4j

```
log4j-api
```

```
log4j-core
```

* ReportNG

```
reportng
```



Step 3: Create Data-Driven Test Class

Step 4: Create TestNG XML File&#x20;

Step 5: Implement Data Provider

Step 6: Execute Tests



### 2.2 Test Data Preparation

* The test data file format should be XLS or XLSX.
* There should be a sheet with test data for each method and the sheet name should match the name of the method.
* Each column name of the sheet should have a unique.
* Any number of data can be passed\


## 3. Test Case Design



### 3.1 Test Scenarios

* Each Page should have its own test class and each scenario should have its own method.
* All Sanity and Regression scenarios are to be covered.
* Both scenarios can be run separately.
* Negative scenarios are also covered

### 3.2 Test Steps

* Provide both valid and invalid test data in the XLSX / XLS file
* Provide only the required number of test data to avoid a longer run time.

\


## 4. Data-Driven Testing Implementation

### 4.1 Test Data Loading

*   XLX or XLSX files should be stored in &#x20;

    ```
    user.dir + \src\main\resources\testdata
    ```


* Mapping between the `ReadXLSData` class and the `testdata` should be done
* Column Names of the sheets to be passed in the methods signature placeholder as parameters to fetch the data from the data provider.

### 4.2 Test Execution

* Set up test Environment
* Create Test class
* Implement data provider
* Run test classes
* Analyze test results &#x20;



## 5. Reporting and Logging

### 5.1 Test Result Reporting

* TestNG is used as a report provider
* Every class name is to be mentioned in the `testng.xml` file to be a part of a report
* Should be able to generate HTML emailable report by running the `testng.xm`l file.
* An `emailable-report.html` and `testing-failed.xml` reports to be generated in the test-output file



### 5.2 Logging

* log4j has been used as a logging tool
* This will provide the log for each test method that fails during the test suite execution
* Finding the exact error in the test suite execution will be easy

\


## 6. Test Environment Configuration

### 6.1 Driver Configuration

* Driver configuration will be handled by the `Webdriver Manager` .
* Webdriver Manager will manage the download, setup, and maintenance of the drivers required by Selenium WebDriver.

### 6.2 Test Environment Parameters

* Users need to provide the browser name (Case insensitive) and URL of the environment in `configfiles > config.properties.`



## 7. Maintenance and Updates

### 7.1 Test Data Updates

1. Identify the need for updates, considering application changes, data quality, and new scenarios.
2. Update data in its source (e.g., Excel, database) to reflect current requirements and formats.
3. Ensure data validity by including boundary and edge cases.
4. Consider versioning data for tracking changes over time.

### 7.2 Codebase Maintenance



\


9.Conclusion

9.1 Summary

9.2 Future Improvements

\
