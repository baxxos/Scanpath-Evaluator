'use strict';

// State machine for named states based on URL and (currently) unnamed corresponding views
angular.module('ScanpathEvaluator')
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
							templateUrl: 'static/partials/research/layout.html'
						},
						'left@research' : {
							controller: 'SidebarCtrl',
							templateUrl: 'static/partials/research/sidebar.html'
						},
						'right@research' : {
							templateUrl: 'static/partials/research/static.html'
						}
					},
					ncyBreadcrumb: {
						label: 'Research',
						parent: 'index'
					}
				})
				// State which allows to choose a dataset for an UX experiment stored in the DB
				.state('research.dataset', {
					url: '/dataset/:datasetId',
					views: {
						'right@research': {
							templateUrl: 'static/partials/research/dataset/dataset.html',
							controller: 'DatasetCtrl'
						}
					},
					ncyBreadcrumb: {
						label: '{{ dataset.name ? dataset.name : "Dataset detail"}}',
						parent: 'research'
					}
				})
				.state('research.datasetNew', {
					url: '/dataset-new',
					views: {
						'right@research': {
							templateUrl: 'static/partials/research/dataset/datasetNew.html',
							controller: 'DatasetNewCtrl'
						}
					},
					ncyBreadcrumb: {
						label: 'New dataset',
						parent: 'research'
					}
				})
				// State which allows to choose a task (sub-dataset) from the previously selected dataset
				.state('research.dataset.task', {
					url: '/task/:taskId',
					views: {
						'right@research': {
							templateUrl: 'static/partials/research/task/task.html',
							controller: 'TaskCtrl'
						}
					},
					ncyBreadcrumb: {
						label: '{{ task.name ? task.name : "Task detail" }}',
						parent: 'research.dataset'
					}
				})
				// State which performs a run of all common scanpath algorithms on a chosen dataset task
				.state('research.dataset.task.compare', {
					url: '/alg-compare',
					views: {
						'right@research': {
							templateUrl: 'static/partials/research/task/algCompare.html',
							controller: 'AlgCompareCtrl'
						}
					},
					ncyBreadcrumb: {
						label: 'Algorithm comparison',
						parent: 'research.dataset.task'
					}
				});
			// Set default fallback URL
			$urlRouterProvider.otherwise('/');
}]);

