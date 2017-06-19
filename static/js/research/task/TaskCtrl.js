// Handles all scanpath data related actions such as AJAX calls etc.
angular.module('ScanpathEvaluator').controller('TaskCtrl', function($scope, $rootScope, $state, $http, $window, CanvasDrawService) {
	/*** DATA-HANDLING METHODS ***/
	$scope.getTaskData = function(taskId, userId) {
		$http({
			url: 'api/task',
			method: 'GET',
			params: {
				taskId: taskId
			}
		}).then(
			function(response) {
				// Update the task object with response data
				$scope.task.scanpaths = response.data.load.scanpaths;
				$scope.task.visuals = response.data.load.visuals;
				$scope.task.aois = response.data.load.aois;

				// For displaying breadcrumbs, etc.
				$scope.task.name = response.data.load.name;
				$scope.dataset.name = response.data.load.datasetName;

				// Load the canvas background image again to get its natural resolution
				$scope.canvasInfo.backgroundImg = new Image();
				// Callback that gets triggered when the img has completed loading (draw the returned data)
				$scope.canvasInfo.backgroundImg.onload = function() {
					// Draw returned data onto the default canvas
					$scope.canvasInfo.aois = redrawCanvas(
						$scope.canvas, $scope.ctx, $scope.canvasInfo,
						$scope.canvasInfo.backgroundImg, $scope.task.aois
					);
				};
				$scope.canvasInfo.backgroundImg.src = $scope.task.visuals.main;

				// Remember user action for drawing on modal canvas ('' is default)
				$scope.task.lastAction = '';
			},
			function(data) {
				console.error('Failed to get task data content.', data);
			}
		);
    };

    // Calculate average similarity in a common/custom scanpath similarity object provided by back-end as response
    var calcAvgSimToCommon = function(commonScanpathSimilarity) {
		var similarity = 0, total = 0;

		// Loop through all similarity values stored in the similarity object
		for(var scanpath in commonScanpathSimilarity) {
			similarity += commonScanpathSimilarity[scanpath];
			// Keep track of the total number of scanpaths as there is no keys.length in dict
			total++;
		}
		return similarity / total;
	};

	var getCommonScanpathDetails = function(algorithm) {
		// The algorithm specifies url to be used from the backend API - e.g. '/sta' or '/emine'
		$http({
			url: '/api/scanpath/' + algorithm,
			method: 'POST',
			data: {
				taskId: $scope.task.id,
				excludedScanpaths: $scope.task.excludedRows
			}
		}).then(
			function(response) {
				if(response.data.success) {
					// Get the common scanpath
					$scope.task.commonScanpath = response.data.load;
					// Get the similarity object
					var similarities = $scope.task.commonScanpath.similarity;
					// Get the average similarity of user scanpath to the common scanpath
					$scope.task.commonScanpath.avgSimToCommon = calcAvgSimToCommon(similarities);

					// Assign each user scanpath its similarity to the common scanpath
					$scope.task.scanpaths.forEach(function(actScanpath) {
						actScanpath.simToCommon = similarities[actScanpath.identifier];
					});

					// Remember user action for drawing on modal canvas
					$scope.task.lastAction = 'commonScanpath';

					// Draw the common scanpath on the default canvas
					$scope.canvasInfo.aois = drawFixationsAndAois(
						$scope.canvas, $scope.ctx, $scope.canvasInfo, $scope.canvasInfo.backgroundImg,
						$scope.task.aois, $scope.task.commonScanpath.fixations
					);
				}
				else {
					console.error(response.data.message);
				}
				// Enable the submit button regardless of the result
				setSubmitBtnDisabled(false);
			},
			function(data) {
				console.error('Failed to get common scanpath response from the server.', data);
				// Enable the submit button regardless of the response
				setSubmitBtnDisabled(false);
			}
		);
    };

	var getCustomScanpathDetails = function(customScanpathStr) {
		// Remove all whitespaces from the user input by regex
		customScanpathStr = customScanpathStr.replace(/\s/g, "");

		$http({
			url: '/api/scanpath/custom',
			method: 'POST',
			data: {
				customScanpath: customScanpathStr,
				taskId: $scope.task.id,
				excludedScanpaths: $scope.task.excludedRows
			}
		}).then(
			function(response) {
				if(response.data.success) {
					// Get the common scanpath
					$scope.task.customScanpath = response.data.load;
					// Get the similarity object
					var similarities = $scope.task.customScanpath.similarity;
					// Get the average similarity of each user scanpath to the common scanpath
					$scope.task.customScanpath.avgSimToCommon = calcAvgSimToCommon(similarities);

					// Assign each user scanpath its similarity to the common scanpath
					$scope.task.scanpaths.forEach(function(actScanpath) {
						actScanpath.simToCommon = similarities[actScanpath.identifier];
					});

					// Remember user action for drawing on modal canvas
					$scope.task.lastAction = 'customScanpath';

					// Draw the custom scanpath onto the default canvas
					$scope.canvasInfo.aois = drawFixationsAndAois(
						$scope.canvas, $scope.ctx, $scope.canvasInfo, $scope.canvasInfo.backgroundImg,
						$scope.task.aois, $scope.task.customScanpath.fixations
					);
				}
				else {
					console.error(response.data.message);
				}
				// Enable the submit button regardless of the result
				setSubmitBtnDisabled(false);
			},
			function(data) {
				console.error('Failed to get common scanpath response from the server.', data);
				// Enable the submit button regardless of the response
				setSubmitBtnDisabled(false);
			}
		);
    };

    /*** VIEW-HANDLING METHODS ***/
    // Collapses or expands all rows of the scanpath table
	$scope.toggleAllRows = function(toggleValue) {
		if(toggleValue === false) {
			$scope.expandedRows = {};
		}
		else {
			$scope.task.scanpaths.forEach(function(scanpath) {
				$scope.expandedRows[scanpath.identifier] = true;
			});
		}
	};

	// Performs the common/custom scanpath calculation based on the selected algorithm
	$scope.getScanpathTableData = function() {
		if ($scope.userInputs.isCustomScanpath && $scope.userInputs.customScanpathText) {
			setSubmitBtnDisabled(true);
			getCustomScanpathDetails($scope.userInputs.customScanpathText);
		}
		else if($scope.userInputs.commonScanpathAlg) {
			setSubmitBtnDisabled(true);
			getCommonScanpathDetails($scope.userInputs.commonScanpathAlg);
		}
	};

	// Function changes sorting base or inverts it when it's the same
    $scope.setSort = function(value) {
		if($scope.task.sortBy == value) {
			$scope.task.sortBy = '-' + $scope.task.sortBy;
		} else {
			$scope.task.sortBy = value;
		}
	};

	// Excludes (or includes) the scanpaths from the future dataset computations
	$scope.toggleRowExcluded = function(scanpath) {
		scanpath.excluded = !scanpath.excluded;

		if(scanpath.excluded) {
			$scope.task.excludedRows.push(scanpath.identifier)
		}
		else {
			// Remove given row identifier from the array of excluded ones
			for(var i = $scope.task.excludedRows.length - 1; i >= 0; i--) {  // Backward iteration due to splice()
				if($scope.task.excludedRows[i] == scanpath.identifier) {
					$scope.task.excludedRows.splice(i, 1);
					break;
				}
			}
		}
	};

	// Removes the excluded flag from all available scanpaths
	$scope.setAllRowsExcludedValue = function(val) {
		// Re-initialize the excluded scanpaths array
		$scope.task.excludedRows = [];

		// Make sure the value is really a boolean (e.g. not "0" which would be true)
		if(typeof(val) === "boolean") {
			$scope.task.scanpaths.forEach(function(scanpath) {
				scanpath.excluded = val;

				// If the scanpath is about to be excluded
				if(val) {
					$scope.task.excludedRows.push(scanpath.identifier);
				}
			});
		}
	};

	$scope.viewCanvasAsImage = function() {
		$window.open($scope.canvas.toDataURL('image/jpeg', 0.5), '_blank');
	};

	$scope.drawIndividualScanpath = function(scanpath) {
		// Remember the action & scanpath data for drawing on modal canvas later
		$scope.task.lastAction = 'individualScanpath';
		$scope.task.individualScanpath = scanpath;

		// Draw the individual scanpath onto the default canvas
		$scope.canvasInfo.aois = drawFixationsAndAois(
			$scope.canvas, $scope.ctx, $scope.canvasInfo, $scope.canvasInfo.backgroundImg,
			$scope.task.aois, scanpath.fixations
		);
	};

	$scope.clearFixations = function() {
		// Remember the action & scanpath data for drawing on modal canvas later
		$scope.task.lastAction = '';

		// Reset any previously calculated individual, custom and common scanpaths
		$scope.task.individualScanpath = {};
		$scope.task.commonScanpath = {};
		$scope.task.customScanpath = {};

		$scope.canvasInfo.aois = redrawCanvas(
			$scope.canvas, $scope.ctx, $scope.canvasInfo,
			$scope.canvasInfo.backgroundImg, $scope.task.aois
		);
	};

	// CSV export utility method
	$scope.getTableExport = function() {
		var exportArray = [];

		$scope.task.scanpaths.forEach(function(actScanpath) {
			exportArray.push({
				id: actScanpath.identifier,
				totalFixations: actScanpath.fixations.length,
				mostSimilarTo: actScanpath.minSimilarity.identifier,
				mostSimilarVal: actScanpath.minSimilarity.value,
				leastSimilarTo: actScanpath.maxSimilarity.identifier,
				leastSimilarVal: actScanpath.maxSimilarity.value,
				simToCommon: actScanpath.simToCommon ? actScanpath.simToCommon : 'N/A',
				fixations: actScanpath.fixations.toString()
			});
		});
		return exportArray;
	};

	// Shows/hides the selected algorithm description panel
	$scope.toggleAlgDescription = function() {
		$scope.guiParams.showAlgDesc = !$scope.guiParams.showAlgDesc;
		$scope.guiParams.algDescText = ($scope.guiParams.showAlgDesc ? 'Hide' : 'Show') + ' description';
	};

	var setSubmitBtnDisabled = function(val) {
		if(val != undefined) {
			$scope.guiParams.isProcessing = val;
			$scope.guiParams.submitBtnText = (val ? 'Processing' : 'Submit');
		}
		else {
			console.error('Submit button value is undefined.')
		}
	};

	/*** CANVAS CONTROLS ***/
	// Returns a set of random colors if none has been generated for the specified source canvas yet
	var getAoiColors = function(aois) {
		return $scope.canvasInfo.aoiColors
			? $scope.canvasInfo.aoiColors
			: randomColor({ luminosity: 'bright', count: aois.length });
	};

	// Canvas manipulation
	var initCanvasDefault = function(canvasId) {
		// Fetch canvas elements in a non-angular way://
		$scope.canvas = document.getElementById(canvasId);
    	$scope.ctx = $scope.canvas.getContext('2d');

		// Basic canvas setup
		$scope.canvasInfo = CanvasDrawService.getDefaultCanvasInfo();

		$scope.ctx.globalAlpha = 1.0;
		$scope.ctx.beginPath();
	};

	var initCanvasModal = function(canvasId) {
		// Fetch modal canvas elements in a non-angular way://
		$scope.canvasModal = document.getElementById(canvasId);
    	$scope.ctxModal = $scope.canvasModal.getContext('2d');

		$scope.ctxModal.globalAlpha = 1.0;
		$scope.ctxModal.beginPath();
	};

	// Redraws the specified canvas with AOIs and also fixations if provided
	var redrawCanvas = function(canvas, ctx, canvasInfo, backgroundImage, aois, fixations) {
		// Make canvas resolution match its real size
		canvas.width = backgroundImage.naturalWidth;
		canvas.height = backgroundImage.naturalHeight;

		// Set of colors to be used for drawing AOIs - default canvas needs to be checked first (not the modal one)
		$scope.canvasInfo.aoiColors = getAoiColors($scope.task.aois);

		// If fixations are specified draw them (includes drawing AOIs implicitly)
		if(fixations) {
			return drawFixationsAndAois(canvas, ctx, canvasInfo, backgroundImage, $scope.task.aois, fixations);
		}
		// Else draw only AOIs on the desired canvas
		else {
			return CanvasDrawService.drawAois(canvas, ctx, canvasInfo, backgroundImage, aois);
		}
	};

	// Utility method to de-bloat the scope of frequent drawing calls
	var drawFixationsAndAois = function(canvas, ctx, canvasInfo, backgroundImage, aois, fixations) {
		var drawnAois = CanvasDrawService.drawAois(canvas, ctx, canvasInfo, backgroundImage, aois);

		// If the last action was not a request for individual scanpath drawing, reset the individual scanpath object
		if($scope.task.lastAction != 'individualScanpath') {
			$scope.task.individualScanpath = {};
		}

		// Draw new fixation circles on the top of the canvas
		if(!CanvasDrawService.drawFixations(canvas, ctx, canvasInfo, drawnAois, fixations, '#44f')) {
			// If the process failed, draw back only the AOIs
			return CanvasDrawService.drawAois(canvas, ctx, canvasInfo, backgroundImage, aois);
		}

		return drawnAois;
	};

	$scope.toggleCanvasModal = function() {
		$scope.guiParams.showCanvasModal = !$scope.guiParams.showCanvasModal;

		if($scope.guiParams.showCanvasModal) {
			// Redraw the modal canvas when the element is revealed and its true size is known
			var fixations = undefined;

			// If last user action was COMMON SCANPATH calculation, we want to mirror it on the modal canvas
			if($scope.task.lastAction == 'commonScanpath') {
				fixations = $scope.task.commonScanpath.fixations;
			}
			// If last user action was CUSTOM SCANPATH scanpath calculation, we want to mirror it on the modal canvas
			else if($scope.task.lastAction == 'customScanpath') {
				fixations = $scope.task.customScanpath.fixations;
			}
			// If last user action was INDIVIDUAL SCANPATH calculation, we want to mirror it on the modal canvas
			else if($scope.task.lastAction == 'individualScanpath') {
				fixations = $scope.task.individualScanpath.fixations;
			}

			$scope.canvasInfo.aoisModal = redrawCanvas(
				$scope.canvasModal, $scope.ctxModal, $scope.canvasInfo,
				$scope.canvasInfo.backgroundImg, $scope.task.aois, fixations
			);
		}
	};

    var initController = function() {
		// Forward declaration of similarity objects to prevent IDE warnings. May be omitted later.
		$scope.task = {
			// Store the actual task ID from URL (ui-router functionality)
			id: $state.params.taskId,
			datasetId: $state.params.datasetId,
			scanpaths: [],
			// Scanpaths temporarily excluded from all computations
			excludedRows: [],
			// Sort the data based on a default column
			sortBy: 'identifier',
			// Remember last user action to determine modal canvas content
			lastAction: ''
		};

		// For storing parent dataset data
		$scope.dataset = {};

		// Variables controlling hide/show/content properties of some GUI elements
		$scope.guiParams = {
			// Disable user inputs while waiting for AJAX response
			isProcessing: false,
			// Hide the zoomed in (modal) canvas element and AOI legend
			showCanvasModal: false,
			// Misc
			submitBtnText: 'Submit',
			algDescText: 'Show description',
			showAoiLegend: false,
			showAlgDesc: false
		};

		// User ng-model inputs grouped together in one object
		$scope.userInputs = {
			// Initializing to false/undef to get rid of IDE 'unresolved variable' warnings
			isCustomScanpath: false,  // User wants to provide his own common scanpath
			customScanpathText: undefined,  // Users own common scanpath content
			commonScanpathAlg: undefined  // Algorithm selected for common scanpath calculation (val = AJAX url)
		};

		// Initialize the canvas elements
		initCanvasDefault('scanpathCanvas');
		initCanvasModal('scanpathCanvasModal');

		// Get the basic scanpath data (mutual similarity etc.)
		$scope.getTaskData($scope.task.id, $rootScope.globals.currentUser.id);

		// Scanpath table rows expanding/collapsing controls
		$scope.expandedRows = {};
	};
	// Perform view initialization
	initController();
});
