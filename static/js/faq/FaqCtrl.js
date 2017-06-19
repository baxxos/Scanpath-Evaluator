angular.module('ScanpathEvaluator').controller('FaqCtrl', function($scope, $anchorScroll) {
    // Lazy-load paths for JS & HTML components (ocLazyLoad)
    $scope.lazyLoadParams = [
        'static/js/faq/faqAccordionHeading.js'
    ];

    $scope.scrollAndExpand = function(id) {
        $anchorScroll(id);
        $scope.questionStates[id] = true;
    };

    var initController = function() {
        // Open only one question at a time (true) or allow multiple ones to be opened (false)
        $scope.closeOthers = false;

        // True = question with given ID is expanded, false = collapsed
        $scope.questionStates = {
            // Featured question is initially expanded
            'featured': true
        };
    };

    initController();
});