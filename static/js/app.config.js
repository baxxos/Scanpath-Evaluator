'use strict';

// State machine for named states based on URL and (currently) unnamed corresponding views
angular.module('gazerApp')
	.config(['$stateProvider', '$urlRouterProvider', '$locationProvider',
		function($stateProvider, $urlRouterProvider) {
			$stateProvider
				.state("index", {
					url: "/",
					controller: 'defaultCtrl',
					templateUrl: 'static/partials/landing.html',
					ncyBreadcrumb: {
						label: 'Home'
					}
				})
				.state('profile', {
					url: '/profile',
					controller: 'defaultCtrl',
					templateUrl: 'static/partials/profile.html',
					ncyBreadcrumb: {
						label: 'Profile',
						parent: 'index'
					}
				})
				.state('research', {
					url: '/research',
					controller: 'researchCtrl',
					templateUrl: 'static/partials/research.html',
					ncyBreadcrumb: {
						label: 'Research',
						parent: 'index'
					}
				})
				.state('research.sidebar', {
					templateUrl: 'static/partials/research.sidebar.html',
					controller: 'researchSidebarCtrl',
					ncyBreadcrumb: {
						skip: true // Do not consider this state in the breadcrumbs data
					}
				});
			// Set default fallback URL
			$urlRouterProvider.otherwise('/');
}]);

