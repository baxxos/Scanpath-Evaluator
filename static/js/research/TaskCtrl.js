// Handles all scanpath data related actions such as AJAX calls etc.
angular.module('gazerApp').controller('TaskCtrl', function($scope, $state, $http, CanvasDrawService) {
	$scope.getTaskScanpaths = function() {
		$http({
			url: 'get_task_data',
			method: 'GET',
			params: {
				taskId: $scope.task.id
			}
		}).then(
			function(response) {
				$scope.task.scanpaths = response.data.scanpaths;
				$scope.task.visuals = response.data.visuals;
				$scope.task.aois = response.data.aois;

				redrawCanvas();
			},
			function(data) {
				console.error('Failed to get task data content.', data);
			}
		);
    };

    // Calculate average similarity in a common scanpath similarity object provided by back-end as response
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

				// Draw the common scanpath on the canvas
				drawFixations($scope.task.commonScanpath.fixations, $scope.canvasInfo.aois);
			},
			function(data) {
				console.error('Failed to get common scanpath response from the server.', data);
			}
		);
    };

    // Calculate average similarity to a custom scanpath data object provided by back-end as a response
    var calcAvgSimToCustom = function(customScanpathSimilarity) {
		var similarity = 0, total = 0;

		// Loop through all similarity values stored in the similarity object
		for (var scanpath in customScanpathSimilarity) {
			similarity += customScanpathSimilarity[scanpath];
			// Keep track of the total number of scanpaths as there is no keys.length in dict
			total++;
		}
		return similarity / total;
	};

	var getCustomScanpathDetails = function(customScanpathStr) {
		// Remove all whitespaces from the user input by regex
		customScanpathStr = customScanpathStr.replace(/\s/g, "");
		// Regex to normalize the scanpath (remove repeated AOIs: AABC -> ABC)
		// The Regex /(.)\1+/ matches any single char followed by the same char at least once (+)
		customScanpathStr = customScanpathStr.replace(/(.)\1+/g, '$1');

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
					$scope.task.customScanpath.avgSimToCommon = calcAvgSimToCustom(similarities);

					// Assign each user scanpath its similarity to the common scanpath
					for (var index in $scope.task.scanpaths) {
						var act_scanpath = $scope.task.scanpaths[index];
						act_scanpath.simToCommon = similarities[act_scanpath.identifier];
					}

					// Draw the custom scanpath onto the canvas
					drawFixations($scope.task.customScanpath.fixations, $scope.canvasInfo.aois);
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

	// Removes excluded flag from all available scanpaths
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

	// Inverse function to the one above (since classic toggle is not user friendly)
	$scope.disableAllScanpaths = function() {
		$scope.task.excludedScanpaths = [];
		$scope.task.scanpaths.forEach(function(scanpath) {
			scanpath.excluded = true;
			$scope.task.excludedScanpaths.push(scanpath.id);
		});
	};

	var initCanvas = function() {
		// Fetch canvas element in a non-angular way://
		$scope.canvas = document.getElementById('commonScanpathCanvas');
    	$scope.ctx = $scope.canvas.getContext('2d');

		// Basic canvas setup
		$scope.canvasInfo = {
			fontSize: 14,
			whitespaceToKeep: 0,
			scale: 1,
			offset: 2,
			aois: {} // Serves for accessing the aois after drawing (e.g. for common scanpath displaying)
		};

		$scope.ctx.globalAlpha = 1.0;
		$scope.ctx.beginPath();
	};

	var redrawCanvas = function() {
		// Reset background image
		$scope.canvas.style.backgroundImage = 'url(' + $scope.task.visuals.main + ')';

		// Load the canvas background image again to get its natural resolution
		var canvasImage = new Image();
		// Callback that gets triggered once the img has completed loading - it adjusts the canvas to the img
		canvasImage.onload = function() {
			// Determine how much whitespace do we need to keep around the canvas after scaling
			var canvasWrapper = document.getElementById('canvasWrapper');
			var canvasWrapperStyle = window.getComputedStyle(canvasWrapper);

			$scope.canvasInfo.whitespaceToKeep =
				parseInt(canvasWrapperStyle.marginRight) +
				parseInt(canvasWrapperStyle.marginLeft) +
				parseInt(canvasWrapperStyle.paddingLeft) +
				parseInt(canvasWrapperStyle.paddingRight);

			// Determine the scaling based on canvas max width, whitespace and offset compared to image raw resolution
			$scope.canvasInfo.scale =
				(canvasWrapper.offsetWidth - $scope.canvasInfo.whitespaceToKeep - $scope.canvasInfo.offset * 2) /
				canvasImage.naturalWidth;

			// Set scaled sizes of width/height and the apply the default offset
			$scope.canvas.style.width =
				canvasImage.naturalWidth * $scope.canvasInfo.scale + ($scope.canvasInfo.offset * 2) + 'px';
			$scope.canvas.style.height =
				canvasImage.naturalHeight * $scope.canvasInfo.scale + ($scope.canvasInfo.offset * 2) + 'px';
			// Make canvas resolution match its real size
			$scope.canvas.width = $scope.canvas.offsetWidth;
			$scope.canvas.height = $scope.canvas.offsetHeight;

			// Set of colors to be used for drawing AOIs
			$scope.canvasInfo.colors = randomColor({
				luminosity: 'bright',
				count: $scope.task.aois.length
			});

			drawAois($scope.task.aois, $scope.canvasInfo.scale, $scope.canvasInfo.offset, $scope.canvasInfo.colors);
		};
		canvasImage.src = $scope.task.visuals.main;
	};

	var clearFixations = function() {
		// Erase common scanpath fixation drawing by re-creating the canvas without it
		$scope.ctx.clearRect(0, 0, $scope.canvas.width, $scope.canvas.height);
		drawAois($scope.task.aois, $scope.canvasInfo.scale, $scope.canvasInfo.offset, $scope.canvasInfo.colors);
    };

    var drawAois = function(data, scale, offset, colors) {
		// Reset previously drawn AOIs
		$scope.canvasInfo.aois = {};

		// Data from backed is formatted as: ['aoiName', 'xFrom', 'xLen', 'yFrom', 'yLen', 'aoiShortName']
		// Convert from strings to numbers TODO do this at the backend
		for(var j = 0; j < data.length; j++) {
			for(var k = 1; k <= 4; k++) {
				data[j][k] = Number(data[j][k]);
			}
		}

		data.forEach(function(aoi, index) {
			var aoiBox = {
				x: (aoi[1] * scale) + offset,
				y: (aoi[3] * scale) + offset,
				xLen: aoi[2] * scale,
				yLen: aoi[4] * scale,
				name: aoi[5],
				fullName: aoi[0]
			};

			// Draw the AOI box
			CanvasDrawService.drawRect($scope.ctx, aoiBox, colors[index], $scope.canvasInfo.offset);
			// Draw the AOI label
			drawLabel(aoiBox);
			// Remember the current AOI data for later access
			$scope.canvasInfo.aois[aoiBox.name] = aoiBox;
		});
	};

	var drawFixations = function(commonScanpath, aois) {
		// Clear the canvas from previous fixation drawings first
		clearFixations();

		for(var i = 1; i < commonScanpath.length; i++) {
			// scanpathData fixations are formatted as: [["E", 500], ["C", 350] ... ]
			var actFixation = commonScanpath[i];
			var prevFixation = commonScanpath[i - 1];

			// Skip undefined AOIs (e.g. wrong user input)
			if(!aois[prevFixation[0]] || !aois[actFixation[0]]) {
				console.error('No such area of interest : ' + prevFixation[0] + ' or ' + actFixation[0]);
				clearFixations();
				return;
			}

			// Line from the center of the previous fixation
			var lineFrom = {
				x: aois[prevFixation[0]].x + (aois[prevFixation[0]].xLen / 2),
				y: aois[prevFixation[0]].y + (aois[prevFixation[0]].yLen / 2)
			};
			// Line to the center of the current fixation
			var lineTo = {
				x: aois[actFixation[0]].x + (aois[actFixation[0]].xLen / 2),
				y: aois[actFixation[0]].y + (aois[actFixation[0]].yLen / 2)
			};

			CanvasDrawService.drawLine($scope.ctx, lineFrom, lineTo, '#000', $scope.canvasInfo.offset);
        }

		commonScanpath.forEach(function(fixation, index) {
			// Draw a circle in the middle of a corresponding AOI box
			var fixationCircle = {
				x: aois[fixation[0]].x + (aois[fixation[0]].xLen / 2),
				y: aois[fixation[0]].y + (aois[fixation[0]].yLen / 2),
				r: (fixation[1] ? fixation[1] : 400) / 40 // TODO limit the radius of circle to the enclosing AOI
			};

			CanvasDrawService.drawCircle($scope.ctx, fixationCircle, '#000', $scope.canvasInfo.offset, '#44f');

			// Draw a label (centering is based on the fontSize and stroke line width)
			$scope.ctx.fillStyle = '#fff';
			$scope.ctx.lineWidth = $scope.canvasInfo.offset;
			$scope.ctx.fillText(
				(index + 1).toString(),
				fixationCircle.x,
				fixationCircle.y + ($scope.canvasInfo.fontSize / 2) - $scope.ctx.lineWidth
			);
		});
    };

	var drawLabel = function(aoiBox) {
		// Initialize label style
		var fontSize = $scope.canvasInfo.fontSize;
		$scope.ctx.font = 'bold ' + fontSize + 'px Helvetica, Arial';
		$scope.ctx.textAlign = 'center';
		$scope.ctx.lineWidth = $scope.canvasInfo.offset;

		// Draw the label background rectangle in the center of the AOI box
		var labelBox = {
			x: aoiBox.x + (aoiBox.xLen / 2) - (fontSize / 2), // Center the label horizontally
			y: aoiBox.y + (aoiBox.yLen / 2) - (fontSize - $scope.ctx.lineWidth), // Center it vertically
			xLen: fontSize,
			yLen: fontSize
		};
		CanvasDrawService.drawRect($scope.ctx, labelBox, '#000', $scope.canvasInfo.offset, '#000');

		// Draw text in the exact center of the AOI box
		$scope.ctx.fillStyle = '#fff';
		$scope.ctx.fillText(aoiBox.name, aoiBox.x + (aoiBox.xLen / 2) , aoiBox.y + (aoiBox.yLen / 2));
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
			sortBy: 'identifier'
		};
		// Initialize the canvas element
		initCanvas();
		// Get the basic scanpath data
		$scope.getTaskScanpaths();
	};
	// Perform view initialization
	initController();
});
