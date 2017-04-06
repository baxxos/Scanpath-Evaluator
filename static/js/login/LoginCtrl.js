angular.module('gazerApp').controller('LoginCtrl', function($scope, $state, AuthenticationService) {
    var isLoginFormValid = function() {
		// Check required form inputs
		return (
			$scope.userInputs.password &&
			$scope.userInputs.email
		);
	};

    $scope.login = function() {
        if(!isLoginFormValid()) {
            return;
        }
        else {
            $scope.errors = [];
            $scope.warnings = [];
        }

        AuthenticationService.login(
            $scope.userInputs.email,
            $scope.userInputs.password,
            // Successful login callback
            function(response) {
                AuthenticationService.setCredentials(
                    response.data.load.id,
                    $scope.userInputs.email,
                    $scope.userInputs.password
                );
                $state.go('research');
            },
            // Unsuccessful login callback
            function(response) {
                $scope.errors.push(response.data.message);
            },
            // Timed out request callback
            function(response) {
                $scope.warnings.push('Internal error - please try again later.')
            }
        );
    };

    var initController = function() {
        $scope.userInputs = {};
    };

    initController();
});