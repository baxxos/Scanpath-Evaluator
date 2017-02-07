// Handles all sidebar related actions
angular.module('gazerApp').controller('ResearchSidebarCtrl', function($scope, DataTreeService) {
    var init = function() {
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
                for(var dataset_iter = 0; dataset_iter < data.length; dataset_iter++) {
                    // Compose dataset object in the format suitable for nav tree
                    var formatted_dataset = {
                        'label': data[dataset_iter].label,
                        'href': '#/research/dataset/' + data[dataset_iter].id,
                        'children': []
                    };

                    for (var task_iter = 0; task_iter < data[dataset_iter].children.length; task_iter++) {
                        // Compose task object in the format suitable for nav tree
                        var formatted_task = {
                            'label': data[dataset_iter].children[task_iter].label,
                            'href': '#/research/task/' + data[dataset_iter].children[task_iter].id
                        };
                        formatted_dataset.children.push(formatted_task);
                    }
                    // Push formatted dataset with its children into the tree navigation data object
                    $scope.navTreeData.push(formatted_dataset);
                }
            }
        );

        // Update navigation view with user owned datasets
        DataTreeService.updateNavTreeData();
    };

    init();
});