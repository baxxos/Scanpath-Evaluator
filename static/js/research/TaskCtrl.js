// Handles all scanpath data related actions such as AJAX calls etc.
angular.module('gazerApp').controller('TaskCtrl', function($scope, $state, $http) {
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
		// Convert user input to uppercase and remove all whitespaces by regex
		customScanpathStr = customScanpathStr.toUpperCase();
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
				// Get the common scanpath
				$scope.task.customScanpath = response.data;
				// Get the similarity object
				var similarities = $scope.task.customScanpath.similarity;
				// Get the average similarity of each user scanpath to the common scanpath
				$scope.task.customScanpath.avgSimToCommon = calcAvgSimToCustom(similarities);

				// Assign each user scanpath its similarity to the common scanpath
				for (var index in $scope.task.scanpaths) {
					var act_scanpath = $scope.task.scanpaths[index];
					act_scanpath.simToCommon = similarities[act_scanpath.identifier];
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
		// Fetch canvas element in an un-angular way://
		$scope.canvas = document.getElementById('commonScanpathCanvas');
    	$scope.ctx = $scope.canvas.getContext('2d');

		// Basic canvas setup
		$scope.canvasInfo = {
			whitespaceToKeep: 0,
			scale: 1,
			offset: 2
		};

		$scope.ctx.globalAlpha = 1.0;
		$scope.ctx.beginPath();
	};

	var redrawCanvas = function() {
		// Fetch and setup the canvas element in an non-angular way://
		$scope.canvas = document.getElementById('commonScanpathCanvas');
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

			// Determine the scaling based on canvas max width, whitespace and offset <-> image raw resolution
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
			var colors = randomColor({
				luminosity: 'bright',
				count: $scope.task.aois.length
			});

			drawAois($scope.task.aois, $scope.canvasInfo.scale, $scope.canvasInfo.offset, colors);
		};
		canvasImage.src = $scope.task.visuals.main;
	};

	var clearFixations = function() {
		// Erase common scanpath fixation drawing by re-creating the canvas without it
		$scope.ctx.clearRect(0, 0, $scope.canvas.width, $scope.canvas.height);
		drawAois($scope.task.aois, $scope.canvasInfo.scale, $scope.canvasInfo.offset, colors);
    };

    var calcBoundingBox = function(data) {
		// Calculate bounding box for all aois
		var topLeftPoint = {
			x: data[0][1],
			y: data[0][3]
		};

		var bottomRightPoint = {
			x: topLeftPoint.x + data[0][2],
			y: topLeftPoint.y + data[0][4]
		};

		// Search the AOIs for the most upper-left and right-down points
		for(var i = 0; i < data.length; i++) {
			var actAoi = data[i];

			topLeftPoint.x = (actAoi[1] < topLeftPoint.x ? actAoi[1] : topLeftPoint.x);
			topLeftPoint.y = (actAoi[3] < topLeftPoint.y ? actAoi[3] : topLeftPoint.y);

			bottomRightPoint.x =
				(actAoi[1] + actAoi[2] > bottomRightPoint.x ? actAoi[1] + actAoi[2] : bottomRightPoint.x);
			bottomRightPoint.y =
				(actAoi[3] + actAoi[4] > bottomRightPoint.y ? actAoi[3] + actAoi[4] : bottomRightPoint.y);
		}

		return {
			topLeftPoint: topLeftPoint,
			bottomRightPoint: bottomRightPoint
		}
	};

    var drawAois = function(data, scale, offset, colors) {
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
				color: colors[index]
			};

			// Draw the AOI box
			drawRect(aoiBox, false);
			// Draw the AOI label
			drawLabel(aoiBox, aoi[5]);
		});
	};

	var drawLabel = function(aoiBox, aoiName) {
		// Initialize label style
		var fontSize = 14;
		$scope.ctx.font = 'bold ' + fontSize + 'px Helvetica, Arial';
		$scope.ctx.textAlign = 'center';
		$scope.ctx.lineWidth = $scope.canvasInfo.offset;

		// Draw the label background rectangle in the center of the AOI box
		var labelBox = {
			x: aoiBox.x + (aoiBox.xLen / 2) - (fontSize / 2), // Center the label horizontally
			y: aoiBox.y + (aoiBox.yLen / 2) - (fontSize - $scope.ctx.lineWidth), // Center it vertically
			xLen: fontSize,
			yLen: fontSize,
			color: '#000'
		};
		drawRect(labelBox, true);

		// Draw text in the exact center of the AOI box
		$scope.ctx.fillStyle = '#fff';
		$scope.ctx.fillText(aoiName, aoiBox.x + (aoiBox.xLen / 2) , aoiBox.y + (aoiBox.yLen / 2));
	};

    var drawFixations = function(data) {
		for(var i = 1; i < data.length; i++) {
			drawLine(data[i], data[i-1]);
        }

		data.forEach(function(circle) {
			drawCircle(circle);
		});
    };

    var drawCircle = function(data) {
        $scope.ctx.beginPath();
        $scope.ctx.arc(data.x, data.y, data.r, 0, 2*Math.PI, false);
        $scope.ctx.fillStyle = "#44f";
        $scope.ctx.fill();
        $scope.ctx.lineWidth = $scope.canvasInfo.offset;
        $scope.ctx.strokeStyle = "#000";
        $scope.ctx.stroke();
    };

    var drawRect = function(data, isFilled) {
		$scope.ctx.beginPath();
		$scope.ctx.rect(data.x, data.y, data.xLen, data.yLen);
		$scope.ctx.lineWidth = $scope.canvasInfo.offset;
        $scope.ctx.strokeStyle = data.color;
		$scope.ctx.stroke();

		// Optional: fill the rect area
		if(isFilled) {
			$scope.ctx.fillStyle = data.color;
        	$scope.ctx.fill();
		}
	};

    var drawLine = function(data1, data2) {
        $scope.ctx.beginPath();
        $scope.ctx.moveTo(data1.x, data1.y);
        $scope.ctx.lineTo(data2.x, data2.y);
		$scope.ctx.lineWidth = $scope.canvasInfo.offset;
        $scope.ctx.strokeStyle = "black";
        $scope.ctx.stroke();
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
