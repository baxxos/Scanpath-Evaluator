angular.module('gazerApp').controller('ResearchTaskFormCtrl', function($scope, $state, $http) {
    // New task form related methods (from the dataset screen)
	$scope.isFormValid = function() {
		return true;
	};

	$scope.showUserErrors = function() {

	};

	// Fix for required field missing message appearing when form was hidden without submitting
	$scope.toggleTaskForm = function() {
		if($scope.taskNew.showForm == true) {
		   $scope.taskNew.name = ' ';
		}
		else {
		   $scope.taskNew.name = null;
		}
		$scope.taskNew.showForm = !$scope.taskNew.showForm;
	};

	$scope.submitTask = function() {
		if(!isFormValid()) {
			showUserErrors();
		}
	};

    var initController = function() {
        // New task form related variables (from the dataset screen)
		$scope.taskNew = {
			showForm: false
		};
    };
    initController();
});