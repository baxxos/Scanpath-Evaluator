// Default controller is defined as ng-controller on the body element of index.html
angular.module('ScanpathEvaluator').controller('DefaultCtrl', function($scope, $rootScope, $state, $anchorScroll, AuthenticationService){
	// Used for excluding breadcrumbs in particular states
	$scope.isBreadcrumbAreaDisplayed = function() {
		var excluded_states = ['login', 'register', 'index', 'faq'];

		for (var i = 0; i < excluded_states.length; i++) {
			if ($state.includes(excluded_states[i])) {
				return true;
			}
		}
		return false;
	};

	// Used for controlling the body background (image/none)
	$scope.isHomePage = function() {
		return $state.includes('index');
	};

	// Consider moving to a separate controller
	$scope.logout = function() {
		AuthenticationService.clearCredentials();
		$state.go('login');
	};

	$scope.scrollTo = function(id) {
		$anchorScroll(id);
	};

    var initController = function() {
    	// Hide navigation on mobile devices by default when the page loads
		$rootScope.isNavCollapsed = true;
	};
	// Perform view initialization
	initController();
});

// TODO https://github.com/mgechev/angularjs-style-guide#controllers upratat