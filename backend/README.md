# NUPEDEE Website (backend)

## Dependencies

This project uses Django, Django REST Framework, and PostgreSQL.

## Instructions

These instructions assume a working PostgreSQL server. On GNU/Linux, the server can be installed with the package manager (e.g. `apt`):

``` sh
# apt install postgresql
```

Then a database (in this case, named 'nupedee') and a user (also named 'nupedee') with write access must be created.

```sh
$ sudo -u postgres psql postgres
postgres=# \password postgres
postgres=# CREATE DATABASE nupedee;
postgres=# CREATE USER nupedee PASSWORD ChangeThisPassword123;
postgres=# ALTER DATABASE nupedee OWNER TO nupedee;
```

With the database set up, create a `.env` file in this folder (backend) containing the following variables:

``` sh
SECRET_KEY = 'my-secret-key' # Use get_random_secret_key()
DB_NAME = 'my-database-name'
DB_USER = 'my-database-user'
DB_PASS = 'my-database-password'
DB_HOST = 'network-adress-of-the-database'
DB_PORT = 'port-to-connect-to-the-database' # PostgreSQL defaults to 5432
```

Install [Hatch](https://hatch.pypa.io/) and then install the dependencies in the environment:

Make the Django migrations and migrate to the database:

``` sh
hatch run python manage.py makemigrations
hatch run python manage.py migrate
```

Lastly, create a Django superuser with:

``` sh
hatch run python manage.py createsuperuser
```

And log in to the admin interface in `/admin` on the address where the server is running. Some of the models may be managed there.
