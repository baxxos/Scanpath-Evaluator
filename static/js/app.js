// Created by Baxos on 2.11.2016.

var gazerApp = angular.module("gazerApp", ['ngAnimate', 'ngTouch', 'ui.router', 'ui.bootstrap', 'ncy-angular-breadcrumb']);

gazerApp.controller("gazerAppCtrl", function($scope, $state){
    $scope.init = function() {
		//console.log($state.includes('profile'));
        $scope.$state = $state;
		$scope.isNavCollapsed = true;
	};

	$scope.init();
});

gazerApp.controller("customCtrl", function($scope, $state, $http){
	$scope.getCommonScanpath = function() {
		$http.get('sta').then(
			function(response){
				$scope.commonScanpath = response.data;
			},
			function(data){
				console.log('Failed to get common scanpath: ' + data);
			}
		);
    };
});