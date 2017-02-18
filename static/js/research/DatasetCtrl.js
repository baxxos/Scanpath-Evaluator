angular.module('gazerApp').controller('DatasetCtrl', function($scope, $rootScope, $http, $state, $timeout, DataTreeService, Upload) {
	// New task form related methods
	var isTaskFormValid = function() {
		// Check required inputs
		return (
			$scope.taskNew.name &&
			$scope.taskNew.url &&
			$scope.taskNew.fileScanpaths &&
			$scope.taskNew.fileRegions
		);
	};

	var resetTaskForm = function() {
		$scope.taskNew = {
			errors: [],
			warnings: [],
			success: false,
			uploading: false
		};

		$scope.taskForm.$setPristine();
		$scope.taskForm.$setUntouched();
	};

	// Fix for required field missing message appearing when form was hidden without submitting
	$scope.toggleTaskForm = function() {
		// Do a cleanup if we are hiding the form
		if($scope.showTaskForm) {
			resetTaskForm();
		}
		// Toggle the form controlling variable
		$scope.showTaskForm = !$scope.showTaskForm;
	};

	var showUserErrors = function() {
		$scope.taskNew.errors = [];

		if(!$scope.taskNew.name || !$scope.taskNew.url) {
			$scope.taskNew.errors.push('A required field is missing!');
		}
		if(!$scope.taskNew.fileScanpaths) {
			$scope.taskNew.errors.push('Scanpaths file is missing!');
		}
		if(!$scope.taskNew.fileRegions) {
			$scope.taskNew.errors.push('AOI file is missing!');
		}
	};

	// Utility methods to de-bloat the html
	$scope.isUploading = function() {
		if($scope.taskNew.fileScanpaths) {
			var progress = $scope.taskNew.fileScanpaths.progress;
			return (progress >= 0 && progress < 100);
		}
		else {
			return false;
		}
	};

	$scope.concatFileErrors = function(file){
		if(file) {
			return file.$error + ': ' + file.$errorParam;
		}
	};

	// Handles the uploading of the new task form and its uploaded data
	$scope.submitTask = function() {
		if(!isTaskFormValid()) {
			showUserErrors();
			return;
		}
		else {
			$scope.taskNew.warnings = [];
			$scope.taskNew.errors = [];
		}

		var fileScanpaths = $scope.taskNew.fileScanpaths;
		var fileRegions = $scope.taskNew.fileRegions;

		fileScanpaths.progress = 0;
		fileRegions.progress = 0;

		// Disable control buttons during the upload
		$scope.taskNew.uploading = true;

		Upload.upload({
			url: '/api/task/add',
			data: {
				datasetId: $state.params.id,
				name: $scope.taskNew.name,
				url: $scope.taskNew.url,
				// Optional attributes, replace 'undefined' by empty string as undefined value is not a valid JSON
				// value and null value would be changed into 'null' string value on the backend due to multipart form
				description: ($scope.taskNew.description ? $scope.taskNew.description : ''),
				// Uploaded files
				files: {
					fileScanpaths: fileScanpaths,
					fileRegions: fileRegions
				}
			}
		}).then(
			function(response) {
				if(response.data.success == true && response.data.load.id) {
					$scope.taskNew.success = true;
					$scope.taskNew.id = response.data.load.id;

					// Update navigation view
					DataTreeService.updateNavTreeData($rootScope.globals.currentUser.email);
					// Update current screen
					loadDataset($scope.dataset.id);

					// If the user wishes to be redirected afterwards
					if($scope.taskNew.redirect == true) {
						$timeout(function() {
							$state.go(
								'research.task',
								{ id: $scope.taskNew.id }
							);
						}, 5000);
					}
				}
				else {
					$scope.taskNew.warnings.push(response.data.message);
				}
				// Re-enable control buttons
				$scope.taskNew.uploading = false;
			},
			function(response) {
				console.error('There was no response from the server to the new task request .');
				// Re-enable control buttons
				$scope.taskNew.uploading = false;
			},
			function(evt) {
				// Update progress bar (both files get uploaded at the same time)
				fileRegions.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
				fileScanpaths.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
			}
		);
	};

	// Current dataset related methods
	var loadDataset = function(datasetId) {
		$http({
			method: 'GET',
			url: '/api/dataset',
			params: {
			   id: datasetId
			}
		}).then(
			function(response) {
				if(response.data.success == true && response.data.load) {
				   $scope.dataset = response.data.load;
				}
				else {
				   console.error(response.data.message);
				}
			},
			function(response) {
			   console.error('There was no response to from the server to the dataset load request.');
			}
		);
	};

	var initController = function() {
		// New task form related variables (from the dataset screen)
		$scope.taskNew = {
			errors: [],
			warnings: [],
			success: false,
			uploading: false
		};

		$scope.showTaskForm = false;
		$scope.dataset = {};

		// Get basic dataset information and fill $scope.dataset object
		if($state.params.id) {
			loadDataset($state.params.id);
		}
	};

	initController();
});