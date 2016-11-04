// Created by Baxos on 2.11.2016.

var gazerApp = angular.module("gazerApp", ["ui.router", "ncy-angular-breadcrumb"]);

gazerApp.controller("gazerAppCtrl", function($scope, $state){
    $scope.init = function() {
		//console.log($state.includes('profile'));
        $scope.$state = $state;
	};

	$scope.init();
});

gazerApp.controller("customCtrl", function($scope, $state){
    $scope.init = function() {
		console.log($state.includes('profile'));
        //$scope.$parent.$state = $state;
	};

	$scope.foo = function() {
        return true;
    };

	$scope.init();
});