CREATE SCHEMA IF NOT EXISTS {schema};
DROP TABLE IF EXISTS {schema}.{table};
CREATE TABLE {schema}.{table} 
(
{fields_definition}
)
;

COPY {schema}.{table}
FROM '{data_path_and_filename}' CSV HEADER DELIMITER '{sep}' ENCODING '{encoding}';

COMMIT;