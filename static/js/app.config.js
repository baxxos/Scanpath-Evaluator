// Created by Baxos on 2.11.2016.
'use strict';

angular.module('gazerApp')
	.config(['$stateProvider', '$urlRouterProvider', '$locationProvider',
		function($stateProvider, $urlRouterProvider, $locationProvider) {
			$stateProvider
				.state("index", {
					url: "/",
					controller: 'customCtrl',
					templateUrl: 'static/partials/landing.html',
					ncyBreadcrumb: {
						label: 'Home'
					}
				})
				.state('profile', {
					url: '/profile',
					controller: 'customCtrl',
					templateUrl: 'static/partials/profile.html',
					ncyBreadcrumb: {
						label: 'Profile',
						parent: 'index'
					}
				})
				.state('research', {
					url: '/research',
					controller: 'customCtrl',
					templateUrl: 'static/partials/research.html',
					ncyBreadcrumb: {
						label: 'Research',
						parent: 'index'
					}
				});
			$urlRouterProvider.otherwise('/');
}]);

