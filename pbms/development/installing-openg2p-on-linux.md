# Installing On Linux

## Description

Developers can run the entire OpenG2P package on their machines. The guide here provides steps to install OpenG2P on a laptop/desktop running Linux.

## Prerequisites

* A Linux server
* Python3
* Git
* PostgreSQL
* [Odoo 15.0](https://www.odoo.com/documentation/15.0/administration/install/install.html#installing-odoo)

## Installation of Odoo

#### 1. Update system packages

* Log in to your Linux server using SSH and update the package list and upgrade the existing packages:

```bash
sudo apt update
sudo apt upgrade -y
```

#### 2. Install dependencies

* Odoo requires several dependencies to function correctly. Install them using the following commands:

```bash
sudo apt install -y python3-pip python3-dev build-essential libxml2-dev libxslt1-dev libevent-dev libsasl2-dev libldap2-dev libpq-dev libjpeg-dev zlib1g-dev libfreetype6-dev liblcms2-dev libwebp-dev libopenjp2-7-dev libtiff5-dev libffi-dev nodejs npm
```

#### 3. Create Odoo user

*   It is recommended to create a separate system user to run Odoo for security purposes. Create the user with the following command:

    ```bash
    sudo adduser --system --home=/opt/odoo --group odoo
    ```

#### 4. Install and Configure PostgreSQL

*   Install PostgreSQL server and create a new database user for Odoo:

    ```bash
    sudo apt install -y postgresql
    sudo su - postgres
    createuser --createdb --username postgres --no-createrole --no-superuser --pwprompt odoo_user
    exit
    ```

#### 5. Install Wkhtmltopdf <a href="#docs-internal-guid-f8d8e15e-7fff-3872-8a9f-bfbb05735977" id="docs-internal-guid-f8d8e15e-7fff-3872-8a9f-bfbb05735977"></a>

*   Odoo supports printing reports as PDF files. Wkhtmltopdf helps to generate PDF reports from HTML data format. Moreover, the Qweb template reports are converted to HTML format by the report engine and Wkhtmltopdf will produce the PDF report:

    ```bash
    sudo wget https://github.com/wkhtmltopdf/wkhtmltopdf/releases/download/0.12.5/wkhtmltox_0.12.5-1.bionic_amd64.deb
    sudo dpkg -i wkhtmltox_0.12.5-1.bionic_amd64.deb
    sudo apt install -f
    ```

#### 6. Install Odoo

*   Clone the Odoo 15 repository from the official GitHub repository:

    ```bash
    sudo git clone https://github.com/odoo/odoo.git -b 15.0 /opt/odoo/odoo15
    ```

{% hint style="danger" %}
Cloning the odoo15 repo takes time because of the large file.
{% endhint %}

*   Make a new Odoo Python virtual environment:

    ```bash
    cd /opt/odoo
    python3 -m venv odoo-venv
    ```
*   Turn on the virtual environment:

    ```bash
    source odoo-venv/bin/activate
    ```
*   Switch to the Odoo 15 directory and install the required Python libraries:

    ```bash
    sudo chown -R <odoo_user>: /opt/odoo/odoo15
    cd /opt/odoo/odoo15
    pip3 install wheel
    pip3 install -r requirements.txt
    ```

#### 7. Configure Odoo

* Edit the configuration file `/opt/odoo/odoo15/debian/odoo.conf` and set the appropriate values for the following parameters:

```
sudo nano /opt/odoo/odoo15/debian/odoo.conf
```

```
[options]
addons_path = /opt/odoo/odoo15/addons,/opt/odoo/odoo15/custom-addons
admin_passwd = strong_admin_password
db_host = localhost
db_port = 5432
db_user = odoo_user
db_password = your_database_password
```

* Inside the customs addons directories, place the relevant project module and custom third-party modules.

#### 8. Start Odoo

*   Start the Odoo server using the following command:

    ```bash
    cd /opt/odoo/odoo15
    ./odoo-bin -c debian/odoo.conf
    ```

## Installation of OpenG2P package

1. Create a `custom-addons` folder inside the `odoo15` folder to keep all the extra modules.
2.  Clone all the [OpenG2P modules](repositories/):

    ```bash
    git clone <repo_url>
    ```
3.  Install the required Python libraries for all the custom addons:

    ```bash
    cd /opt/odoo/custom-addons/<module_directory>
    pip3 install -r requirements.txt
    ```
4. Add addons directory path to the _odoo.conf_ file in **addons\_path** parameter, mentioned in [point 7](installing-openg2p-on-linux.md#id-7.-configure-odoo).
