// Default controller is defined as ng-controller on the body element of index.html
angular.module('gazerApp').controller("defaultCtrl", function($scope, $state, $animate){
    var initDefault = function() {
		$scope.isNavCollapsed = true;
	};
	// Perform view initialization
	initDefault();
});