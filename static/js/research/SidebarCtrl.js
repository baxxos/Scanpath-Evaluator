// Handles all sidebar related actions
angular.module('ScanpathEvaluator').controller('SidebarCtrl', function($scope, $rootScope, DataTreeService) {
    var initController = function() {
        $scope.navTreeData = [];

        // Watch variable and do something if its value changes
        $scope.$watch(
            // Watched variable
            function() {
                return DataTreeService.dataTree;
            },
            // Value change callback - e.g. when a new data tree is acquired through ajax call
            function(data) {
                $scope.navTreeData = [];

                for(var datasetIter = 0; datasetIter < data.length; datasetIter++) {
                    // Compose dataset object in the format suitable for nav tree
                    var formatted_dataset = {
                        'label': data[datasetIter].label,
                        'href': '#/research/dataset/' + data[datasetIter].id,
                        'children': []
                    };

                    for (var taskIter = 0; taskIter < data[datasetIter].children.length; taskIter++) {
                        // Compose task object in the format suitable for nav tree
                        var formatted_task = {
                            'label': data[datasetIter].children[taskIter].label,
                            'href': '#/research/dataset/' + data[datasetIter].id +
                                    '/task/' + data[datasetIter].children[taskIter].id
                        };
                        formatted_dataset.children.push(formatted_task);
                    }
                    // Push formatted dataset with its children into the tree navigation data object
                    $scope.navTreeData.push(formatted_dataset);
                }
            }
        );

        // Update navigation view with user owned datasets (if the current user is set)
        if($rootScope.globals.currentUser) {
            DataTreeService.updateNavTreeData($rootScope.globals.currentUser.id);
        }
    };

    initController();
});