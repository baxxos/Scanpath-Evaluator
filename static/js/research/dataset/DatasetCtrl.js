angular.module('ScanpathEvaluator').controller('DatasetCtrl', function($scope, $rootScope, $http, $state, $timeout, DataTreeService, Upload) {
	/*** NEW TASK (FORM) RELATED METHOD ***/
	var isTaskFormValid = function() {
		// Check required inputs
		return (
			$scope.taskNew.name &&
			$scope.taskNew.fileScanpaths &&
			$scope.taskNew.fileRegions &&
			$scope.taskNew.fileBgImage
		);
	};

	var resetTaskForm = function() {
		$scope.taskNew = {
			errors: [],
			success: false,
			uploadState: 0 // System feedback to user: -1: failure, 0: default, 1: uploading, 2: success
		};

		$scope.taskForm.$setPristine();
		$scope.taskForm.$setUntouched();
	};

	// Fix for required field missing message appearing when form was hidden without submitting
	$scope.toggleTaskForm = function() {
		// Do a cleanup if we are hiding the form
		if($scope.guiParams.showTaskForm) {
			resetTaskForm();
		}
		// Toggle the form controlling variable
		$scope.guiParams.showTaskForm = !$scope.guiParams.showTaskForm;
	};

	// Method handles the missing required inputs alerts (most browsers do this automatically though)
	var showUserErrors = function() {
		$scope.taskNew.errors = [];
		$scope.taskNew.success = false;

		if(!$scope.taskNew.name) {
			$scope.taskNew.errors.push('Task name is missing!');
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

	// Utility methods to de-bloat the html
	$scope.concatFileErrors = function(file){
		if(file) {
			return file.$error + ': ' + file.$errorParam;
		}
	};

	$scope.toggleEditTaskForm = function(task) {
		$scope.guiParams.expandedTaskRow = ($scope.guiParams.expandedTaskRow == task.id ? -1 : task.id);

		// Save the object of the task which user requested to edit
		if($scope.guiParams.expandedTaskRow >= 0) {
			$scope.editedTask = angular.copy(task);
		}
	};

	// Updates task details
	$scope.updateTask = function(editedTask) {
		var confirmed = confirm('Are you sure you want to edit this task?');

		if(confirmed) {
			$http({
				url: 'api/task',
				method: 'PUT',
				data: editedTask  // This must match the backend dataset object in terms of attributes
			}).then(
				function(response) {
					if (response.data.success) {
						// Update navigation view
						DataTreeService.updateNavTreeData($rootScope.globals.currentUser.id);

						// Update current screen & notify the user
						loadDataset($scope.dataset.id);
						alert('Your task was edited successfully.');
						// Hide the editing form
						$scope.guiParams.expandedTaskRow = -1;
					}
					else {
						alert(response.data.message);
						console.error(response.data.message);
					}
				},
				function(response) {
					alert('No response from the server');
					console.error('There was no response to from the server to the dataset delete request.');
				}
			)
		}
	};

	// Handles the uploading of the new task form and its uploaded data
	$scope.submitTask = function() {
		if(!isTaskFormValid()) {
			showUserErrors();
			return;
		}
		else {
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
			url: '/api/task',
			method: 'POST',
			data: {
				datasetId: $scope.dataset.id,
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
				// For displaying the success message
				$scope.taskNew.success = response.data.success;

				if(response.data.success == true && response.data.load.id) {
					$scope.taskNew.id = response.data.load.id;

					// Update navigation view
					DataTreeService.updateNavTreeData($rootScope.globals.currentUser.id);
					// Update current screen
					loadDataset($scope.dataset.id);

					// Feedback to user & re-enable control buttons
					$scope.taskNew.uploadState = 2;

					// If the user wishes to be redirected afterwards
					if($scope.taskNew.redirect == true) {
						$timeout(function() {
							$state.go(
								'research.dataset.task',
								{
									datasetId: $state.params.datasetId,
									taskId: $scope.taskNew.id
								}
							);
						}, 5000);
					}
				}
				else {
					$scope.taskNew.errors.push(response.data.message);
					// Feedback to user & re-enable control buttons
					$scope.taskNew.uploadState = -1;
				}
			},
			function(response) {
				alert('No response from the server');
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

		if(confirmed) {
			$http({
				url: 'api/task',
				method: 'DELETE',
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

	/*** CURRENT DATASET RELATED METHODS ***/
	$scope.updateDataset = function(editedDataset) {
		var confirmed = confirm('Are you sure you want to edit this dataset?');

		if(confirmed) {
			$http({
				url: 'api/dataset',
				method: 'PUT',
				data: editedDataset  // This must match the backend dataset object in terms of attributes
			}).then(
				function(response) {
					if (response.data.success) {
						// Update navigation view
						DataTreeService.updateNavTreeData($rootScope.globals.currentUser.id);

						// Update current screen & notify the user
						loadDataset($scope.dataset.id);
						alert('Your dataset was edited successfully.');

						$scope.guiParams.datasetFormErrors = [];
						$scope.guiParams.showEditDatasetForm = false;
					}
					else {
						$scope.guiParams.datasetFormErrors.push(response.data.message);
						console.error(response.data.message);
					}
				},
				function(response) {
					alert('No response from the server');
					console.error('There was no response to from the server to the dataset delete request.');
				}
			)
		}
	};

	$scope.deleteDataset = function(dataset) {
		var confirmed = confirm('Are you sure you want to delete dataset named "' + dataset.name + '"?');

		if(confirmed) {
			$http({
				url: 'api/dataset',
				method: 'DELETE',
				data: {
					datasetId: dataset.id
				}
			}).then(
				function(response) {
					// Update navigation view
					DataTreeService.updateNavTreeData($rootScope.globals.currentUser.id);
					// Redirect from the deleted dataset screen
					$state.go('research');
				},
				function(response) {
					alert('No response from the server');
					console.error('There was no response to from the server to the dataset delete request.');
				}
			)
		}
	};

	var loadDataset = function(datasetId) {
		$http({
			method: 'GET',
			url: '/api/dataset',
			params: {
				datasetId: datasetId
			}
		}).then(
			function(response) {
				if(response.data.success && response.data.load) {
					$scope.dataset = response.data.load;

					// Convert the DB string timestamp into a JavaScript object
					$scope.dataset.dateCreated = formatDatasetDate($scope.dataset.dateCreated);
					$scope.dataset.dateUpdated = formatDatasetDate($scope.dataset.dateUpdated);

					// Set the dataset editing object attributes equal to the loaded one
					$scope.editedDataset = angular.copy($scope.dataset);
				}
				else {
					$scope.guiParams.datasetFormErrors.push(response.data.message);
					console.error(response.data.message);
				}
			},
			function(response) {
			   console.error('There was no response to from the server to the dataset load request.');
			}
		);
	};

	var formatDatasetDate = function(dateString) {
		return Date.parse(dateString);
	};

	$scope.toggleEditDatasetForm = function() {
		$scope.guiParams.showEditDatasetForm = !$scope.guiParams.showEditDatasetForm;
	};

	var initController = function() {
		// New task form related variables
		$scope.taskNew = {
			errors: [],
			success: false,
			uploadState: 0 // System feedback to user: -1: failure, 0: default, 1: uploading, 2: success
		};

		// Edit task form related variables
		$scope.editedTask = {};

		$scope.guiParams = {
			// Misc GUI params
			showTaskForm: false,
			recEnvCollapsed: true,
			showEditDatasetForm: false,
			datasetFormErrors: []
		};

		// For displaying dataset attributes etc.
		$scope.dataset = {};
		// Edit dataset form related variables
		$scope.editedDataset = {};

		// Get basic dataset information and fill $scope.dataset object
		if($state.params.datasetId) {
			loadDataset($state.params.datasetId);
		}
	};

	initController();
});