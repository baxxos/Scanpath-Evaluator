// Default controller is defined as ng-controller on the body element of index.html
angular.module('gazerApp').controller("defaultCtrl", function($scope, $state, $animate){
    $scope.initDefault = function() {
        $scope.$state = $state;
		$scope.isNavCollapsed = true;
	};
	// Perform scope state initialization
	$scope.initDefault();
});