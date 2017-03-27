angular.module('gazerApp').controller('LoginCtrl', function($scope, $state, AuthenticationService) {
    $scope.login = function() {
        AuthenticationService.login(
            $scope.userInputs.email,
            $scope.userInputs.password,
            function(response) {
                AuthenticationService.setCredentials(
                    response.data.load.id,
                    $scope.userInputs.email,
                    $scope.userInputs.password
                );
                $state.go('index');
            },
            function(response) {
                console.error(response.data.message);
            }
        );
    };


    var initController = function() {
        $scope.userInputs = {};
    };

    initController();
});