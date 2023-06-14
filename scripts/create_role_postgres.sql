DO
$do$
BEGIN
   IF EXISTS (
      SELECT FROM pg_catalog.pg_roles
      WHERE  rolname = 'postgres') THEN

      RAISE NOTICE 'Role "postgres" already exists. Skipping.';
   ELSE
      CREATE ROLE postgres LOGIN PASSWORD 'postgres';
   END IF;
END
$do$;