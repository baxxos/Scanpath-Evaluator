// Created by Baxos on 2.11.2016.

var gazerApp = angular.module('gazerApp');

gazerApp.config(function($stateProvider, $urlRouterProvider) {
	$stateProvider
		.state("index", {
			url: "/index",
			controller: "",
			templateUrl: "../static/partials/landing.html",
			ncyBreadcrumb: {
				label: "Home"
			}
		})
		.state("profile", {
			url: "/profile",
			controller: "",
			templateUrl: "../static/partials/profile.html",
			ncyBreadcrumb: {
				label: "Profile",
				parent: "index"
			}
		});

	$urlRouterProvider.otherwise("/index");
});

