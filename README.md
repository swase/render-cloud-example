# API Development and Documentation Final Project

## Capstone

The following python project was originally forked from https://github.com/udacity/render-cloud-example. 

The work work here is for the completion of the module : Capstone Project. (Part of the FullStack Nanodegree program - https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044). The work done is purely for learning resources and should be used as such. 

Any further information on the project should be looked up on the above links.

## About the Stack
The app is made up of mainly 2 parts - a backend (python, Flask, SQLAlchemy and PostgresSQL) and Testing(Flask and unittest)
### Backend

The backend files are contained within the root directory. They consist of folders: auth (used for handling authentication that is done using third party provider Auth0. https://auth0.com/)

The database folder consists of the model used for project. While postgres was used, any equivelant relational database could be used. Required changes would be to the database uri found in ./database/models.py folder.

#### Authentication
Adjust the environment variable as shown below in order to bypass the authentication. If using authentication, a valid token set up using Auth0 would need to be used. This would then need to be linked to the domain and API audience. 

Adding permissions to the API resources is required. Permissions must be added to the token in the authorisation header. A bearer token is used for this application. 2 roles were create: "Team Leader" and "Team Member" for basic testing. POST, PATCH, DELETE permissions were created for each end point.

All resources are get requests require no authentication and accessible to both roles
"team lead" role has access to all permissions

#### Setting up the Backend

##### Install Dependencies

1. **Python 3.7** - Follow instructions to install the latest version of python for your platform in the [python docs](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python)

2. **Virtual Environment** - We recommend working within a virtual environment whenever using Python for projects. This keeps your dependencies for each project separate and organized. Instructions for setting up a virual environment for your platform can be found in the [python docs](https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/)

3. **PIP Dependencies** - Once your virtual environment is setup and running, install the required dependencies by navigating to the `/backend` directory and running:

```bash
pip install -r requirements.txt
```

##### Key Pip Dependencies

- [Flask](http://flask.pocoo.org/) is a lightweight backend microservices framework. Flask is required to handle requests and responses.

- [SQLAlchemy](https://www.sqlalchemy.org/) is the Python SQL toolkit and ORM we'll use to handle the lightweight SQL database. You'll primarily work in `app.py`and can reference `models.py`.

- [Flask-CORS](https://flask-cors.readthedocs.io/en/latest/#) is the extension we'll use to handle cross-origin requests from our frontend server.

#### Set up the Database

With Postgres running, create a `capstone` database (or whichever name is used):

```bash
createdb capstone;
```

In order to populate the db with tables, a user with sufficient permissions must be used when setting up the database uri. See appropriate environment variables below. 

##### Environment variables
The database URI is configured in backend/models.py as such `"postgresql://{}:{}@{}/{}".format(
    user, password, "localhost:5432", database_name
)`

- Either can be confirgured by hard coding the user, password and database_name. (Must edit models.py file)
- Other option is to use enironment variables as below
The Below variables can be placed within a file called setup.sh (changing to allow execution of said file. On linux: chmod +x setup.sh).

The variable RUN_WITH_NO_AUTH is used in auth.py module in order to run locally without any auth. It is recommended to remove the code in lines 165 - 168. Can also set the metnioned variable to 'true'. Note flask app will need to be stopped/started again. 

```bash
export TABLE_NAME=capstone
export DB_USER=
export DB_PASSWORD=
export TABLE_NAME_TEST=capstone_test
export DB_USER_TEST=
export DB_PASSWORD_TEST=
export API_AUDIENCE=default
export AUTH0_DOMAIN=default
export TEAM_LEAD_TOKEN=
export TEAM_MEMBER_TOKEN=
export RUN_WITH_NO_AUTH=false
```

To run the server, execute:
```bash
source ./run.sh
flask run
```

## API Reference

### Getting Started
- Below set up is to run locally. Although this app can be deployed elsewhere, the appropriate steps would need to be followed by the cloud provider being used. 
- Base URL: At present this app can only be run locally and is not hosted as a base URL. The backend app is hosted at the default, `http://127.0.0.1:5000/`, which is set as a proxy in the frontend configuration. 
- Authentication: When run by default, this app requires a token provided by Auth0. To set up an application, steps can be followed as shown: https://auth0.com/docs/get-started/auth0-overview/set-up-apis.

By default there is a Test application that can be used to acquire a valid token. An example is given below

```
https://your-domain-.com/authorize?audience=<YOUR-API-AUDIENCE>&response_type=token&client_id=<YOUR-CLIENT-ID>&redirect_uri=<APPROPRIATE-CALLBACK-URL>/login-results
```

### Error Handling
Handling of errors are shown in error_handlers.py. With custom AuthError in auth/auth.py.

Errors are returned as JSON objects in the following format:
```
{
    "success": False, 
    "error": 400,
    "message": "bad request"
}
```
Authentication errors are handled with extra nested JSON object for further detail. An example below
```
{
    "error": 401,
    "message": {
        "code": "authorization_header_missing",
        "description": "Authorization header is expected."
    },
    "success": false
}
```
The API will return three error types when requests fail:
- 400: Bad Request
- 401: Unauthorised
- 403: Forbidden
- 404: Resource Not Found
- 422: Unprocessable 

### Endpoints 

`GET  /articles`
- General:
  - returns a list of articles
  - Request Arguments: None
  - Returns: An object with a 2 keys, articles, that contains an array of articles objects in short format, and success key.
  - Acessible without any authentication
- Sample: `curl http://127.0.0.1:5000/articles`
```json
{
    "articles": [
        {
            "id": 5,
            "tags": "poem,top-rated,popular",
            "title": "The Water"
        },
        {
            "id": 14,
            "tags": "Test123,Interesting,To-do",
            "title": "Test Article"
        }
    ],
    "success": true
}
```

---


`GET '/articles/${id}'`

- (If exists) Fetches longer format detail of specified article
- Request Arguments: `id` - integer
- Returns: An article object
- Sample: `curl http://127.0.0.1:5000/articles/4
```json
{
    "article": {
        "article_link": "https://www.public-domain-poetry.com/henry-lawson/water-5558",
        "author_id": 2,
        "id": 5,
        "publisher_id": 2,
        "tags": "poem,top-rated,popular",
        "title": "The Water"
    },
    "success": true
}
```

`GET  /authors`
- General:
  - returns a list of authors
  - Request Arguments: None
  - Returns: An object with a 2 keys, "articles", that contains an array of author objects in short format, and "success".
  - Acessible without any authentication
- Sample: `curl http://127.0.0.1:5000/authors`
```json
{
    "authors": [
        {
            "full_name": "Robert  Lowe",
            "id": 1
        },
        {
            "full_name": "Henry  Lawson",
            "id": 2
        }
    ],
    "success": true
}
```

---


`GET '/authors/${id}'`

- (If exists) Fetches longer format detail of specified author
- Request Arguments: `id` - integer
- Returns: An author object
- Sample: `curl http://127.0.0.1:5000/articles/4
```json
{
    "author": {
        "articles": [
            {
                "article_id": 357,
                "title": "Children Of Light"
            }
        ],
        "full_name": "Robert  Lowe",
        "id": 1
    },
    "success": true
}
```
`GET  /publishers`
- General:
  - returns a list of publishers
  - Request Arguments: None
  - Returns: An object with a 2 keys, "publishers", that contains an array of author objects in short format, and "success".
  - Acessible without any authentication
- Sample: `curl http://127.0.0.1:5000/publishers`
```json
{
    "publishers": [
        {
            "id": 2,
            "name": "Scott and Young"
        },
        {
            "id": 5,
            "name": "test Publisher - test PATCH"
        }
    ],
    "success": true
}
```

---
`GET '/publishers/${id}'`

- (If exists) Fetches longer format detail of specified publisher
- Request Arguments: `id` - integer
- Returns: An author object
- Sample: `curl http://127.0.0.1:5000/publishers/4
```json
{
    "publisher": {
        "articles": [],
        "company_link": "www.test-articles.com",
        "id": 5,
        "name": "test Publisher - test PATCH"
    },
    "success": true
}
```

---

`DELETE '/articles/${id}'`

- Deletes a specified articles using the id of the question
- Request Arguments: `id` - integer
- Returns: Appropriates JSON object with keys "success" and "delete". The latter refering to id of successfully deleted resource. 
- Requires sufficient permission. "Team lead" role.
  - delete:articles
- Sample: `curl -X DELETE http://localhost:5000/Articles/10`

Response body:
```json
{
    "delete": 14,
    "success": true
}
```
`DELETE '/authors/${id}'`

- Deletes a specified author using the id of the question
- Request Arguments: `id` - integer
- Returns: Appropriates JSON object with keys "success" and "delete". The latter refering to id of successfully deleted resource. 
- Requires sufficient permission. "Team lead" role.
  - delete:authors
- Sample: `curl -X DELETE http://localhost:5000/publishers/10`

Response body:
```json
{
    "delete": 5,
    "success": true
}
```
`DELETE '/publishers/${id}'`

- Deletes a specified publisher using the id of the question
- Request Arguments: `id` - integer
- Returns: Appropriates JSON object with keys "success" and "delete". The latter refering to id of successfully deleted resource. 
- Requires sufficient permission. "Team lead" role.
  - delete:publishers
- Sample: `curl -X DELETE http://localhost:5000/publishers/10`

Response body:
```json
{
    "delete": 5,
    "success": true
}
```

---

`POST '/articles'`

- Sends a post to create a new article
- Requires existing author and publisher present
- All fields required as shown below
- post:articles permission required
- Responds with article object of created resource

 Request Body:
```json
{
    "title": "Children Of Light",
    "article_link": "https://www.public-domain-poetry.com/robert-lowell/children-of-light-2114",
    "tags": ["poem", "top-rated", "popular"],
    "publisher_id": 2,
    "author_id": 51
}
 
```

Response Body:
```json
{
    "article": {
        "article_link": "https://www.public-domain-poetry.com/robert-lowell/children-of-light-2114",
        "author_id": 1,
        "id": 357,
        "publisher_id": 2,
        "tags": "poem,top-rated,popular",
        "title": "Children Of Light"
    },
    "success": true
}
 
```

---

`POST '/authors'`

- Sends a post request in order to add a new author
- requires post:authors permission
- Articles field left null for initial creation
- All fields required as shown below

Request Body:
```json
{
    "names": "Robert",
    "lastname": "Lowe"
}
```

Response Body:
```json
{
    "author": {
        "articles": [],
        "full_name": "Robert  Lowe",
        "id": 365
    },
    "success": true
}
```

---

`POST '/publishers'`

- Sends a post request to create a new publisher
- requires post:publishers permission
- Articles field left null for initial creation
- All fields required as shown below

Request Body:
```json
{
    "name": "Penguin Books",
    "company_link": "www.penguin-books.com"
}
```

Response body:

```json
{
    "publisher": {
        "articles": [],
        "company_link": "www.penguin-books.com",
        "id": 344,
        "name": "Penguin Books"
    },
    "success": true
}
```

## Testing


To deploy the tests, run

```bash
dropdb if exisdts capstone_test
createdb capstone_test
python test_flaskr.py
```

User with sufficient permissions required as with the main application. Ability to read, write and make changes to the database and table structures.

## Authors
Forked from  https://github.com/udacity/render-cloud-example and edited as part of Udacity course by myself, Francois.


## Acknowledgements 
Part of the FullStack Webdev course https://www.udacity.com/course/full-stack-web-developer-nanodegree--nd0044.

Taken as part of a cohort and sponsored by my employer, NatWest Group. 