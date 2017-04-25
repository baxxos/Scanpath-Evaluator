// Handles all scanpath data related actions such as AJAX calls etc.
angular.module('ScanpathEvaluator').controller('AlgCompareCtrl', function($scope, $rootScope, $state, $http, $window, CanvasDrawService) {
	/*** DATA-HANDLING METHODS (mostly don't modify the $scope) ***/
	$scope.getTaskData = function(taskId, userId) {
		$http({
			url: 'api/task',
			method: 'GET',
			params: {
				taskId: taskId
			}
		}).then(
			function(response) {
				$scope.task.scanpaths = response.data.load.scanpaths;
				$scope.task.visuals = response.data.load.visuals;
				$scope.task.aois = response.data.load.aois;
				$scope.task.name = response.data.load.name;

				// Load the canvas background image again to get its natural resolution
				$scope.canvasInfo.backgroundImg = new Image();
				// Callback that gets triggered when the img has completed loading (draw the returned data)
				$scope.canvasInfo.backgroundImg.onload = function() {
					// Draw returned data onto the default canvas
					$scope.canvasInfo.aois = redrawCanvas(
						$scope.canvas, $scope.ctx, $scope.canvasInfo,
						$scope.canvasInfo.backgroundImg, $scope.task.aois
					);
					// Run the cross-comparison
					$scope.getAlgTableData();
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
			// Keep track of the total number of scanpaths as there is no keys.length in JS
			total++;
		}
		return similarity / total;
	};

	// Calculate average similarity of multiple common scanpaths
	var calcAvgTotalSimilarity = function(algResults) {
		var similaritySum = 0, total = 0;

		for(var i = 0; i < algResults.length; i++) {
			// We don't want to consider algorithms which failed to find a common scanpath
			if(algResults[i].simToCommon == 0) {
				continue;
			}

			similaritySum += algResults[i].simToCommon;
			// Keep track of the total number of scanpaths as we might skip some
			total++;
		}
		return similaritySum/total;
	};

	// Calculate average length of multiple (common) scanpaths
	var calcAvgTotalLength = function(algResults) {
		var lengthSum = 0, total = 0;

		for(var i = 0; i < algResults.length; i++) {
			// We don't want to consider algorithms which failed to find a common scanpath
			if(algResults[i].simToCommon == 0) {
				continue;
			}

			lengthSum += algResults[i].fixations.length;
			// Keep track of the total number of scanpaths as we might skip some
			total++;
		}
		return lengthSum/total;
	};

	/* Updates the current set of algorithm results with data from a new one with the same format. We are not replacing
	 * the object/array directly since we want to preserve some original data (e.g. which rows are excluded) */
	var getUpdatedTableData = function(responseData, tableData) {
		for(var i = 0; i < responseData.length; i++) {
			var newAlgResult = responseData[i];

			// Look for a match between new and current results identifiers
			for(var j = 0; j < tableData.length; j++) {
				var oldAlgResult = tableData[j];

				if(newAlgResult.identifier == oldAlgResult.identifier) {
					// Preserve the 'included/excluded' value
					newAlgResult.excluded = oldAlgResult.excluded;
					// Replace data by the new result
					tableData[j] = newAlgResult;
					break;
				}
			}
		}
		return tableData;
	};

    /*** VIEW-HANDLING METHODS (directly modify the $scope) ***/
    // Collapses or expands all rows of the algorithm results table
	$scope.toggleAllRows = function(toggleValue) {
		if(toggleValue === false) {
			$scope.expandedRows = {};
		}
		else {
			$scope.task.algResults.forEach(function(algResult) {
				$scope.expandedRows[algResult.identifier] = true;
			});
		}
	};

	// Performs the common/custom scanpath calculation based on the selected algorithm
	$scope.getAlgTableData = function() {
		setSubmitBtnDisabled(true);

		$http({
			url: '/api/scanpath/alg-compare',
			method: 'POST',
			data: {
				taskId: $scope.task.id,
				excludedAlgs: $scope.task.excludedRows
			}
		}).then(
			function(response) {
				if(response.data.success) {
					// Check if the table data object needs replacing (first comparison call) or updating (later calls)
					if (!$scope.task.algResults || !$scope.task.algResults.length) {
						$scope.task.algResults = response.data.load;
					}
					else {
						$scope.task.algResults = getUpdatedTableData(response.data.load, $scope.task.algResults)
					}

					// Process the response data - calculate achieved average similarity for all algorithms etc.
					for(var algName in $scope.task.algResults) {
						// Represents currently processed algorithm result
						var algResult = $scope.task.algResults[algName];

						// If the algorithm computed common scanpath successfully, calculate the achieved avg similarity
						algResult.simToCommon =
							(algResult.fixations.length > 0 ? calcAvgSimToCommon(algResult.similarity) : 0);

						// Assign a random color for future drawings on canvas (seed ensures distinguishable colors)
						algResult.color = randomColor({ luminosity: 'dark', seed: algResult.identifier });
					}

					$scope.task.avgTotalSimilarity = calcAvgTotalSimilarity($scope.task.algResults);
					$scope.task.avgTotalLength = calcAvgTotalLength($scope.task.algResults);

					// Remember user action for drawing on modal canvas
					$scope.task.lastAction = 'algComparison';

					// Draw all the common scanpaths onto the default canvas
					$scope.canvasInfo.aois = drawScanpathsAndAois(
						$scope.canvas, $scope.ctx, $scope.canvasInfo, $scope.canvasInfo.backgroundImg,
						$scope.task.aois, $scope.task.algResults
					);
				}
				else {
					console.error(response.data.message);
				}
				// Enable the submit button regardless of the result
				setSubmitBtnDisabled(false);
			},
			function(data) {
				console.error('Failed to get response from the server.', data);
				// Enable the submit button regardless of the response
				setSubmitBtnDisabled(false);
			}
		);
	};

	// Function changes sorting base or inverts it when it's the same
    $scope.setSort = function(value) {
		if($scope.task.sortBy == value) {
			$scope.task.sortBy = '-' + $scope.task.sortBy;
		} else {
			$scope.task.sortBy = value;
		}
	};

	// Excludes (or includes) the selected algorithms from the future dataset computations
	$scope.toggleRowExcluded = function(rowData) {
		rowData.excluded = !rowData.excluded;

		if(rowData.excluded) {
			$scope.task.excludedRows.push(rowData.identifier)
		}
		else {
			// Remove given row identifier from the array of excluded ones
			for(var i = $scope.task.excludedRows.length - 1; i >= 0; i--) {  // Backward iteration due to splice()
				if($scope.task.excludedRows[i] == rowData.identifier) {
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
			$scope.task.algResults.forEach(function(resultRow) {
				resultRow.excluded = val;

				// If the scanpath is about to be excluded
				if(val) {
					$scope.task.excludedRows.push(resultRow.identifier);
				}
			});
		}
	};

	$scope.viewCanvasAsImage = function() {
		window.open($scope.canvas.toDataURL('image/jpeg', 0.5), '_blank');
	};

	$scope.drawIndividualScanpath = function(scanpath) {
		// Remember the action & scanpath data for drawing on modal canvas later
		$scope.task.lastAction = 'individualScanpath';
		$scope.task.individualScanpath = scanpath;

		// Draw the individual scanpath onto the default canvas
		$scope.canvasInfo.aois = drawScanpathsAndAois(
			$scope.canvas, $scope.ctx, $scope.canvasInfo, $scope.canvasInfo.backgroundImg,
			$scope.task.aois, [scanpath]
		);
	};

	$scope.clearFixations = function() {
		// Remember the action & scanpath data for drawing on modal canvas later
		$scope.task.lastAction = '';

		// Reset any previously calculated/drawn individual scanpaths
		$scope.task.individualScanpath = {};

		// Clear all previous scanpath calculations
		for(var i = 0; i < $scope.task.algResults.length; i++) {
			$scope.task.algResults[i].fixations = [];
			$scope.task.algResults[i].simToCommon = 0;
		}

		// Reset the average similarity/length results
		$scope.task.avgTotalSimilarity = undefined;
		$scope.task.avgTotalLength = undefined;

		$scope.canvasInfo.aois = redrawCanvas(
			$scope.canvas, $scope.ctx, $scope.canvasInfo,
			$scope.canvasInfo.backgroundImg, $scope.task.aois
		);
	};

	// CSV export utility method
	$scope.getTableExport = function() {
		var exportArray = [];

		$scope.task.algResults.forEach(function(algResult) {
			exportArray.push({
				name: algResult.identifier,
				totalFixations: algResult.fixations.length,
				avgSimilarity: algResult.simToCommon ? algResult.simToCommon : 'N/A',
				fixations: algResult.fixations.toString()
			});
		});
		return exportArray;
	};

	var setSubmitBtnDisabled = function(val) {
		if(val != undefined) {
			$scope.guiParams.isProcessing = val;
			$scope.guiParams.submitBtnText = (val ? 'Processing' : 'Cross-compare');
		}
		else {
			console.error('Submit button value is undefined.')
		}
	};

	/*** CANVAS CONTROLS (might directly modify the $scope) ***/
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
	var redrawCanvas = function(canvas, ctx, canvasInfo, backgroundImage, aois, scanpathsToDraw) {
		// Make canvas resolution match its real size
		canvas.width = backgroundImage.naturalWidth;
		canvas.height = backgroundImage.naturalHeight;

		// Set of colors to be used for drawing AOIs - default canvas needs to be checked first (not the modal one)
		$scope.canvasInfo.aoiColors = getAoiColors($scope.task.aois);

		// If fixations are specified draw them (includes drawing AOIs implicitly)
		if(scanpathsToDraw) {
			return drawScanpathsAndAois(canvas, ctx, canvasInfo, backgroundImage, $scope.task.aois, scanpathsToDraw);
		}
		// Else draw only AOIs on the desired canvas
		else {
			return CanvasDrawService.drawAois(canvas, ctx, canvasInfo, backgroundImage, aois);
		}
	};

	// Utility method to de-bloat the scope of frequent drawing calls
	var drawScanpathsAndAois = function(canvas, ctx, canvasInfo, backgroundImage, aois, scanpathsToDraw) {
		var drawnAois = CanvasDrawService.drawAois(canvas, ctx, canvasInfo, backgroundImage, aois);

		// If the last action was not a request for individual scanpath drawing, reset the individual scanpath object
		if($scope.task.lastAction != 'individualScanpath') {
			$scope.task.individualScanpath = {};
		}

		// Draw all non-excluded common scanpaths on the canvas
		for(var i = 0; i < scanpathsToDraw.length; i++) {
			// Draw new fixation circles on the top of the canvas
			if (!CanvasDrawService.drawFixations(canvas, ctx, canvasInfo, drawnAois,
					scanpathsToDraw[i].fixations, scanpathsToDraw[i].color)) {
				// If the process failed, draw back only the AOIs
				return CanvasDrawService.drawAois(canvas, ctx, canvasInfo, backgroundImage, aois);
			}
		}

		return drawnAois;
	};

	$scope.toggleCanvasModal = function() {
		$scope.guiParams.showCanvasModal = !$scope.guiParams.showCanvasModal;

		if($scope.guiParams.showCanvasModal) {
			// Redraw the modal canvas when the element is revealed and its true size is known
			var scanpathsToDraw = undefined;

			// If last user action was COMMON SCANPATH COMPARISON drawing, we want to mirror it on the modal canvas
			if($scope.task.lastAction == 'algComparison') {
				scanpathsToDraw = $scope.task.algResults;
			}
			// If last user action was INDIVIDUAL SCANPATH drawing, we want to mirror it on the modal canvas
			else if($scope.task.lastAction == 'individualScanpath') {
				scanpathsToDraw = [$scope.task.individualScanpath];
			}

			$scope.canvasInfo.aoisModal = redrawCanvas(
				$scope.canvasModal, $scope.ctxModal, $scope.canvasInfo,
				$scope.canvasInfo.backgroundImg, $scope.task.aois, scanpathsToDraw
			);
		}
	};

    var initController = function() {
		// Forward declaration of similarity objects to prevent IDE warnings. May be omitted later.
		$scope.task = {
			// Store the actual task ID from URL (ui-router functionality)
			id: $state.params.taskId,
			scanpaths: [],
			// Scanpaths temporarily excluded from all computations
			excludedRows: [],
			// Sort the data based on a default column
			sortBy: 'identifier',
			// Remember last user action to determine modal canvas content
			lastAction: ''
		};

		// Variables controlling hide/show/content properties of some GUI elements
		$scope.guiParams = {
			// Disable user inputs while waiting for AJAX response
			isProcessing: false,
			// Hide the zoomed in (modal) canvas element and AOI legend
			showCanvasModal: false,
			// Misc
			submitBtnText: 'Submit',
			showAoiLegend: false
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
