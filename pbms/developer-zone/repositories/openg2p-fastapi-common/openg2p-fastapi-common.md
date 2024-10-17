# OpenG2P FastAPI Common

## Introduction

This is a Python package that can be used as a library to bootstrap REST API services, based on [FastAPI](https://fastapi.tiangolo.com/). This page describes different concepts within the library and instructions on how to use it.

## Technical concepts

This package/library contains basic components, like Configuration helpers, Logging helpers, DB ORM helpers, Base Initializers, etc that are required to bootstrap a basic service built using Python and FastAPI. A detailed description is given below.

<table><thead><tr><th width="234">Name</th><th>Description</th></tr></thead><tbody><tr><td>Component</td><td><ul><li>A Component is an object that gets stored in a global registry (called Component Registry) when initialized.</li><li>Components are usually only initialized once mostly inside an Initializer class. Once initialized in Initializer, they can be obtained using the class method; <code>&#x3C;ComponentClass>.get_component()</code>.</li><li>A <code>name</code> (optional) can be given to instances of Components so that they can be retrieved using that name if there are multiple instances of a Component. <code>&#x3C;ComponentClass>.get_component("mycomp")</code>.</li><li><code>BaseComponent</code> is the base Class for Components.</li></ul></td></tr><tr><td>Service</td><td><ul><li>A Service is also a Component that usually contains some logic that is executed inside a Controller.</li><li>Use <code>&#x3C;ServiceClass>.get_component()</code> to retrieve a service.</li><li><code>BaseService</code> is the base Class for Services.</li><li>Service is technically the same as Component. Prefer Service over Component when defining new.</li></ul></td></tr><tr><td>Controller</td><td><ul><li>A Controller is also a Component, that contains a <a href="https://fastapi.tiangolo.com/reference/apirouter/">FastAPI APIRouter</a> and API Routes inside it. The APIRouter and APIs get initialized when the Controller is initialized.</li><li>In the init method of a Controller, the API Routes need to be manually added.</li><li>Controllers also have a <code>post_init</code> method that adds the APIRouter and APIs into a global <a href="https://fastapi.tiangolo.com/reference/fastapi/">FastAPI App</a>. So inside an Initializer, the <code>post_init</code> method can be called immediately after the Controller is initialized.</li><li>Use <code>&#x3C;ControllerClass>.get_component()</code> to retrieve a Controller.</li><li><code>BaseController</code> is the base Class for Controllers.</li></ul></td></tr><tr><td>Settings</td><td><ul><li>Settings, based on Pydantic's BaseSettings, establishes configuration options.</li><li>Configuration Parameters defined inside Settings can be loaded through Env variables / <code>.env</code> file.</li><li><code>Settings</code> Class in <code>config</code> can be used as the base class by other Settings classes to inherit.</li></ul></td></tr><tr><td>BaseORMModel</td><td><ul><li>BaseORMModel is an SQLAlchemy ORM Model, that can be used as a base class for other ORM Classes to inherit.</li></ul></td></tr><tr><td>BaseExceptionHandler</td><td><ul><li>BaseExceptionHandler is an Exception Handler Implementation that uses FastAPI Exception Handler at the base and handles extra exceptions defined in this module, mainly <code>BaseAppException</code>.</li><li>This can also be extended to further handle custom Exceptions when defined.</li></ul></td></tr><tr><td>Initializer</td><td><ul><li>Initializer is a class that initializes all the components, services, controllers, configs, loggers, etc along with any additional Components of a particular Python Package/Module.</li><li>The Components have to be individually initialized inside the init method of an Initializer.</li></ul></td></tr></tbody></table>

## Installation

This section describes instructions for installing the package. Primarily intended for developers using this module to build their own projects.

* Install python3 for your environment.
*   Set up a virtualenv in your project directory. Using:

    ```bash
    python3 -n venv .venv
    source .venv/bin/activate
    ```
* Clone [openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common).
*   Then Install the common package using pip:

    ```bash
    pip install -e <path-to-cloned-common-repo>/openg2p-fastapi-common
    ```

## Recommended project structure

* Follow the instructions here [https://github.com/OpenG2P/openg2p-fastapi-template](https://github.com/OpenG2P/openg2p-fastapi-template), to set up a repository with the given template and folder structure.

## Usage guide

This section describes instructions for using the package/library. Primarily intended for developers using this module to build their own projects.

### App.py

* The `app.py` file in the project acts as the main file which initializes all the components of the project. It should contain an `Initializer`.
*   Initialize the Components (like Services, Controllers, etc.) inside the `initialize` method of the `Initializer`. Example

    ```python
    # ruff: noqa: E402

    from .config import Settings

    _config = Settings.get_config()

    from openg2p_fastapi_common.app import Initializer

    from .services.ping_service import PingService
    from .controllers.ping_controller import PingController


    class PingInitializer(Initializer):
        def initialize(self):
            PingService()
            PingController().post_init()
    ```
* Note: If the Initializer is only supposed to be used by external modules to inherit/extend/use. Then do not run `super().initialize()` inside the `initialize` method. If the Initializer is the main Initializer that sets up the FastAPI apps etc then run `super().initialize()` inside the `initialize` method.
* Note: Due to a limitation in the way the config is set up, the `Settings.get_config()` needs to be put at the beginning of the app.py (only applies to app.py), before importing other Initializers. If your Linters/Code Formatters are throwing up an E402 error, ignore the error at the beginning of app.py. Check the above example.

### Configuration

*   If you are using the template given above, use the config file present in the `src` folder of your Python package. If not, create a `config.py` file in your project that looks like this.

    ```python
    from openg2p_fastapi_common.config import Settings
    from pydantic_settings import SettingsConfigDict


    class Settings(Settings):
        model_config = SettingsConfigDict(
            env_prefix="myproject_", env_file=".env", extra="allow"
        )
    ```
* This `Settings` class derives from [`pydantic_settings` 's `BaseSettings`](https://docs.pydantic.dev/latest/concepts/pydantic\_settings/).
*   To define configuration parameters for your project, add the properties to the above Settings class defined in `config.py`. Example

    ```python
    class Settings(AuthSettings, Settings):
        ...
        m_param_a : str = "default_value"
        m_param_b : int = 12
    ```
*   The parameters defined here can be loaded through environment variables or `.env` file. The environment variables can be case insensitive. For example

    ```bash
    myproject_m_param_a="loaded_value"
    MYPROEJCT_M_PARAM_B="10456"
    ```

    * The environment variable prefix, `myproject_` in the above example, can be configured under `model_config` of Settings class, under `env_prefix`.
*   To use this config in other components of your project like models/controllers/services, etc. use the `get_config` class method of the above Settings class. Example inside a controller file

    ```python
    ...
    from .config import Settings

    _config = Settings.get_config()


    class PingController(BaseController):
        ...
        
        def get_ping(self):
            ...
            print(_config.m_param_a)
            ...
    ```
* Refer to [Additional Configuration](openg2p-fastapi-common.md#additional-configuration) to see the configuration properties already available in the base `Settings` class.

### Controllers

* To add more APIs to your project, create controllers in the `controllers` directory.
*   Add each API route using the `add_api_route` method of the router. Example `ping_controller.py`.

    ```python
    from openg2p_fastapi_common.controller import BaseController

    from .config import Settings

    _config = Settings.get_config()


    class PingController(BaseController):
        def __init__(self, name="", **kwargs):
            super().__init__(name, **kwargs)

            self.router.tags += ["ping"]

            self.router.add_api_route(
                "/ping",
                self.get_ping,
                methods=["GET"],
            )

        async def get_ping(self):
            return "pong"
    ```
*   Initialize the Controller, preferably in an Initializer like given [above](openg2p-fastapi-common.md#app.py). It is important to run the `post_init` method of the Controller after initializing it since that will add the API Router of the Controller to the FastAPI App. Example

    ```python
    ...
    from .controllers.ping_controller import PingController

    class PingInitializer(Initializer):
        def __init__(self):
            ...
            PingController().post_init()
    ```
* A Controller will automatically initialize Response models for the APIs for the following HTTP Codes: 401, 403, 404, and 500 (with the `ErrorListResponse` response model defined in this module). These can be changed/updated accordingly.

### Services

* Create Services in the `services` directory similar to a Controller.
* Initialize the Service in the Initializer like given [above](openg2p-fastapi-common.md#app.py).
*   Example

    ```python
    from openg2p_fastapi_common.service import BaseService

    from .config import Settings

    _config = Settings.get_config()


    class PingService(BaseService):
        def ping(self, pong: str):
            return _config.m_param_a + " " + pong
    ```

### Components

* To retrieve an instance of a Component (Service, Controller, etc) use `Component.get_component()`.&#x20;
*   Example in `PingController` if you want to retrieve the `PingService`.

    ```python
    ...
    from .services.ping_service import PingService
    ...


    class PingController(BaseController):
        def __init__(self, name="", **kwargs):
            super().__init__(name, **kwargs)
            ...

            self.ping_service = PingService.get_component()
        
        async def get_ping(self):
            return self.ping_service.ping("pong")
    ```

### Logging

* Get the logger using `logging.getLogger(__name__)` . This logger initializes JSON logging, using [json-logging](https://github.com/bobbui/json-logging-python).
* This can be modified using the `init_logger` method of an Initializer.

### Models

* Define [Pydantic Models](https://docs.pydantic.dev/latest/concepts/models/) and ORM Models (based on [SQLAlcehmy 2.0 ORM](https://docs.sqlalchemy.org/en/20/orm/)) inside the `models` directory.
* Use `BaseORMModel` as the base class for your ORM Model.
  * Use `BaseORMModelWithID` as the base class, to automatically add `id` and `active` fields to the ORM class, along with quick helper classmethods to get an object using id. Example `<MyORMModel>.get_by_id(id)` .
  * Use `BaseORMModelWithTimes` as the base class, to automatically add `created_at` and `updated_at` along with features of `BaseORMModelWithID`.
*   This module also uses the [AsyncIO Extension of SQLAlchemy 2.0 ORM](https://docs.sqlalchemy.org/en/20/orm/extensions/asyncio.html#synopsis-orm). Follow the link to understand how to use SQLAlchemy and async conventions to interact with the database. Example:&#x20;

    ```python
    from openg2p_fastapi_common.context import dbengine
    from openg2p_fastapi_common.models import BaseORMModelWithTimes
    from sqlalchemy.ext.asyncio import async_sessionmaker
    from sqlalchemy.orm import Mapped, mapped_column
    from sqlalchemy import String, select

    class MyORMModel(BaseORMModelWithTimes):
        name: Mapped[str] = mapped_column(String())
        
        @classmethod
        def get_by_name(cls, name: str):
            response = []
            async_session_maker = async_sessionmaker(dbengine.get())
            async with async_session_maker() as session:
                stmt = select(cls).where(cls.name==name).order_by(cls.id.asc())
                result = await session.execute(stmt)
                response = list(result.scalars())
            return response
    ```

### Exceptions

The following Exceptions are defined by this module. When these exceptions are raised in code, they are caught and handled by BaseExceptionHandler.

The HTTP Response Payload looks like this when the following exceptions are raised. (The HTTP Response Status code is defined according to the Exception).&#x20;

```json
{
    "errors": [
        {
            "code": "<error_code from Exception>",
            "message": "<error_message from Exception>",
        }
    ]
}
```

<table><thead><tr><th width="216">Exception</th><th>Description</th></tr></thead><tbody><tr><td>UnauthorizedError</td><td><p>Raise this to return <code>401 Unauthorized</code> HTTP response.<br>UnauthorizedError derives from BaseAppException.</p><p>Default <code>error_code</code> is <code>G2P-AUT-401</code>.</p><p>Default <code>error_message</code> is <code>Unauthorized</code>.</p><p>Default <code>http_status_code</code> is <code>401</code>.</p><pre class="language-python"><code class="lang-python">from openg2p_fastapi_common.errors.http_errors import UnauthorizedError
</code></pre></td></tr><tr><td>ForbiddenError</td><td><p>Raise this to return <code>403 Forbidden</code> HTTP response.<br>ForbiddenError derives from BaseAppException.</p><p>Default <code>error_code</code> is <code>G2P-AUT-403</code>.</p><p>Default <code>error_message</code> is <code>Forbidden</code>.</p><p>Default <code>http_status_code</code> is <code>403</code>.</p><pre class="language-python"><code class="lang-python">from openg2p_fastapi_common.errors.http_errors import ForbiddenError
</code></pre></td></tr><tr><td>BadRequestError</td><td><p>Raise this to return <code>400 Bad Request</code> HTTP response.<br>BadRequestError derives from BaseAppException.</p><p>Default <code>error_code</code> is <code>G2P-REQ-400</code>.</p><p>Default <code>error_message</code> is <code>Bad Request</code>.</p><p>Default <code>http_status_code</code> is <code>400</code>.</p><pre class="language-python"><code class="lang-python">from openg2p_fastapi_common.errors.http_errors import BadRequestError
</code></pre></td></tr><tr><td>NotFoundError</td><td><p>Raise this to return <code>404 Not Found</code> HTTP response.<br>BadRequestError derives from BaseAppException.</p><p>Default <code>error_code</code> is <code>G2P-REQ-404</code>.</p><p>Default <code>error_message</code> is <code>Not Found</code>.</p><p>Default <code>http_status_code</code> is <code>404</code>.</p><pre class="language-python"><code class="lang-python">from openg2p_fastapi_common.errors.http_errors import NotFoundError
</code></pre></td></tr><tr><td>InternalServerError</td><td><p>Raise this to return <code>500 Internal Server Error</code> HTTP response.<br>InternalServerError derives from BaseAppException.</p><p>Default <code>error_code</code> is <code>G2P-REQ-500</code>.</p><p>Default <code>error_message</code> is <code>Internal Server Error</code>.</p><p>Default <code>http_status_code</code> is <code>500</code>.</p><pre class="language-python"><code class="lang-python">from openg2p_fastapi_common.errors.http_errors import InternalServerError
</code></pre></td></tr><tr><td>BaseAppException</td><td><p>BaseAppException is the parent for the custom exceptions. It takes an <code>error_code</code> , <code>error_message</code> and <code>http_status_code</code> arguments. Default <code>http_status_code</code> is 500. If this is manually raised in code, an error response will be returned on the API Call with the given error code, and error message, and  HTTP Status will be set to the given status code. </p><pre class="language-python"><code class="lang-python">from openg2p_fastapi_common.errors import BaseAppException
</code></pre></td></tr></tbody></table>

### Additional Configuration

The following configuration properties are already present in the base `Settings` class mentioned in [Configuration Guide](openg2p-fastapi-common.md#configuration).&#x20;

The following properties can also be set through the environment variables, but the `env_prefix` configured in your project's config `Settings` will have to be used, as mentioned [above](openg2p-fastapi-common.md#configuration). Example `myproject_logging_level=DEBUG` .

<table><thead><tr><th width="226">Property</th><th width="334">Description</th><th>Default Value</th></tr></thead><tbody><tr><td>host</td><td>Host/IP to which the HTTP server should bind to.</td><td>0.0.0.0</td></tr><tr><td>port</td><td>Port on which the server HTTP should run.</td><td>8000</td></tr><tr><td>logging_level</td><td>Logging Level. Available values <code>DEBUG</code>, <code>INFO</code>, <code>WARN</code>, <code>ERROR</code> and <code>CRITICAL</code>.</td><td>INFO</td></tr><tr><td>logging_file_name</td><td>Path to a file where the log should should be stored. If left empty, no file logging. Stdout logging is enabled by default.</td><td></td></tr><tr><td>openapi_title</td><td>Title in OpenAPI Definition. This is the title field in <code>openapi.json</code> generated by FastAPI. Hence also present on Swagger and API Docs.</td><td>Common</td></tr><tr><td>openapi_description</td><td>Description in OpenAPI</td><td></td></tr><tr><td>openapi_version</td><td>Version in OpenAPI</td><td>1.0.0</td></tr><tr><td>openapi_contact_url</td><td>Contact URL in OpenAPI</td><td>https://www.openg2p.org/</td></tr><tr><td>openapi_contact_email</td><td>Contact Email in OpenAPI</td><td>info@openg2p.org</td></tr><tr><td>openapi_license_name</td><td>License Name in OpenAPI</td><td>Mozilla Public License 2.0</td></tr><tr><td>openapi_license_url</td><td>License URL in OpenAPI</td><td>https://www.mozilla.org/en-US/MPL/2.0/</td></tr><tr><td>db_datasource</td><td><p>This is the property used by SQLALchemy for DB datasource. If left empty, this will be constructed, using the following db properties, like the following: </p><pre><code>f"{db_driver}://{db_username}:{db_password}@{db_hostname}:{db_port}/{db_dbname}"
</code></pre></td><td></td></tr><tr><td>db_driver</td><td>Driver to use while connecting to Database. Configure this based on the Database being used. If using PostgreSQL, leave it as default.</td><td>postgresql+asyncpg</td></tr><tr><td>db_hostname</td><td>Database Host/IP</td><td>localhost</td></tr><tr><td>db_port</td><td>Database Port</td><td>5432</td></tr><tr><td>db_dbname</td><td>Database Name</td><td></td></tr><tr><td>db_username</td><td>Database Authentication Username</td><td></td></tr><tr><td>db_password</td><td>Database Authentication Password</td><td></td></tr><tr><td>db_logging</td><td>Database Logging. If true, all the database operations being made will be put out in the server logs. Useful while debugging.</td><td>false</td></tr></tbody></table>

## Source code

* OpenG2P FastAPI Common Module Source Code - [https://github.com/OpenG2P/openg2p-fastapi-common/tree/develop/openg2p-fastapi-common](https://github.com/OpenG2P/openg2p-fastapi-common/tree/develop/openg2p-fastapi-common)
