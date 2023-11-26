# Twitter-clone

---

## About project

This project is similar to the social network Twitter. 
Backend was created on Python with the FastAPI framework.
Docker is used to deploy the project. You can see all of
endpoints by looking at link 
[http://localhost/api/docs](http://localhost/api/docs) after
project installing and starting.

---

## How to install

1. Pull it by Git
2. Create a file with name `.env` in the root of project by 
template of `.env.template`
3. Insert into just created file `.env` all variables.
4. Execute command `docker-compose up`
5. All is done! Enjoy!

> By default, in Postgres is created a user with username 
> 'admin' and the same password, host of database currently 
> is 'postgres' but it can change by changing the name of 
> container in `docker-compose.yml`. Database by default 
> is created with name 'twitter' (but you also can change it
> in file located in `postgres/init_db.sql`)

## How to test the API

1. Install the project (by instructions higher)
2. Set the variables in `.env` file for testing
3. Install all requirements for developers 
`pip install -r backend/requirements/requirements-dev.txt` 
4. Uncomment (if it is) in file docker-compose.yml the graph 
`ports` in the service of database 
5. Start the service named database (`docker-compose up 
-d database`)
6. Move to `backend` directory
7. Execute command `pytest -v tests/tests.py`
