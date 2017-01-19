// ngAnimate and ngTouch provide basic animations e.g. on a collapsing element
// ui.router defines routes and states (app.config.js) - these are then used in ncy-angular-breadcrumb
// ui.bootstrap to prevent full jQuery import in bootstrapJS
angular.module('gazerApp', ['ngAnimate', 'ngTouch', 'ui.router', 'ui.bootstrap', 'ncy-angular-breadcrumb']);

// globals
// jQuery-style utility selector
var $ = function (elementSelector) {
	return document.body.querySelector(elementSelector);
};

