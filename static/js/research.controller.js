angular.module('gazerApp').controller('customCtrl', function($scope, $state, $http) {
	$scope.getUserScanpaths = function() {
		$http.get('get_dataset').then(
			function(response){
				$scope.dataset.scanpaths = response.data.scanpaths;
				$scope.dataset.visualMain = response.data.visualMain
			},
			function(data){
				console.log('Failed to get dataset content: ' + data);
			}
		);
    };

    // Calculate average similarity to a custom scanpath based on previous similarity calculations
    var calcAvgSimToCommon = function() {
		var similarity = 0, total = 0;

		for (var scanpath in $scope.dataset.commonScanpath.similarity) {
			if ($scope.dataset.commonScanpath.similarity.hasOwnProperty(scanpath)) {
				similarity += $scope.dataset.commonScanpath.similarity[scanpath];
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
			function(response){
				// Get the common scanpath
				$scope.dataset.commonScanpath = response.data;
				// Get the average similarity of user scanpath to the common scanpath
				$scope.dataset.commonScanpath.avgSimToCommon = calcAvgSimToCommon();

				// Assign each user scanpath its similarity to the common scanpath
				var similarities = $scope.dataset.commonScanpath.similarity;

				for (var index in $scope.dataset.scanpaths) {
					if ($scope.dataset.scanpaths.hasOwnProperty(index)) {
						var act_scanpath = $scope.dataset.scanpaths[index];
						act_scanpath.simToCommon = similarities[act_scanpath.identifier]; // TODO try-catch of some sort
					}
					else {
						console.error('Missing property ' + index + ' in scanpaths object');
					}
				}
			},
			function(data){
				console.log('Failed to get common scanpath: ' + data);
			}
		);
    };

    // Calculate average similarity to a custom scanpath based on previous similarity calculations
    var calcAvgSimToCustom = function() {
		var similarity = 0, total = 0;

		for (var scanpath in $scope.dataset.customScanpath.similarity) {
			if ($scope.dataset.customScanpath.similarity.hasOwnProperty(scanpath)) {
				similarity += $scope.dataset.customScanpath.similarity[scanpath];
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
			url: "/custom",
			method: "POST",
			data: {customScanpath: customScanpathStr}
		}).then(
			function(response){
				// Get the common scanpath
				$scope.dataset.customScanpath = response.data;
				// Get the average similarity of user scanpath to the common scanpath
				$scope.dataset.customScanpath.avgSimToCommon = calcAvgSimToCustom();

				// Assign each user scanpath its similarity to the common scanpath
				var similarities = $scope.dataset.customScanpath.similarity;

				for (var index in $scope.dataset.scanpaths) {
					if ($scope.dataset.scanpaths.hasOwnProperty(index)) {
						var act_scanpath = $scope.dataset.scanpaths[index];
						act_scanpath.simToCommon = similarities[act_scanpath.identifier]; // TODO try-catch of some sort
					}
					else {
						console.error('Missing property ' + index + ' in scanpath object');
					}
				}
			},
			function(data){
				console.log('Failed to get common scanpath: ' + data);
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

    $scope.initData = function() {
		// Forward declaration of similarity objects to prevent IDE warnings. May be omitted later.
		$scope.dataset = {
			customScanpath: {similarity: ''},
			commonScanpath: {similarity: ''}
		};
		$scope.getUserScanpaths();
		$scope.scanpathSort = 'identifier';
	};
	// Perform scope data initialization
	$scope.initData();
});