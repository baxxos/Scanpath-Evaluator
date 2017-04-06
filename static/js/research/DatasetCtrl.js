angular.module('gazerApp').controller('DatasetCtrl', function($scope, $rootScope, $http, $state, $timeout, DataTreeService, Upload) {
	/*** NEW TASK (FORM) RELATED METHOD ***/
	var isTaskFormValid = function() {
		// Check required inputs
		return (
			$scope.taskNew.name &&
			$scope.taskNew.url &&
			$scope.taskNew.fileScanpaths &&
			$scope.taskNew.fileRegions &&
			$scope.taskNew.fileBgImage
		);
	};

	var resetTaskForm = function() {
		$scope.taskNew = {
			errors: [],
			warnings: [],
			success: false,
			uploadState: 0 // System feedback to user: -1: failure, 0: default, 1: uploading, 2: success
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

	// Method handles the missing required inputs alerts (most browsers do this automatically though)
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
		if(!$scope.taskNew.fileBgImage) {
			$scope.taskNew.errors.push('Background image is missing!');
		}
	};

	// Utility method to de-bloat the html
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
		var fileBgImage = $scope.taskNew.fileBgImage;

		// fileScanpaths.progress = 0;
		// fileRegions.progress = 0;

		// Disable control buttons during the upload and notify the user about uploading start
		$scope.taskNew.uploadState = 1;

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
					fileRegions: fileRegions,
					fileBgImage: fileBgImage
				}
			}
		}).then(
			function(response) {
				if(response.data.success == true && response.data.load.id) {
					$scope.taskNew.success = true;
					$scope.taskNew.id = response.data.load.id;

					// Update navigation view
					DataTreeService.updateNavTreeData($rootScope.globals.currentUser.id);
					// Update current screen
					loadDataset($scope.dataset.id);

					// Feedback to user & re-enable control buttons
					$scope.taskNew.uploadState = 2;

					// TODO If the user wishes to be redirected afterwards
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
					// Feedback to user & re-enable control buttons
					$scope.taskNew.uploadState = -1;
				}
			},
			function(response) {
				console.error('There was no response from the server to the new task request .');
				// Feedback to user & re-enable control buttons
				$scope.taskNew.uploadState = -1;
			},
			function(evt) {
				// Update progress bar (both files get uploaded at the same time) - OPTIONAL
				// fileRegions.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
				// fileScanpaths.progress = Math.min(100, parseInt(100.0 * evt.loaded / evt.total));
			}
		);
	};

	$scope.deleteTask = function(task) {
		var confirmed = confirm('Are you sure you want to delete task named "' + task.name + '"?');

		if(confirmed == true) {
			$http({
				method: 'DELETE',
				url: 'api/task',
				data: {
					taskId: task.id
				}
			}).then(
				function(response) {
					// Update navigation view
					DataTreeService.updateNavTreeData($rootScope.globals.currentUser.id);
					// Update current screen
					loadDataset($scope.dataset.id);
				},
				function(response) {
					alert('No response from the server');
					console.error('There was no response to from the server to the task delete request.');
				}
			)
		}
	};

	/*** ACT DATASET RELATED METHODS ***/
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
			uploadState: 0 // System feedback to user: -1: failure, 0: default, 1: uploading, 2: success
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