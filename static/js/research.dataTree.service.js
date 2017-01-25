angular.module('gazerApp').service('dataTreeService', function($http) {
    // For self-reference in callbacks
    var dataTreeService = this;
    // Data tree object watched by dependent controllers
    this.dataTree = {};

    this.updateNavTreeData = function() {
        $http({
			url: '/get_data_tree',
			method: 'POST',
			data: {
				userId: 123
			}
		}).then(
			function(response) {
                dataTreeService.dataTree = response.data;
			},
			function(data){
				console.log('Failed call to load user data tree.', data);
			}
        );
    }
});