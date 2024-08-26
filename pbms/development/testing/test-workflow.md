# Test Workflow



## Overview

The "Test Workflow" automates the sanity test for every new push or pull on the specified branch and generates the report and deploys the report on GitHub pages. This workflow is designed to ensure a streamlined and consistent testing pipeline.  which further can be integrated with the build and deploy workflow to complete the CI/CD pipeline.&#x20;

## Purpose

Here are the primary objectives and benefits of using this workflow:

* Ensures that the codebase is continuously integrated, built, and tested whenever changes are pushed to the 'develop' branch or when pull requests are created or updated.
* Executes a series of automated tests, including sanity tests, using Maven. This ensures that the Java project functions correctly and does not introduce new bugs with each code change.
* Sends Slack notifications to designated channels on both successful and failed workflow runs.
* Installs and uses Allure to generate detailed test reports. The generated Allure report provides insights into test results which helps understand the quality of the codebase.
* Deploys the Allure report to GitHub Pages, making it accessible and shareable.
* Provides the flexibility for the teams to manually trigger the workflow when needed, offering control over when certain processes are executed.

## Functionality

The workflow performs the following key tasks:

### **Build and test**

* Sets up the latest version of Ubuntu as the execution environment.
* Configures Java Development Kit (JDK) version 17.
* Caches Maven dependencies to improve build efficiency.
* Installs WireGuard and configures it for accessing specific URLs.
* Sets up Google Chrome browser and Chromedriver for hosting testing environment
* Builds the Java project using Maven, skipping tests initially.
* Runs sanity tests using the command `mvn clean test` which runs the sanity test suite.

### **Notification**

* Sends a Slack notification on successful workflow execution, providing information about the actor and commit ID.
* Sends a Slack notification on workflow failure, including details about the actor, commit ID, and the failed step.

### **Generate and deploy Allure report**

* Installs Allure to generate detailed test reports.
* Generates an Allure report for the test results.
* Deploys the generated Allure report to GitHub Pages which can be accessed for result analysis.

### How It Works

The workflow is triggered in the following ways:

* **Push to 'develop' Branch**: The workflow runs automatically when code is pushed to the 'develop' branch.
* **Pull Request to 'develop' Branch**: It also runs when a pull request is opened or updated against the 'develop' branch.
* **Manual Workflow Dispatch**: Developers or DevOps teams can manually trigger the workflow using GitHub Actions' workflow dispatch feature.

## Configuration and secrets

### Configuration file

The workflow is defined in a YAML file (`.github/workflows/ui-sanity.yml`). Developers can customize this file to adjust build and test configurations.

### Required secrets

Ensure the following secrets are configured in the GitHub repository settings:

* **SLACK\_INCOMING\_WEBHOOK**: Slack webhook URL for notifications.
* **GIT\_TOKEN**: GitHub token for deploying the Allure report to GitHub Pages.

## Considerations for Developers/DevOps

* **Dependency Versions**: The workflow uses specific versions of actions and tools (e.g., Java 17, Allure 2.18.1).&#x20;
* **WireGuard Setup**: Setup should reviewed and customized for accessing specific URLs based on project requirements.
* **GitHub Pages Deployment**: Developers need to ensure the presence of a GitHub token (`GIT_TOKEN`) with the necessary permissions for deploying the Allure report to GitHub Pages.
* **Slack Notifications**: Customize the Slack notifications as needed. Ensure the Slack webhook (`SLACK_INCOMING_WEBHOOK`) is valid and accessible.

## Future improvements

To integrate with build and deploy workflows to accomplish the complete CI/CD pipeline.
