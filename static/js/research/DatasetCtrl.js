angular.module('gazerApp').controller('DatasetCtrl', function($scope, $rootScope, $http, $state, $timeout, DataTreeService) {
	// New task form related methods
	var isTaskFormValid = function() {
		// Check required inputs
		return $scope.taskNew.name;
	};

	var resetTaskForm = function() {
		$scope.taskNew = {
			errors: [],
			warnings: [],
			success: false
		};

		$scope.taskForm.$setPristine();
		$scope.taskForm.$setUntouched();
	};

	var showUserErrors = function() {
		$scope.taskNew.errors = [];

		if(!$scope.taskNew.name) {
			$scope.taskNew.errors.push('A required field is missing!');
		}
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

	$scope.submitTask = function() {
		if(!isTaskFormValid()) {
			showUserErrors();
		}
		else {
			$scope.taskNew.warnings = [];
			$scope.taskNew.errors = [];
		}

		$http({
			method: 'POST',
			url: '/api/task/add',
			data: {
				datasetId: $state.params.id,
				name: $scope.taskNew.name,
				// Optional attributes, replace 'undefined' by 'null' to ensure valid JSON object
				description: ($scope.taskNew.description ? $scope.taskNew.description : null)
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
			},
			function(response) {
				console.error('There was no response from the server to the new task request .');
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
			success: false
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