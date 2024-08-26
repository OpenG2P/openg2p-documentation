# OpenG2P FastAPI Auth

## Introduction

This is a Python package that provides additional support, particularly Authentication and Authorization, to the [OpenG2P FastAPI Common](openg2p-fastapi-common.md) Library. This page describes different concepts within the library and instructions on how to use it.

## Technical Concepts

This package/library contains API Authentication and Authorization helpers for Rest API Services that are bootstrapped by the [OpenG2P FastAPI Common](openg2p-fastapi-common.md) Library. Details:

<table><thead><tr><th width="184">Name</th><th>Description</th></tr></thead><tbody><tr><td>Login Provider</td><td><ul><li>LoginProvider is an object that helps the user login in the current web app using an external Authorization System.</li><li><p>LoginProviders is a database table where different types of login providers can be configured.</p><ul><li>This module also exposes APIs to query the LoginProviders configured on DB.</li></ul></li><li><p>The <code>type</code> column of LoginProviders can be set to one of the following values.</p><ul><li><code>oauth2_auth_code</code> - If the type is set to this, then the LoginProvider is an OIDC Provider, that supports the basic <code>auth_code</code> flow. (With PKCE being optional)</li></ul></li><li>The <code>authorization_parameters</code> are the parameters required by this LoginProvider </li></ul></td></tr><tr><td>AuthController</td><td>TODO</td></tr><tr><td>OauthController</td><td>TODO</td></tr><tr><td>JwtBearerAuth</td><td>TODO</td></tr><tr><td>ApiAuthSettings</td><td>TODO</td></tr></tbody></table>

## Installation

This section describes instructions for installing the package. Primarily intended for developers using this module.

* Install python3 for your environment.
*   Set up a virtualenv in your project directory. Using:

    ```bash
    python3 -n venv .venv
    source .venv/bin/activate
    ```
* Clone [openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common).
*   Then Install the common package using pip:

    ```bash
    pip install -e <path-to-cloned-common-repo>/openg2p-fastapi-auth
    ```

## Usage Guide

This section describes instructions for using the package/library. Primarily intended for developers using this module to build their own projects.

TODO

### Configuration

TODO

## Source Code

* OpenG2P FastAPI Common Module Source Code - [https://github.com/OpenG2P/openg2p-fastapi-common/tree/develop/openg2p-fastapi-auth](https://github.com/OpenG2P/openg2p-fastapi-common/tree/develop/openg2p-fastapi-auth)
