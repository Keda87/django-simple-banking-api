# Simple banking API Demo

Demo of simple banking system API.
Built on top of python stack using Django, Gunicorn, PostgreSQL and Nginx


### Setup and installation (Docker):

- Build docker image
 ```sh
    $ make build
 ```

- Start banking system service
 ```sh
    $ make start
 ```

- Stop banking system service
 ```sh
    $ make stop
 ```

- Run tests for this project
 ```sh
    $ make test
 ```

- make command usage details
 ```sh
     $ make help
 ```

### Setup and installation (Manual):

Pre-requisite:
- Python 3.6
- PostgreSQL

You can go through following below to start the project.

```
$ createdb --username=postgres simplebankdb
$ pip install -r requirements.txt
$ ./manage.py migrate
$ ./manage.py runserver
```

And you can run the project test using following command.

```
$ ./manage.py test --keepdb
```

### API Docs.

Endpoints for this project are documented in `<hostname>/docs/`

But you can also import [postman collections](Simple BANK.postman_collection.json) within this project for more convenience.


