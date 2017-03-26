angular.module('gazerApp').controller('LoginCtrl', function($scope, $state, AuthenticationService) {
    $scope.login = function() {
        AuthenticationService.login(
            $scope.userInputs.email,
            $scope.userInputs.password,
            function(response) {
                AuthenticationService.setCredentials(
                    $scope.userInputs.email,
                    $scope.userInputs.password
                );
                $state.go('index');
            },
            function(response) {
                alert(response.data.message);
            }
        );
    };


    var initController = function() {
        $scope.userInputs = {};
    };

    initController();
});