// Default controller is defined as ng-controller on the body element of index.html
angular.module('gazerApp').controller("defaultCtrl", function($scope, $state, $animate){
	// Used for excluding breadcrumbs in particular states
	$scope.isCurrStateExcluded = function() {
		var excluded_states = ['login', 'register'];

		for (var i = 0; i < excluded_states.length; i++) {
			if ($state.includes(excluded_states[i])) {
				return true;
			}
		}

		return false;
	};

    var initDefault = function() {
		$scope.isNavCollapsed = true;
	};
	// Perform view initialization
	initDefault();
});