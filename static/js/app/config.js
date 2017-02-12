'use strict';

// State machine for named states based on URL and (currently) unnamed corresponding views
angular.module('gazerApp')
	.config(['$stateProvider', '$urlRouterProvider', '$locationProvider',
		function($stateProvider, $urlRouterProvider) {
			$stateProvider
				.state("index", {
					url: "/",
					controller: 'DefaultCtrl',
					templateUrl: 'static/partials/landing.html',
					ncyBreadcrumb: {
						label: 'Home'
					}
				})
				.state('login', {
					url: '/login',
					controller: 'LoginCtrl',
					templateUrl: 'static/partials/login.html',
					ncyBreadcrumb: {
						label: 'Login',
						parent: 'index'
					}
				})
				.state('register', {
					url: '/register',
					controller: 'RegisterCtrl',
					templateUrl: 'static/partials/register.html',
					ncyBreadcrumb: {
						label: 'Register',
						parent: 'index'
					}
				})
				// State displaying static information about datasets and their tasks
				.state('research', {
					url: '/research',
					views: {
						'@': {
							controller: 'DefaultCtrl',
							templateUrl: 'static/partials/research.layout.html'
						},
						'left@research' : {
							controller: 'SidebarCtrl',
							templateUrl: 'static/partials/research.sidebar.html'
						},
						'right@research' : {
							templateUrl: 'static/partials/research.static.html'
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
							templateUrl: 'static/partials/research.dataset.html',
							controller: 'DatasetCtrl'
						}
					},
					ncyBreadcrumb: {
						label: 'Dataset details',
						parent: 'research'
					}
				})
				.state('research.datasetNew', {
					url: '/dataset-new',
					views: {
						'right@research': {
							templateUrl: 'static/partials/research.datasetNew.html',
							controller: 'DatasetFormCtrl'
						}
					},
					ncyBreadcrumb: {
						label: 'New dataset',
						parent: 'research'
					}
				})
				// State which allows to choose a task (sub-dataset) from the previously selected dataset
				.state('research.task', {
					url: '/task/:id',
					views: {
						'right@research': {
							templateUrl: 'static/partials/research.task.html',
							controller: 'TaskCtrl'
						}
					},
					ncyBreadcrumb: {
						label: 'Task details',
						parent: 'research'
					}
				});
			// Set default fallback URL
			$urlRouterProvider.otherwise('/');
}]);

