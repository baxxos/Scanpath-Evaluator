angular.module('ScanpathEvaluator').controller('FaqCtrl', function($scope, $anchorScroll) {

    $scope.scrollAndExpand = function(id) {
        $anchorScroll(id);
        $scope.questionStates[id] = true;
    };

    var initController = function() {
        // True = question with given ID is expanded, false = collapsed
        $scope.questionStates = {
            // Featured question is always expanded
            'featured': true
        };
    };

    initController();
});