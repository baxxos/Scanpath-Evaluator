// Handles all sidebar related actions
angular.module('gazerApp').controller('researchSidebarCtrl', function($scope, $state, $http, $location) {
    var fake_data = function() {
        $scope.navTreeData = [
            {
                label: 'Dataset 1',
                href: '#/research/dataset/1',
                children: [
                    {
                        label: 'Task 1',
                        href: '#/research/task/2'
                    }
                ]
            }
        ];
    };

    fake_data();
});