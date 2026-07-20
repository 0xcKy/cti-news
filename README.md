# CTI News (WIP)

## Description

This project aims to automate the collection, processing, correlation, and notification of news related to Information Security and Cyber Threat Intelligence (CTI).

News is collected from multiple sources, stored in a database, processed, and enriched to identify content relevant to the organization's monitored assets. The system also supports information correlation and alert generation through multiple notification channels.

## Features

* Automatic news collection via RSS feeds.
* News storage in PostgreSQL.
* Extraction of relevant information, including:
  * CVEs
  * IOCs
  * Affected products
  * Vendors
  * Proofs of Concept (PoCs)
* Filtering based on monitored assets.
* Alert generation via email and other notification channels.

## Technologies

* Python
* PostgreSQL
* Ollama
* LangChain

## Objectives

* Automate cyber threat intelligence collection.
* Reduce the volume of manual analysis.
* Prioritize relevant news.
* Correlate information from multiple sources.
* Help Information Security teams quickly identify emerging threats.

