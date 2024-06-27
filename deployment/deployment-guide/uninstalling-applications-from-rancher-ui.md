---
description: >-
  This document provides instructions on uninstalling applications from Rancher
  UI.
---

# Uninstalling Applications from Rancher UI

## Procedure&#x20;

The table below details the process of uninstalling applications from Rancher UI.

<table><thead><tr><th width="228">Process</th><th>Method</th></tr></thead><tbody><tr><td><strong>Delete the application</strong></td><td><p></p><ul><li>Navigate to the Rancher UI and click the <em><strong>Apps</strong></em> tab from the menu.</li><li>Select the application you want to delete.</li></ul><p>The application will be deleted from the <em><strong>Pods</strong></em> and <em><strong>Deployments</strong></em> sections</p></td></tr><tr><td><strong>Verify deletion</strong></td><td><p></p><ul><li>Use the filter to search for the name of the deleted application.</li><li>If the application is deleted successfully, you will not find the application in the <em><strong>Pods</strong></em> and <em><strong>Deployments</strong></em> sections.</li></ul></td></tr><tr><td><strong>Clear completed jobs</strong></td><td><ul><li>Remove all the completed jobs of the deleted applications from the <em><strong>Pods</strong></em> and <em><strong>Jobs</strong></em> sections.</li></ul></td></tr><tr><td><strong>Delete PVCs</strong></td><td><ul><li>Navigate to the <em><strong>PVC</strong></em> (Persistent Volume Claims) tab.</li><li>Filter by the application name and delete all associated PVCs.</li></ul></td></tr><tr><td><strong>Confirm PVC deletion and delete PVs</strong></td><td><p></p><ul><li>Ensure all PVCs are deleted for the deleted application.</li><li>Navigate to the <em><strong>PV</strong></em> (Persistent Volumes) section and delete any PVs that are in the "Released" state.</li></ul></td></tr><tr><td><strong>Optional - Delete PVCs from NFS</strong></td><td><ul><li>If necessary, you can delete the PVCs from the NFS storage.</li></ul></td></tr></tbody></table>
