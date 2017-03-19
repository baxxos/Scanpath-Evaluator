// ngAnimate and ngTouch provide basic animations e.g. on a collapsing element
// ui.router defines routes and states (app.config.js) - these are then used in ncy-angular-breadcrumb
// ui.bootstrap to prevent full jQuery import in bootstrapJS
// TODO migrate to Angular 1.6.x and update ui-bootstrap/router as well
angular.module(
	'gazerApp',
	[
		'ngAnimate', 'ngTouch', 'ui.router', 'ui.bootstrap', 'ncy-angular-breadcrumb',
		'angularBootstrapNavTree', 'ngCookies', 'ngFileUpload', 'ngSanitize', 'ngCsv'
	]
);

// Default app initialization (globals, rootScope etc.)
angular.module('gazerApp').run(function($rootScope, $cookies, $state, $http) {
	// Keep user logged on after page refresh
	$rootScope.globals = $cookies.getObject('globals') || {};

	// Remember current user data
	if ($rootScope.globals.currentUser) {
		$http.defaults.headers.common['Authorization'] = 'Basic ' + $rootScope.globals.currentUser.authdata;
	}

	$rootScope.$on('$stateChangeSuccess', function (event, next, current) {
		// Redirect to login page if not logged in and trying to access a restricted page
		var allowed_states = ['login', 'register'];
		var allowedPage = false;

		for (var i = 0; i < allowed_states.length; i++) {
			if ($state.includes(allowed_states[i])) {
				allowedPage = true;
			}
		}

		// Redirect when an anonymous user is attempting to access private pages
		var loggedIn = $rootScope.globals.currentUser;
		if (!allowedPage && !loggedIn) {
			$state.go('login');
		}
	});
});
