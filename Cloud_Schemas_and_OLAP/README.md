# SQL for multi-dimensional analysis on cloud: Partition strategies and maintenance, Cloud dataset models, Indexing

Scaling your Data warehouse on RDBMS on-premise replicas and/or on Google Cloud Platform (GCP)
> Older versions will work with Oracle DB + OCI for older requirements/infra... But these schemas, as of 2025, were mostly tested for GCP (CloudSQL, BQ, Cloud storage etc...)

These tables are optimized for OLAP (dimensional) + Cloud Lakes (Apache spark in-memory output files fed into cloud storage/blob/bucket engines) hybrid etc...

> **Please refer to base schemas in "Schemas/" 's README** for intutive order of execution and base logic. The core data model logic there is the base you need to follow for your cloud/multi-dim optimized schemas to integrate with the ETL and NoSQL Big Data/Graph DB GDS analytics 


--- 
SCALING NOTE:
while these work great for dimensional analysis in Big Query + CloudSQL engines 
and integrate well with noSQL ML/AI + Big Data workflows..
If need more than batch ETL operations or scale into large cloud/CDN,
consider denormalizing table model architecture and also make scheduled job proc to re-index,re-cluster etc...
FOR MORE PEOPLE... base plate here will work great
