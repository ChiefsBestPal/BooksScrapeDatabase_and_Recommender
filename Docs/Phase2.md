# Overview
For the second phase, we opted for Neo4j as our NoSQL database due to its ease of use, and because most
of us had gained proficiency with it during our previous assignment. Our system largely remained
unchanged from the first phase, where the database was hosted on MySQL. The system comprises entities
centered around a book structure, such as genres, subjects, characters, authors, reviews, etc., along with
their relationships to books. Each entity has its attributes and is identified by an auto-incremented key.
There are two main differences between our database schema in MySQL and Neo4j. Firstly, weak entities
like thumbnails and prices are now listed as array attributes of books, rather than existing as their own
entities. Secondly, the ISA relationship between Person, Author, and Reviewer was removed in our Neo4j
schema. This decision was made because, within the scope of our database, a Person must be either an
Actor and/or Reviewer, ensuring that the covering constraint is met.
# Approaches
Initially, we populated our data with CSV files from our MySQL database. We began by selecting every
table and exporting them as CSV files. These files were then imported into our Neo4j database to serve as
sections for reading during the creation of entities and formation of relationships. For each entity, we
parsed the CSV file, extracted the attributes of each row, and created nodes with attributes derived from
those rows. Subsequently, we established relationships by processing the "relationship" CSV files, which
contained mappings of one entity to another using their unique auto-incremented keys, forming edges
linked to those nodes. However, we later discovered potential restrictions on the use of CSV files, forcing
us to develop a Python script. This script connects directly to both our databases, enabling us to populate
Neo4j without relying on CSV files ...
# Challenges
The first challenge we faced was during the CSV file exportation process. By default, when exporting
from a table with more than 1000 rows in MySQL, only the first 1000 rows are displayed. To ensure that
every row is shown in a large table, we needed to configure the settings accordingly. Consequently, we
initially believed there was an issue with our script for populating Neo4j because it appeared not to be
mapping relationships properly. However, this was due to our data being limited by a cap imposed by
MySQL workbench. Secondly, the queries to populate our Neo4j database were exceedingly slow; some
relationship queries took up to an hour to execute on a contextually/reasonably powerful machine.
Thirdly, when attempting to write a script to populate the database directly without using CSV files, we
encountered difficulty locating the parameter to establish a connection to both databases. For instance, as
our database was local, Neo4j did not have a field for the "user" value, whereas our Python script required
it.
There were also more fundamental issues in terms of exporting data from MySQL’s persistent state data
formats to Neo4J. Intuitively, we had to be concerned about design in some way since MySQL is tabular
and Neo4j is graph-based, but the most time consuming or the greater challenges were the most
unexpected. There were some indexing issues in populating at times, but as well there were
syntax/parsing issues that were specific to Neo4j and not present in MySQL; namely the double quotes (“)
problem. We had to re-export certain specific data rows and escape all double quotes present with another
double quote (“”) in order for the Cypher scripts to run in Neo4j. Overall we did not have any critical
challenges that we were not able to overcome and it was a great learning experience for both database
tech stack, we view those challenges as evolutionary steps that are integral, efficient and natural part of
our development and testing processes working with these databases.