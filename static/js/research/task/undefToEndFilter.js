// Serves for pushing the scanpaths with undefined common similarity values to the bottom of the table when sorting
angular.module('ScanpathEvaluator').filter('undefToEndFilter', function() {
    return function (array, key) {
        // Column in which we want to push undefined values to the bottom when sorting by it
        var target_key = 'simToCommon';

        if(!angular.isArray(array)) {
            return;
        }
        // Sorting based on a column other than target (e.g. similarity to common scanpath) - leave array as it is
        else if(key.indexOf(target_key) == -1) {
            return array;
        }
        // Sorting based on target column but reversed - fix the key by removing reverse sign ('-')
        else if(key.indexOf(target_key) == 1) {
            key = key.substring(1)
        }

        var present = array.filter(
            function(item) {
                return item[key] != undefined;
            }
        );

        var empty = array.filter(
            function(item) {
                return item[key] === undefined;
            }
        );
        // Push objects with specified value undefined to the end of the sorted array
        return present.concat(empty);
    };
});