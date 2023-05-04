CREATE DATABASE amazonvader;

--Create the connection user and grant it access to the database.
CREATE USER 'amazonreviews' IDENTIFIED WITH mysql_native_password BY 'ThisIsJustATest-1!';
grant all on amazonvader.* to 'amazonreviews';

--In a real environment, you would do something like grant select on specific tables, but this is for development.

