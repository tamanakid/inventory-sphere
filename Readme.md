# InventorySphere - API repository


The following repository provides the API implementation for InventorySphere Inventory Management platform's MVP release. It provides fundamental features for dynamic Inventory Customization and Stock Keeping, which is designed to be domain-agnostic and should provide flexibility for businesses in varying markets to build, manage and maintain their inventories.

The implementation is part of the Final Degree Project for the Communications Electronics Engineering degree authored by Nicolas Villanueva.


&nbsp;
## Implementation Overview

The current implementation runs on a Docker infrastructure, as specified by the `docker-compose.yml` file: the application runs two containers for both the database and API processes, which run a Postgres and Python image respectively, with the latter's process further specified within `Dockerfile`.

The API is developed using Django as a Web Framework, while incorporating other third-party libraries from its tooling environment, such as Django REST Framework (DRF) and others as seen in the `requirements.txt` file.


&nbsp;
## Code Overview

The following is an overview of the components and patterns developed for the API implementation:

* The `/inventorysphere` directory defines Django's high-level configuration for the project in the `settings.py` file, while also providing functionality reusable across the repository such as the Access Layer's renderers and exception handlers, resources for managing authorization, and utilities for data processing.
* The `/api_internal` directory contains resources associated with the API feature's interfaces and business logic. These include components such as Django Views and Serializers, which define the entry points and the composition of each feature, as well as permission classes and any further elements which may be related to the business layer
* The `/infra_*` directories contain the data-layer components for each module or operational domain (i.e., `custom` for inventory customization, `auth` for authentication and authorization, `stock` for stock keeping, etc.) This includes Django's data-layer abstractions, such as Model and Manager classes, as well as the migrations generated for the DB schema processes.


&nbsp;
## Running InventorySphere API Locally

### System Requirements

In order to execute the system, **Docker and Docker-Compose** need to be installed, preferrably in a Linux host machine. A minimum **8GB RAM** is also recommended 

### Execute API

Run the `docker-compose up` command in the root folder of the repository: If running in a debian system, the command varies to `docker compose up`. Both containers will start running.

### Debugging the application

A configuration for debugging the API using VSCode is in place within `/.vscode/launch.json`. In order to enable debugging:

* Set the `DEBUG` variable within `inventorysphere/settings.py` to `True`.
* Run the `docker-compose up` command, which will start only the database container.
* Within VSCode, go to the "Run and Debug" menu tab (Ctrl+Shift+D), and select and run the "Run InventorySphere Django API" option, which will start the python container with Django in debug mode.