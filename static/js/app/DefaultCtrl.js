// Default controller is defined as ng-controller on the body element of index.html
angular.module('gazerApp').controller('DefaultCtrl', function($scope, $rootScope, $state, AuthenticationService){
	// Used for excluding breadcrumbs in particular states
	$scope.isBreadcrumbAreaDisplayed = function() {
		var excluded_states = ['login', 'register'];

		for (var i = 0; i < excluded_states.length; i++) {
			if ($state.includes(excluded_states[i])) {
				return true;
			}
		}
		return false;
	};

	// Consider moving to a separate controller
	$scope.logout = function() {
		AuthenticationService.ClearCredentials();
	};

    var initController = function() {
		$scope.isNavCollapsed = true
	};
	// Perform view initialization
	initController();
});

// TODO https://github.com/mgechev/angularjs-style-guide#controllers upratat