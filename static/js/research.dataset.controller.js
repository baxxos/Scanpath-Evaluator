angular.module('gazerApp').controller('DatasetCtrl', function($scope, $rootScope, $http, $state, $timeout, DataTreeService, $animate) {
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

                    // Update navigation view with user owned datasets
                    DataTreeService.updateNavTreeData($rootScope.globals.currentUser.email);

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
                console.error('There was no response from the server to the new dataset request .');
            }
        );
   };

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

    var initController = function() {
        $scope.datasetNew = {
            success: false,
            redirect: true,
            errors: [],
            warnings: []
        };

        // Get basic dataset information and set $scope.dataset
        loadDataset($state.params.id);

        $scope.taskNew = {
            showForm: false
        };
    };

    initController();
});