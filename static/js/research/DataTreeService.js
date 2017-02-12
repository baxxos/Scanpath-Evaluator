angular.module('gazerApp').service('DataTreeService', function($http) {
    // For self-reference in callbacks
    var DataTreeService = this;
    // Data tree object watched by dependent controllers
    this.dataTree = {};

	// Updates data tree navigation object according to the current user.
	// This object is $watched in controllers which refresh the view in case of change
    this.updateNavTreeData = function(userEmail) {
        $http({
			url: '/api/user/get_data_tree',
			method: 'POST',
			data: {
				email: userEmail
			}
		}).then(
			function(response) {
                DataTreeService.dataTree = response.data;
			},
			function(data){
				console.log('Failed call to load user data tree.', data);
			}
        );
    };

    this.clearNavTreeData = function() {
		DataTreeService.dataTree = {};
	}
});