/* ngAnimate and ngTouch provide basic animations support - e.g. on a collapsing element
 * ui.router defines routes and states (app.config.js) - these are then used in ncy-angular-breadcrumb
 * ui.bootstrap to get rid of jQuery dependency in Bootstrap JS
 * ocLazyLoad for lazy-loading own modules such as controllers, directives etc.
 */
angular.module(
	'ScanpathEvaluator',
	[
		'ngAnimate', 'ngTouch', 'ui.router', 'ui.bootstrap', 'ncy-angular-breadcrumb',
		'angularBootstrapNavTree', 'ngCookies', 'ngFileUpload', 'ngSanitize', 'ngCsv', 'oc.lazyLoad'
	]
);

// Default app initialization (globals, rootScope etc.)
angular.module('ScanpathEvaluator').run(function($rootScope, $cookies, $state) {
	// Keep user logged on after page refresh
	$rootScope.globals = $cookies.getObject('globals') || {};

	$rootScope.$on('$stateChangeSuccess', function (event, next, current) {
		// Hide the mobile navigation on state change
		$rootScope.isNavCollapsed = true;

		// Redirect to login page if not logged in and trying to access a restricted page
		var allowed_states = ['login', 'register', 'index', 'faq'];
		var isPageAllowed = false;

		for (var i = 0; i < allowed_states.length; i++) {
			if ($state.includes(allowed_states[i])) {
				isPageAllowed = true;
			}
		}

		// Redirect when an anonymous user is attempting to access private pages
		var loggedIn = $rootScope.globals.currentUser;
		if (!isPageAllowed && !loggedIn) {
			$state.go('login');
		}
	});
});
