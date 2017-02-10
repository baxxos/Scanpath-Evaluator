angular.module('gazerApp').controller('LoginCtrl', function($scope, $state, AuthenticationService) {
    $scope.login = function() {
        AuthenticationService.Login(
            $scope.userInputs.email,
            $scope.userInputs.password,
            function(response) {
                AuthenticationService.SetCredentials(
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