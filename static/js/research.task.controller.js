// Handles all scanpath data related actions such as AJAX calls etc.
angular.module('gazerApp').controller('taskCtrl', function($scope, $state, $http, $stateParams) {
	$scope.getTaskScanpaths = function() {
		// TODO pass task ID from url
		$http.get('get_task_data').then(
			function(response) {
				$scope.task.scanpaths = response.data.scanpaths;
				$scope.task.visuals = response.data.visuals;
				$scope.task.id = $stateParams.id; // TODO compare with id from DB
			},
			function(data) {
				console.log('Failed to get task data content.', data);
			}
		);
    };

    // Calculate average similarity to a custom scanpath based on previous similarity calculations
    var calcAvgSimToCommon = function(commonScanpath) {
		var similarity = 0, total = 0;

		for (var scanpath in commonScanpath.similarity) {
			if ($scope.task.commonScanpath.similarity.hasOwnProperty(scanpath)) {
				similarity += $scope.task.commonScanpath.similarity[scanpath];
				// Keep track of the total number of scanpaths as there is no keys.length in dict
				total++;
			}
			else {
				console.error('Missing property ' + scanpath + ' in similarity object');
			}
		}
		return similarity / total;
	};

	var getCommonScanpathDetails = function() {
		$http.get('sta').then(
			function(response) {
				// Get the common scanpath
				$scope.task.commonScanpath = response.data;
				// Get the average similarity of user scanpath to the common scanpath
				$scope.task.commonScanpath.avgSimToCommon = calcAvgSimToCommon($scope.task.commonScanpath);

				// Assign each user scanpath its similarity to the common scanpath
				var similarities = $scope.task.commonScanpath.similarity;

				for (var index in $scope.task.scanpaths) {
					if ($scope.task.scanpaths.hasOwnProperty(index)) {
						var act_scanpath = $scope.task.scanpaths[index];
						act_scanpath.simToCommon = similarities[act_scanpath.identifier]; // TODO try-catch of some sort
					}
					else {
						console.error('Missing property ' + index + ' in scanpaths object');
					}
				}
			},
			function(data) {
				console.log('Failed to get common scanpath.', data);
			}
		);
    };

    // Calculate average similarity to a custom scanpath based on previous similarity calculations
    var calcAvgSimToCustom = function(customScanpath) {
		var similarity = 0, total = 0;

		for (var scanpath in customScanpath.similarity) {
			if ($scope.task.customScanpath.similarity.hasOwnProperty(scanpath)) {
				similarity += $scope.task.customScanpath.similarity[scanpath];
				// Keep track of the total number of scanpaths as there is no keys.length in dict
				total++;
			}
			else {
				console.error('Missing property ' + scanpath + ' in similarity object');
			}
		}
		return similarity / total;
	};

	var getCustomScanpathDetails = function(customScanpathStr) {
		// Convert user input to uppercase and remove all whitespaces by regex
		customScanpathStr = customScanpathStr.toUpperCase();
		customScanpathStr = customScanpathStr.replace(/\s/g, "");
		// Regex to normalize the scanpath (remove repeated AOIs: AABC -> ABC)
		// The Regex /(.)\1+/ matches any single char followed by the same char at least once (+)
		customScanpathStr = customScanpathStr.replace(/(.)\1+/g, '$1');

		$http({
			url: '/custom',
			method: 'POST',
			data: {
				customScanpath: customScanpathStr
			}
		}).then(
			function(response) {
				// Get the common scanpath
				$scope.task.customScanpath = response.data;
				// Get the average similarity of user scanpath to the common scanpath
				$scope.task.customScanpath.avgSimToCommon = calcAvgSimToCustom($scope.task.customScanpath);

				// Assign each user scanpath its similarity to the common scanpath
				var similarities = $scope.task.customScanpath.similarity;

				for (var index in $scope.task.scanpaths) {
					if ($scope.task.scanpaths.hasOwnProperty(index)) {
						var act_scanpath = $scope.task.scanpaths[index];
						act_scanpath.simToCommon = similarities[act_scanpath.identifier]; // TODO try-catch of some sort
					}
					else {
						console.error('Missing property ' + index + ' in scanpath object');
					}
				}
			},
			function(data) {
				console.log('Failed to get common scanpath.', data);
			}
		);
    };

	$scope.fillTableDetails = function() {
		if ($scope.customScanpath) {
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

    var init = function() {
		// Forward declaration of similarity objects to prevent IDE warnings. May be omitted later.
		$scope.task = {};
		// Get basic scanpath data
		$scope.getTaskScanpaths();
		// Sort the data based on a column
		$scope.scanpathSort = 'identifier';
	};
	// Perform view initialization
	init();
});