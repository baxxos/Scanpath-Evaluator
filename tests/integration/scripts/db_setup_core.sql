DROP DATABASE "scanpath-evaluator-test";
DROP ROLE IF EXISTS test_user;

CREATE ROLE test_user LOGIN PASSWORD 'test_user';
CREATE DATABASE "scanpath-evaluator-test"
  WITH OWNER = test_user
       ENCODING = 'UTF8'
       TABLESPACE = pg_default
       LC_COLLATE = 'Slovak_Slovakia.1250'
       LC_CTYPE = 'Slovak_Slovakia.1250'
       CONNECTION LIMIT = -1;

COMMENT ON DATABASE "scanpath-evaluator-test"
  IS 'Dedicated database for running automated tests';
