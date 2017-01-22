# scanpath_app

LANGUAGES & FRAMEWORKS USED:<br />
Back-end: Python 2.7 + Flask<br />
<p>
    Front-end:<br />
    <ul>
        <li>
            <a href="https://ajax.googleapis.com/ajax/libs/angularjs/1.5.8/angular.js">
                AngularJS 1.5.8
            </a>
        </li>
        <li>
            <a href="https://angular-ui.github.io/bootstrap/">
                UI-Bootstrap (JS)
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
            <a href="https://maxcdn.bootstrapcdn.com/bootstrap/3.3.7/css/bootstrap.min.css">
                Bootstrap 3 CSS
            </a>
        </li>
    </ul>
</p> 
PAGE RENDERING & NAVIGATION:
HTML files are served by custom Angular routing provider (UI-router). It<br />
enhances the basic Angular $routeProvider functionality by replacing it with own<br />
$stateProvider keyword. It can be used for remembering states (e.g. for breadcrumbs) etc.
