angular.module('ScanpathEvaluator').directive('faqAccordionHeading', function() {
    // Actual heading content
    var headingTemplate = '<span ng-transclude></span>';

    // Arrow direction for expanded/collapsed questions is based on questionStates[featured]
    var arrowTemplate = '<span class="pull-right glyphicon" ' +
        'ng-class="{\'glyphicon-chevron-down\': questionStates[\'featured\'], ' +
        '\'glyphicon-chevron-right\': !questionStates[\'featured\']}"></span>';

    return {
        restrict: 'E',
        transclude: true,
        template: '<uib-accordion-heading>' + headingTemplate + arrowTemplate + '</uib-accordion-heading>',
        replace: false
    }
});