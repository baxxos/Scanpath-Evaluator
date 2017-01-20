// Default controller is defined as ng-controller on the body element of index.html
angular.module('gazerApp').controller("defaultCtrl", function($scope, $state, $animate){
    $scope.initDefault = function() {
        $scope.$state = $state;
		$scope.isNavCollapsed = true;
	};
	$scope.initDefault();
});