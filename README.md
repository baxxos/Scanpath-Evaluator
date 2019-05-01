# Scanpath Evaluator
![](https://reposs.herokuapp.com/?path=baxxos/Scanpath-Evaluator&color=brightgreen)

[Currently hosted on Heroku](https://scanpath-evaluator.herokuapp.com/#/)

## Datasets
To keep this repository clean, all datasets containing TSV-formatted scanpath & AOI data have been moved to [Google Drive](https://drive.google.com/open?id=0B9F-9_QAlgdGZFk1X1lzdExqZFk). You can also download them already zipped together [from here](https://drive.google.com/file/d/0B9F-9_QAlgdGeE9uS3JxOExqWTA).

## Local install
In order to run the app locally, clone this repository (development branch), download required packages (see below), compile SCSS files to CSS and fire it up via your IDE (`main.py`) or [command line](http://flask.pocoo.org/docs/0.12/cli/). 

However, in order to run it properly, you will also need to set up the PostgreSQL database. All tables can be created automatically via [SQLAlchemy's ORM](http://docs.sqlalchemy.org/en/latest/orm/tutorial.html#create-a-schema) - see the `Base.metadata.create_all(engine)` command in `database.py` (application re-launch is required).

If you want to save yourself some time, [here](https://drive.google.com/open?id=0B9F-9_QAlgdGQjFnUEUxVHpCc00) is a template database backup containing 1 guest user and all the datasets linked above. You can use this file to set up your database within seconds by using the _pgAdmin_ app or CLI. The guest user credentials can be found in the `config.py` file.

## Dependencies:

### Back-end:
* Python (2.7.X)
* [Flask](http://flask.pocoo.org/) (0.12.X)
* PostgreSQL (SQLalchemy + psycopg2)
* [Passlib](https://pythonhosted.org/passlib/install.html)

### Front-end:
* [AngularJS 1.5.11](https://ajax.googleapis.com/ajax/libs/angularjs/1.5.11/angular.js)
* [UI-Bootstrap JS](https://angular-ui.github.io/bootstrap/) - to get rid of jQuery required by default Bootstrap
* [UI-Router](https://github.com/angular-ui/ui) - to handle client-side navigation
* [Bootstrap 3 CSS](href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css)
* [Angular-Breadcrumb](https://github.com/ncuillery/angular-breadcrumb)
    * ncy-breadcrumb: marks element where the breadcrumbs panel will be placed. UI-Router configuration determines displayed text content and state hierarchy.
* [Bootstrap Nav Tree](https://github.com/nickperkinslondon/angular-bootstrap-nav-tree) - for navigating between user datasets, tasks etc.
    * abn-tree: hierarchical tree navigation directive based on a custom-format JSON object.
* [ng-file-upload](https://github.com/danialfarid/ng-file-upload) - for uploading user data
* [ng-csv](https://github.com/asafdav/ng-csv") - for exporting user calculations
    * requires [Angular-sanitize](https://cdnjs.com/libraries/angular-sanitize/1.5.11)

## Constraints:
* File size - 100MB for scanpath data/10MB for AOI data
* AOI count - maximum of 52 AOIs (26 lowercase + 26 uppercase characters)
* AOI shape - exactly 4 vertices for each AOI (rect/square)
* Nested and overlapping AOIs - try to avoid this for correct results
* The original AOI image and its resolution must exactly match the uploaded AOI data

## Running tests
### Unit tests
Run following command from the project root directory:  
```
pytest . --cov=src --cov-branch --cov-report term-missing
```

### Integration tests
Run the `run.ps1` PowerShell script from the integration tests folder.  

PostgreSQL 9.5 with a default user account (`postgres/postgres`) has to be installed on the host machine prior to running these tests.

## TODOs:
* __Write unit tests__ (Python & JS)
* Upgrade backend to Python 3.X
* Upgrade frontend to AngularJS 1.6.X
* Upgrade frontend JS to ES6
* Lazy load Angular modules & create a custom Bootstrap build
* Allow users to download their uploaded data in JSON/TSV format
* Exception & error logging
* Write some more tests
