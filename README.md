# Simple banking API Demo

Demo of simple banking system API.
Built on top of python stack using Django, Gunicorn, PostgreSQL and Nginx


### Setup and installation (Docker):

- Build docker image
 ```sh
    $ docker-compose build
 ```

- Start banking system service
 ```sh
    $ ./start-service.sh -s
 ```
 _Note: If you are facing 'Permission denied' error when executing the above command, then re-run the command after granting executable permissions to the 'start-service.sh' file_
   ```sh
      $ chmod +x ./start-service.sh
   ```

- Stop banking system service
 ```sh
    $ ./start-service.sh -k
 ```

- Run tests for this project
 ```sh
    $ ./start-service.sh -t
 ```

- _Note: Check out start-service shell script 'help' command for more details_
 ```sh
     $ ./start-service.sh -h
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


