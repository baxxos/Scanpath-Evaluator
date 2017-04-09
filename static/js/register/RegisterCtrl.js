angular.module('ScanpathEvaluator').controller('RegisterCtrl', function($scope, $http, $state, $timeout) {
    var isFormValid = function() {
        return ($scope.user.password == $scope.user.repeatPassword) &&
               ($scope.user.password.length >= 8) &&
               ($scope.user.password && $scope.user.repeatPassword && $scope.user.email)
    };

    var showUserErrors = function() {
        // Either returns error message or sets user to valid state if there are no errors
        $scope.user.errors = [];

        if($scope.user.password != $scope.user.repeatPassword) {
            $scope.user.errors.push('Passwords do not match!');
        }
        if($scope.user.password.length < 8) {
            $scope.user.errors.push('Passwords too short - enter at least 8 characters!');
        }
        if(!($scope.user.password && $scope.user.repeatPassword && $scope.user.email)) {
            $scope.user.errors.push('A required field is missing!');
        }
    };

    $scope.submitUser = function() {
        // Validate form and show any errors by storing them in the user object
        if(!isFormValid()) {
            showUserErrors();
            return;
        }
        else {
            $scope.user.errors = [];
            $scope.user.warnings = [];
        }

        $http({
			url: '/api/user/add',
			method: 'POST',
			data: {
				email: $scope.user.email,
                password: $scope.user.password,
                // Optional attributes, replace 'undefined' by 'null' to ensure valid JSON object
                name: ($scope.user.name ? $scope.user.name : null),
                surname: ($scope.user.surname ? $scope.user.surname : null)
			}
		}).then(
			function(response) {
                if(response.data.success == true) {
                    $scope.user.success = true;
                    $timeout(function() {
                        $state.go('login');
                    }, 5000);
                }
                else {
                    $scope.user.warnings.push(response.data.message);
                }
			},
			function(response){
				console.log('Failed call to load user data tree.', response);
			}
        );
    };

    var initController = function() {
        $scope.user = {
            errors: [],
            warnings: [],
            success: false
        };
    };

    initController();
});