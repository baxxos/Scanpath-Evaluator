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
				// State displaying static information about datasets and their tasks
				.state('research', {
					url: '/research',
					views: {
						'@': {
							controller: 'defaultCtrl',
							templateUrl: 'static/partials/research.layout.html'
						},
						'left@research' : {
							controller: 'researchSidebarCtrl',
							templateUrl: 'static/partials/research.main.sidebar.html'
						},
						'right@research' : {
							templateUrl: 'static/partials/research.main.static.html'
						}
					},
					ncyBreadcrumb: {
						label: 'Research',
						parent: 'index'
					}
				})
				// State which allows to choose a dataset for an UX experiment stored in the DB
				.state('research.dataset', {
					url: '/dataset/:id',
					views: {
						'right@research': {
							templateUrl: 'static/partials/research.main.dataset.html'
						}
					},
					ncyBreadcrumb: {
						label: 'Dataset details',
						parent: 'research'
					}
				})
				// State which allows to choose a task (sub-dataset) from the previously selected dataset
				.state('research.task', {
					url: '/task/:id',
					views: {
						'right@research': {
							templateUrl: 'static/partials/research.main.task.html',
							controller: 'taskCtrl'
						}
					},
					ncyBreadcrumb: {
						label: 'Task Details',
						parent: 'research.dataset'
					}
				});
			// Set default fallback URL
			$urlRouterProvider.otherwise('/');
}]);

