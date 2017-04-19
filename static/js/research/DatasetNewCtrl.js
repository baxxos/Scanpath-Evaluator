angular.module('ScanpathEvaluator').controller('DatasetNewCtrl', function($scope, $rootScope, $state, $http, $timeout, DataTreeService) {
    var isFormValid = function() {
        // Check required inputs, no other requirements
        return $scope.datasetNew.name;
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
            return;
        }
        else {
            $scope.datasetNew.errors = [];
            $scope.datasetNew.warnings = [];
        }

        $http({
            url: 'api/dataset',
            method: 'POST',
            data: {
                userId: $rootScope.globals.currentUser.id,
                name: $scope.datasetNew.name,
                userEmail: $rootScope.globals.currentUser.email,
                // Optional attributes, replace 'undefined' by 'null' to ensure valid JSON object
                description: ($scope.datasetNew.description ? $scope.datasetNew.description : null)
            }
        }).then(
            function(response) {
               // The server provides us with the new dataset id in order to redirect
                if(response.data.success == true && response.data.load.id) {
                    $scope.datasetNew.success = true;
                    $scope.datasetNew.id = response.data.load.id;

                    // Update navigation view
                    DataTreeService.updateNavTreeData($rootScope.globals.currentUser.id);

                    // If the user wishes to be redirected afterwards
                    if($scope.datasetNew.redirect == true) {
                        $timeout(function() {
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
                console.error('There was no response from the server to the new dataset request .');
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