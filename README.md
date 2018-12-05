# Simple banking API Demo

Demo of simple banking system API.
Built on top of python stack using Django, Gunicorn, Nginx, RabbitMQ and MongoDB.

    
### Setup and installation (Docker):
    
If you are using docker, what you need to do is just build the image.
    
```
$ docker-compose build
$ docker-compose up -d
```
    
Then create the database and do a migrations.
    
```
$ docker-compose exec primary_db createdb --username=postgres simplebankdb
$ docker-compose exec api python manage.py migrate
```

If you want to run test for this project, you can execute following command.

```
$ docker-compose exec api python manage.py test --keepdb
```

### Setup and installation (Manual):

Pre-requisite:
- Python 3.6
- RabbitMQ
- PostgreSQL
- Pipenv (Optional)

You can go through following below to start the project.

```
$ createdb --username=postgres simplebankdb
$ pip install -r requirements.txt or pipenv install
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

In case you need to access all transaction logs, you can access raw mongodb result using following command.

```
$ docker-compose exec api python manage.py event_logs (if you are using Docker)
$ ./manage.py event_logs
```

