# Packages

## Module packages

Each OpenG2P module—such as Social Registry, PBMS, SPAR, and G2P Bridge—is delivered as a deployable package. This package consists of multiple components and is provided as a Helm chart that includes several sub-charts. See the packaging hierarchy outlined below:

<figure><img src="../.gitbook/assets/module-packaging.jpg" alt=""><figcaption></figcaption></figure>



## Package versioning

The version of the Helm Chart of the module is considered as the package version of the module.  For example, Social Registry version 1.5.0 refers to the **Helm chart of the entire package.** As mentioned above, each package contains several components that may have their own versions.  Refer to [versioning conventions](versioning.md).

