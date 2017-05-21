# Scanpath Evaluator

DEPENDENCIES:
<p>
    Back-end:<br />
    <ul>
        <li>Python 2.7</li>
        <li>Flask</li>
        <li>PostgreSQL (SQLalchemy + psycopg2)</li>
        <li><a href="https://pythonhosted.org/passlib/install.html">Passlib</a></li>
    </ul>
</p>
<p>
    Front-end:<br />
    <ul>
        <li>
            <a href="https://ajax.googleapis.com/ajax/libs/angularjs/1.5.8/angular.js">
                AngularJS 1.5.11
            </a>
        </li>
        <li>
            <a href="https://angular-ui.github.io/bootstrap/">
                UI-Bootstrap (JS)
            </a>
        </li>
        <li>
            <a href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                Bootstrap 3 CSS
            </a>
        </li>
        <li>
            <a href="https://github.com/angular-ui/ui-router">UI-router</a> - handles navigation
            <ul>
                <li>ui-view: location where the HTML template assigned to current state should be placed. Can be explicitly named.</li>
                <li>ui-sref-active: this element will be assigned active state if ui-sref matches current state</li>
                <li>ui-sref: see above</li>
            </ul>
        </li>
        <li>
            <a href="https://github.com/ncuillery/angular-breadcrumb">Angular-Breadcrumb</a>
            <ul>
                <li>
                    ncy-breadcrumb: marks element where breadcrumbs panel will be placed. Ui-router configuration determines displayed text and state hierarchy.
                </li>
            </ul>
        </li>
        <li>
            <a href="https://github.com/nickperkinslondon/angular-bootstrap-nav-tree">
                Bootstrap Nav Tree
            </a>
            <ul>
                <li>
                    abn-tree: hierarchical tree navigation directive based on a custom-format JSON object.
                </li>
            </ul>
        </li>
        <li>
            <a href="https://github.com/danialfarid/ng-file-upload">ng-file-upload</a>
        </li>
        <li>
            <a href="https://github.com/asafdav/ng-csv">ng-csv</a> (requires <a href="https://cdnjs.com/libraries/angular-sanitize/1.5.11">Angular-sanitize</a>)
        </li>
    </ul>
</p> 

CONSTRAINTS:
<p>
    <ul>
        <li>File size - 100MB for scanpath data/10MB for AOI data</li>
        <li>AOI count - maximum of 52 AOIs (26 lowercase + 26 uppercase characters)</li>
        <li>AOI shape - exactly 4 vertices for each AOI (rect/square)</li>
        <li>Nested and overlapping AOIs - try to avoid this for correct results</li>
        <li>The original AOI image and its resolution must exactly match the uploaded AOI data</li>
    </ul>
</p>

TODOs:
* Upgrade backend to Python 3.X
* Upgrade frontend to AngularJS 1.6.X
* Upgrade frontend JS to ES6
* Hash passwords on the [client side](https://crackstation.net/hashing-security.htm) as well 
* Ditch the user dataset folders and store the scanpath data in database (formatted as JSON) instead
* Create a branch for Bootstrap 4 beta upgrade
