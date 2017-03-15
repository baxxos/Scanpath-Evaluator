// Handles all scanpath data related actions such as AJAX calls etc.
angular.module('gazerApp').controller('TaskCtrl', function($scope, $state, $http, $window, CanvasDrawService) {
	/*** DATA-HANDLING METHODS ***/
	$scope.getTaskScanpaths = function() {
		$http({
			url: 'get_task_data',
			method: 'GET',
			params: {
				taskId: $scope.task.id
			}
		}).then(
			function(response) {
				$scope.task.scanpaths = response.data.load.scanpaths;
				$scope.task.visuals = response.data.load.visuals;
				$scope.task.aois = response.data.load.aois;

				// Load the canvas background image again to get its natural resolution
				$scope.canvasInfo.backgroundImg = new Image();
				// Callback that gets triggered when the img has completed loading (draw the returned data)
				$scope.canvasInfo.backgroundImg.onload = function() {
					// Draw returned data onto the basic canvas
					$scope.canvasInfo.aois = redrawCanvas(
						$scope.canvas, $scope.canvasWrapper, $scope.ctx, $scope.canvasInfo,
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
		for (var scanpath in commonScanpathSimilarity) {
			similarity += commonScanpathSimilarity[scanpath];
			// Keep track of the total number of scanpaths as there is no keys.length in dict
			total++;
		}
		return similarity / total;
	};

	var getCommonScanpathDetails = function() {
		$http({
			url: '/sta',
			method: 'POST',
			data: {
				taskId: $scope.task.id,
				excludedScanpaths: $scope.task.excludedScanpaths
			}
		}).then(
			function(response) {
				// Get the common scanpath
				$scope.task.commonScanpath = response.data;
				// Get the similarity object
				var similarities = $scope.task.commonScanpath.similarity;
				// Get the average similarity of user scanpath to the common scanpath
				$scope.task.commonScanpath.avgSimToCommon = calcAvgSimToCommon(similarities);

				// Assign each user scanpath its similarity to the common scanpath
				for (var index in $scope.task.scanpaths) {
					var act_scanpath = $scope.task.scanpaths[index];
					act_scanpath.simToCommon = similarities[act_scanpath.identifier];
				}

				// Draw the common scanpath on the default canvas
				$scope.canvasInfo.aois = drawFixationsAndAois(
					$scope.canvas, $scope.ctx, $scope.canvasInfo, $scope.canvasInfo.backgroundImg,
					$scope.task.aois, $scope.task.commonScanpath.fixations
				);
				// Remember user action for drawing on modal canvas
				$scope.task.lastAction = 'commonScanpath'
			},
			function(data) {
				console.error('Failed to get common scanpath response from the server.', data);
			}
		);
    };

	var getCustomScanpathDetails = function(customScanpathStr) {
		// Remove all whitespaces from the user input by regex
		customScanpathStr = customScanpathStr.replace(/\s/g, "");

		$http({
			url: '/custom',
			method: 'POST',
			data: {
				customScanpath: customScanpathStr,
				taskId: $scope.task.id,
				excludedScanpaths: $scope.task.excludedScanpaths
			}
		}).then(
			function(response) {
				if(response.data.success == true) {
					// Get the common scanpath
					$scope.task.customScanpath = response.data.load;
					// Get the similarity object
					var similarities = $scope.task.customScanpath.similarity;
					// Get the average similarity of each user scanpath to the common scanpath
					$scope.task.customScanpath.avgSimToCommon = calcAvgSimToCommon(similarities);

					// Assign each user scanpath its similarity to the common scanpath
					for (var index in $scope.task.scanpaths) {
						var act_scanpath = $scope.task.scanpaths[index];
						act_scanpath.simToCommon = similarities[act_scanpath.identifier];
					}

					// Draw the custom scanpath onto the default canvas
					$scope.canvasInfo.aois = drawFixationsAndAois(
						$scope.canvas, $scope.ctx, $scope.canvasInfo, $scope.canvasInfo.backgroundImg,
						$scope.task.aois, $scope.task.customScanpath.fixations
					);
					// Remember user action for drawing on modal canvas
					$scope.task.lastAction = 'customScanpath'
				}
				else {
					console.error(response.data.message);
				}
			},
			function(data) {
				console.error('Failed to get common scanpath response from the server.', data);
			}
		);
    };

    /*** VIEW-HANDLING METHODS ***/
	$scope.toggleAllRows = function(toggleValue) {
		if(toggleValue == false) {
			$scope.expanded = {};
		}
		else {
			for (var i = 0; i < $scope.task.scanpaths.length; i++) {
				var id = $scope.task.scanpaths[i].identifier;
				$scope.expanded[id] = true;
			}
		}
	};

	$scope.fillTableDetails = function() {
		if ($scope.customScanpath && $scope.customScanpathText) {
			getCustomScanpathDetails($scope.customScanpathText);
		}
		else {
			getCommonScanpathDetails();
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
	$scope.toggleScanpathExcluded = function(scanpath) {
		scanpath.excluded = !scanpath.excluded;

		if(scanpath.excluded) {
			$scope.task.excludedScanpaths.push(scanpath.identifier)
		}
		else {
			// Remove all ocurrencies of the given scanpath in the array of excluded ones
			for(var i = 0; i < $scope.task.excludedScanpaths.length; i++) {
				if($scope.task.excludedScanpaths[i] == scanpath.identifier) {
					$scope.task.excludedScanpaths.splice(i, 1);
				}
			}
		}
	};

	// Removes the excluded flag from all available scanpaths
	$scope.setAllScanpathsValue = function(val) {
		// Re-initialize the excluded scanpaths array
		$scope.task.excludedScanpaths = [];

		// Make sure the value is really a boolean (e.g. not "0" which would be true)
		if(typeof(val) === "boolean") {
			$scope.task.scanpaths.forEach(function(scanpath) {
				scanpath.excluded = val;

				// If the scanpath is about to be excluded
				if(val) {
					$scope.task.excludedScanpaths.push(scanpath.identifier);
				}
			});
		}
	};

	$scope.viewCanvasAsImage = function() {
		window.open($scope.canvas.toDataURL('image/jpeg', 0.5), '_blank');
	};

	/*** CANVAS CONTROLS ***/
	// Returns a set of random colors if none has been generated for the specified source canvas yet
	var getAoiColors = function(aois) {
		return $scope.canvasInfo.colors
			? $scope.canvasInfo.colors
			: randomColor({ luminosity: 'bright', count: aois.length });
	};

	// Canvas manipulation
	var initCanvas = function(canvasId, canvasWrapperId) {
		// Fetch canvas elements in a non-angular way://
		$scope.canvas = document.getElementById(canvasId);
		$scope.canvasWrapper = document.getElementById(canvasWrapperId);
    	$scope.ctx = $scope.canvas.getContext('2d');

		// Basic canvas setup
		$scope.canvasInfo = {
			fontSize: 36,
			lineWidth: 8,
			scale: 1,
			offset: 0,
			aois: {}, // Serves for accessing the aois after drawing (e.g. for common scanpath displaying)
			aoisModal: {}
		};

		$scope.ctx.globalAlpha = 1.0;
		$scope.ctx.beginPath();
	};

	var initCanvasModal = function(canvasId, canvasWrapperId) {
		// Fetch modal canvas elements in a non-angular way://
		$scope.canvasModal = document.getElementById(canvasId);
		$scope.canvasModalWrapper = document.getElementById(canvasWrapperId);
    	$scope.ctxModal = $scope.canvasModal.getContext('2d');

		$scope.ctxModal.globalAlpha = 1.0;
		$scope.ctxModal.beginPath();
	};

	// Redraws the specified canvas with AOIs and also fixations if provided
	var redrawCanvas = function(canvas, canvasWrapper, ctx, canvasInfo, backgroundImage, aois, fixations) {
		// Make canvas resolution match its real size
		canvas.width = backgroundImage.naturalWidth;
		canvas.height = backgroundImage.naturalHeight;

		// Set of colors to be used for drawing AOIs - default canvas needs to be checked first (not the modal one)
		$scope.canvasInfo.colors = getAoiColors($scope.task.aois);

		// If fixations are specified draw them (includes drawing AOIs implicitly)
		if(fixations) {
			return drawFixationsAndAois(canvas, ctx, canvasInfo, backgroundImage, $scope.task.aois, fixations);
		}
		// Else draw only AOIs on the desired canvas
		else {
			return CanvasDrawService.drawAois(canvas, ctx, canvasInfo, backgroundImage, aois);
		}
	};

	var drawFixations = function(canvas, ctx, canvasInfo, drawnAois, scanpath) {
		for(var i = 1; i < scanpath.length; i++) {
			// Fix for user-submitted common scanpath - the AOI might not be in the actual aoi set
			if(CanvasDrawService.drawSaccade(
				ctx, canvasInfo, drawnAois, scanpath[i - 1], scanpath[i]) === false) {
				return false;
			}
        }

        /* Normalize the fixation circles to a maximum size of 1/10 of the corresponding canvas
         * (max circle radius equal to 1/20 of canvas width). */
        var maxCircleRadius = canvas.width / 20;
		var minCircleRadius = canvasInfo.fontSize / 2;
        var fixationLengths = scanpath.map(function(fixation) { return fixation[1]; });
		var sizeRatio = Math.max.apply(Math, fixationLengths) / maxCircleRadius;

		sizeRatio = (sizeRatio > 0 ? sizeRatio : 1);

		// Draw a fixation circle in the approximate center of the corresponding AOI box
		scanpath.forEach(function(fixation, index) {
			/* If there is no data about fixation length (e.g. user-submitted common scanpath) then set all circle
			 * sizes equal to the half of the maximum circle radius */
			var fixationRadius = (fixation[1] ? fixation[1] : (maxCircleRadius / 2));
			// Normalize the values by previously computed ratio
			fixationRadius /= sizeRatio;

			var fixationCircle = {
				x: drawnAois[fixation[0]].x + (drawnAois[fixation[0]].xLen / 2),
				y: drawnAois[fixation[0]].y + (drawnAois[fixation[0]].yLen / 2),
				// Minimum readable circle size radius must be at least equal to the half of the font size
				r: (fixationRadius >= (minCircleRadius) ? fixationRadius : (minCircleRadius))
			};

			CanvasDrawService.drawCircle(ctx, fixationCircle, '#000', canvasInfo.lineWidth / 2, '#44f');

			// Draw a label (centering is based on the fontSize and stroke line width)
			ctx.fillStyle = '#fff';
			ctx.lineWidth = canvasInfo.lineWidth;
			ctx.fillText(
				(index + 1).toString(),
				fixationCircle.x,
				fixationCircle.y + (canvasInfo.fontSize / 2) - ctx.lineWidth
			);
		});
    };

	// Utility method to de-bloat the scope of frequent calls
	var drawFixationsAndAois = function(canvas, ctx, canvasInfo, backgroundImage, aois, fixations) {
		var drawnAois = CanvasDrawService.drawAois(canvas, ctx, canvasInfo, backgroundImage, aois);

		// Draw new fixation circles on the top of the canvas
		if(drawFixations(canvas, ctx, canvasInfo, drawnAois, fixations) === false) {
			// If the process failed, draw back the AOIs
			return CanvasDrawService.drawAois(canvas, ctx, canvasInfo, backgroundImage, aois);
		}

		return drawnAois;
	};

	$scope.toggleCanvasModal = function() {
		$scope.showCanvasModal = !$scope.showCanvasModal;

		if($scope.showCanvasModal == true) {
			// Redraw the modal canvas when the element is revealed and its true size is known
			var fixations = undefined;

			// If last user action was common scanpath calculation, we want to repeat it on the modal canvas
			if($scope.task.lastAction == 'commonScanpath') {
				fixations = $scope.task.commonScanpath.fixations;
			}
			// If last user action was custom scanpath calculation, we want to repeat it on the modal canvas
			else if($scope.task.lastAction == 'customScanpath') {
				fixations = $scope.task.customScanpath.fixations;
			}

			$scope.canvasInfo.aoisModal = redrawCanvas(
				$scope.canvasModal, $scope.canvasModalWrapper, $scope.ctxModal, $scope.canvasInfo,
				$scope.canvasInfo.backgroundImg, $scope.task.aois, fixations
			);
		}
	};

    var initController = function() {
		// Forward declaration of similarity objects to prevent IDE warnings. May be omitted later.
		$scope.task = {
			// Store the actual task ID from URL (ui-router functionality)
			id: $state.params.id,
			scanpaths: [],
			// Scanpaths temporarily excluded from all computations
			excludedScanpaths: [],
			// Sort the data based on a default column
			sortBy: 'identifier',
			// Remember last user action to determine modal canvas content
			lastAction: ''
		};
		// Hide the zoomed in (modal) canvas element and AOI legend
		$scope.showCanvasModal = false;
		$scope.showAoiLegend = false;

		// Initialize the canvas elements
		initCanvas('scanpathCanvas', 'canvasWrapper');
		initCanvasModal('scanpathCanvasModal', 'canvasWrapperModal');

		// Get the basic scanpath data
		$scope.getTaskScanpaths();

		// Scanpath table rows expanding/collapsing controls
		$scope.expanded = {};
	};
	// Perform view initialization
	initController();
});
