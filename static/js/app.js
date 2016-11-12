// Created by Baxos on 2.11.2016.

var gazerApp = angular.module("gazerApp", ['ngAnimate', 'ngTouch', 'ui.router', 'ui.bootstrap', 'ncy-angular-breadcrumb']);

gazerApp.controller("defaultCtrl", function($scope, $state, $http, $animate){
	$scope.getUserScanpaths = function() {
		$http.get('get_scanpaths').then(
			function(response){
				$scope.data.userScanpaths = response.data;
			},
			function(data){
				console.log('Failed to get user scanpaths: ' + data);
			}
		);
    };

    $scope.init = function() {
        $scope.$state = $state;
		$scope.isNavCollapsed = true;
		$scope.data = {};
		$scope.getUserScanpaths();
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