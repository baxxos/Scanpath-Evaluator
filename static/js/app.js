// Created by Baxos on 2.11.2016.

var gazerApp = angular.module("gazerApp", ['ngAnimate', 'ngTouch', 'ui.router', 'ui.bootstrap', 'ncy-angular-breadcrumb']);

gazerApp.controller("defaultCtrl", function($scope, $state, $http, $animate){
    $scope.init = function() {
        $scope.$state = $state;
		$scope.isNavCollapsed = true;
	};

	$scope.init();
});

gazerApp.controller("customCtrl", function($scope, $state, $http){
	$scope.getUserScanpaths = function() {
		$http.get('get_scanpaths').then(
			function(response){
				$scope.dataset.userScanpaths = response.data.userScanpaths;
				$scope.dataset.visualMain = response.data.visualMain
			},
			function(data){
				console.log('Failed to get user scanpaths: ' + data);
			}
		);
    };

    var getAvgSimToCommon = function() {
		var similarity = 0, total = 0;

		for (var scanpath in $scope.dataset.commonScanpath.similarity) {
			similarity += $scope.dataset.commonScanpath.similarity[scanpath];
			total++;
		}

		return similarity / total;
	};

	var getCommonScanpathDetails = function() {
		$http.get('sta').then(
			function(response){
				// Get the common scanpath
				$scope.dataset.commonScanpath = response.data;
				// Get the average similarity of user scanpath to the common scanpath
				$scope.dataset.commonScanpath.avgSimToCommon = getAvgSimToCommon();

				// Assign each user scanpath its similarity to the common scanpath
				var similarities = $scope.dataset.commonScanpath.similarity;

				for (var index in $scope.dataset.userScanpaths) {
					var act_scanpath = $scope.dataset.userScanpaths[index];
					act_scanpath.simToCommon = similarities[act_scanpath.identifier]; // TODO try-catch of some sort
				}
			},
			function(data){
				console.log('Failed to get common scanpath: ' + data);
			}
		);
    };

    var getAvgSimToCustom = function() {
		var similarity = 0, total = 0;

		for (var scanpath in $scope.dataset.customScanpath.similarity) {
			similarity += $scope.dataset.customScanpath.similarity[scanpath];
			total++;
		}

		return similarity / total;
	};

	var getCustomScanpathDetails = function(customScanpath) {
		// Convert user input to uppercase and remove all whitespaces by regex
		customScanpath = customScanpath.toUpperCase();
		customScanpath = customScanpath.replace(/\s/g, "");

		$http.get('custom/' + customScanpath).then(
			function(response){
				// Get the common scanpath
				$scope.dataset.customScanpath = response.data;
				// Get the average similarity of user scanpath to the common scanpath
				$scope.dataset.customScanpath.avgSimToCommon = getAvgSimToCustom();

				// Assign each user scanpath its similarity to the common scanpath
				var similarities = $scope.dataset.customScanpath.similarity;

				for (var index in $scope.dataset.userScanpaths) {
					var act_scanpath = $scope.dataset.userScanpaths[index];
					// TODO simToCustom instead of simToCommon - html edit needed
					act_scanpath.simToCommon = similarities[act_scanpath.identifier]; // TODO try-catch of some sort
				}
			},
			function(data){
				console.log('Failed to get common scanpath: ' + data);
			}
		);
    };

    var $ = function (elementSelector) {
		return document.body.querySelector(elementSelector);
	};

	$scope.fillTableDetails = function() {
		if ($scope.customScanpath) {
			console.log('calculating similarities to custom scanpath');
			getCustomScanpathDetails($('#customScanpathText').value);
		}
		else {
			getCommonScanpathDetails();
		}
	};

    $scope.setSort = function(sortVariable, newValue) {
		if($scope[sortVariable] == newValue) {
			$scope[sortVariable] = '-' + $scope[sortVariable];
		} else {
			$scope[sortVariable] = newValue;
		}
	};

    $scope.init = function() {
		$scope.dataset = {};
		$scope.getUserScanpaths();
		$scope.scanpathSort = 'identifier';
	};

	$scope.init();
});