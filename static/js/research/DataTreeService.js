angular.module('ScanpathEvaluator').service('DataTreeService', function($http) {
    // For self-reference in callbacks
    var self = this;
    // Data tree object watched by dependent controllers
    this.dataTree = {};

	// Updates data tree navigation object according to the current user.
	// This object is $watched in controllers which refresh the view in case of change
    this.updateNavTreeData = function(userId) {
        $http({
			url: '/api/user/get_data_tree',
			method: 'GET',
			params: {
				userId: userId
			}
		}).then(
			function(response) {
				// Replace the current data tree (any depending ctrl will fire $watch event)
				self.dataTree = self.orderAlphabetically(response.data, 'label');
			},
			function(data){
				console.log('Failed call to load user data tree.', data);
			}
        );
    };

    this.orderAlphabetically = function(objToSort, sortBy) {
		// Custom comparison function (case insensitive string sorting)
		var compareFunc = function(a, b) {
			var aToLower = a[sortBy].toLowerCase();
			var bToLower = b[sortBy].toLowerCase();

			if (aToLower < bToLower) {
				return -1;
			}
			if (aToLower > bToLower) {
				return 1;
			}
			else {
				return 0;
			}
		};
		// Return sorted array
		return objToSort.sort(compareFunc);
	};

    this.clearNavTreeData = function() {
		self.dataTree = {};
	}
});