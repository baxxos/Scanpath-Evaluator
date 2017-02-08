angular.module('gazerApp').controller('DatasetCtrl', function($scope, $rootScope, $http, $state, $timeout, DataTreeService) {
    var isFormValid = function() {
        return true;
    };

    var showUserErrors = function() {
        $scope.datasetNew.errors = [];

        if (!$scope.datasetNew.name) {
            $scope.datasetNew.errors.push('A required field is missing!');
        }
    };

    $scope.submitDataset = function() {
        if(!isFormValid()) {
            showUserErrors();
        }
        else {
            $scope.datasetNew.errors = [];
            $scope.datasetNew.warnings = [];
        }

        $http({
            url: 'api/dataset/add',
            method: 'POST',
            data: {
               name: $scope.datasetNew.name,
               description: $scope.datasetNew.description,
               userEmail: $rootScope.globals.currentUser.email
            }
        }).then(
            function(response) {
               // The server provides us with the new dataset id in order to redirect
                if(response.data.success == true && response.data.load.id) {
                    $scope.datasetNew.success = true;
                    $scope.datasetNew.id = response.data.load.id;

                    // Update navigation view with user owned datasets
                    DataTreeService.updateNavTreeData();

                    // If the user wishes to be redirected afterwards
                    if($scope.datasetNew.redirect == true) {
                        $timeout(function () {
                            $state.go(
                                'research.dataset',
                                { id: $scope.datasetNew.id }
                            );
                        }, 5000);
                    }
                }
                else {
                    $scope.datasetNew.warnings.push(response.data.message);
                }
            },
            function(response) {

            }
        );
   };

    var initController = function() {
        $scope.datasetNew = {
            success: false,
            redirect: true,
            errors: [],
            warnings: []
        };
    };

    initController();
});