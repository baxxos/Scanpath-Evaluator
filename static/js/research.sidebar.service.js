angular.module('gazerApp').service('DataTreeService', function($http, $rootScope) {
    // For self-reference in callbacks
    var DataTreeService = this;
    // Data tree object watched by dependent controllers
    this.dataTree = {};

    this.updateNavTreeData = function() {
        $http({
			url: '/get_data_tree',
			method: 'POST',
			data: {
				email: $rootScope.globals.currentUser.email
			}
		}).then(
			function(response) {
                DataTreeService.dataTree = response.data;
			},
			function(data){
				console.log('Failed call to load user data tree.', data);
			}
        );
    }
});