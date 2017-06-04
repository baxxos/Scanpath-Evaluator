# Scanpath Evaluator

## DEPENDENCIES:

### Back-end:
* Python 2.7.X
* Flask
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

## CONSTRAINTS:
* File size - 100MB for scanpath data/10MB for AOI data
* AOI count - maximum of 52 AOIs (26 lowercase + 26 uppercase characters)
* AOI shape - exactly 4 vertices for each AOI (rect/square)
* Nested and overlapping AOIs - try to avoid this for correct results
* The original AOI image and its resolution must exactly match the uploaded AOI data
        
## TODOs:
* __Write unit tests__ (Python & JS)
* Upgrade backend to Python 3.X
* Upgrade frontend to AngularJS 1.6.X
* Upgrade frontend JS to ES6
* Hash passwords on the [client side](https://crackstation.net/hashing-security.htm) as well 
* Ditch the user dataset folders and store the scanpath data in database (formatted as JSON) instead
* Create a branch for [Bootstrap 4](https://v4-alpha.getbootstrap.com/) beta upgrade
* Exception & error logging
* Write some more tests
