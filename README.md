# About
This repository is home to the Interactive Research Map. It was created as part of a project seminar during winter term 2022/23.
The Research Map visualizes and contextualizes research output of the Department of Information Systems of the University of Muenster.
To understand how it was created and how each component works, please refer to the repository’s [Wiki](https://github.com/HendrikDroste/research-map/wiki).

# Getting Started
## Prerequisites
To run the application, you need (at least) one machine running Docker Engine on a platform of your choice. It is recommended to allocate at least 8Gb RAM to this machine, as some of the containers are very memory intensive.
As the Research Map uses [MongoDB](https://www.mongodb.com/) to store its data, you need either a self-hosted instance or make use of MongoDB Atlas. The MongoDB Community Edition is free and there is a [Docker image](https://hub.docker.com/_/mongo) available .
To support the implemented search function, a [Meilisearch](https://www.meilisearch.com/) instance is required. Meilisearch is free and there is also a [Docker image](https://hub.docker.com/r/getmeili/meilisearch) available .
## Setup
The Interactive Research Map application is set up using Docker containers. While the frontend container, MongoDB and Meilisearch instances are running continuously, the other containers only need to run periodically. 
### MongoDB
After the [initial setup](https://www.mongodb.com/docs/manual/installation/) of your MongoDB instance, it is recommended to create two additional database users, one with read/write permissions to create and edit collection, and one user with read permissions to perform queries initiated by the frontend.
Currently there are two databases in use: `FLK_Data_Lake` and `FLK_Web`. These databases are created automatically when running the different containers. The read/write permissions of the first user are required for both databases, whereas read permissions are only required for `FLK_Web`.
Database `FLK_Data_Lake` is home to all collections filled by the CRIS exporter and enhanced by the Data_Prep_Pipeline.
Database `FLK_Web` contains all data that is used by the frontend.
### Meilisearch
After the [initial setup](https://docs.meilisearch.com/learn/getting_started/quick_start.html) of your Meilisearch instance, it is recommended to [secure](https://docs.meilisearch.com/learn/security/master_api_keys.html) it by setting a Master key and creating two API keys. The first API key is used by the Meilisearch pipeline container and needs permissions to edit/create documents and indexes, while the second API key is used by the frontend and only needs permission for the search action. The Meilisearch search index is filled/updated every time the Meilisearch pipeline container runs.
### Backend
To retrieve all available data from the CRIS database, the [CRIS exporter](https://github.com/HendrikDroste/research-map/wiki/4.1.3.-CRIS-Exporter) needs to run first. After it has finished, data stored in `FLK_Data_Lake` is enriched by running the [Data Prep Pipeline](https://github.com/HendrikDroste/research-map/wiki/4.2.-Automated-Data-Enrichment). While this pipeline writes some data into `FLK_Web`, additional data from `FLK_Data_Lake` is copied by running the Web pipeline.
When all data is present, you have to run the [Meilisearch pipeline](https://github.com/HendrikDroste/research-map/wiki/4.1.2.-Meilisearch) to create/update the search index.
### Frontend
The Docker image for the frontend can be built by using one of the Dockerfiles located in *./frontend/next-flk/*. In a production environment, it is recommended to use the frontend image built by *prod.Dockerfile*, as this is a leaner image and should reduce load times.
When starting the frontend container, you have to provide different environment variables, that are used to access your MongoDB and your Meilisearch instance respectively. In `NEXT_PUBLIC_MONGODB_URI` you must provide your MongoDB connection string, in `NEXT_PUBLIC_MS_URI` the IP address and port of your Meilisearch instance, and `NEXT_PUBLIC_MS_API_KEY` should be the read-only API key you created earlier.
