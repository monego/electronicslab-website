# NUPEDEE Website (backend)

## Dependencies

This project uses Django, Django REST Framework, and MariaDB.

## Instructions

These instructions assume a working MariaDB server. On GNU/Linux, the server can be installed with the package manager (e.g. `apt`):

``` sh
# apt install mariadb-server
```

Then a database and a user with write access must be created.

With the database set up, create a `.env` file in this folder (backend) containing the following variables:

``` sh
SECRET_KEY = 'my-secret-key' # Make something up
DB_NAME = 'my-database-name'
DB_PASS = 'my-database-password'
DB_HOST = 'network-adress-of-the-database'
DB_PORT = 'port-to-connect-to-the-database'
```

Install [Poetry](https://python-poetry.org/) and then install the dependencies in the environment:

``` sh
poetry install
```

Make the Django migrations and migrate to the database:

``` sh
poetry run ./manage.py makemigrations
poetry run ./manage.py migrate
```

Lastly, create a Django superuser with:

``` sh
poetry run ./manage.py createsuperuser
```

And log in to the admin interface in `/admin` on the address where the server is running. Some of the models may be managed there.
