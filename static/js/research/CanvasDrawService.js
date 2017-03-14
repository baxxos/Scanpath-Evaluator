angular.module('gazerApp').service('CanvasDrawService', function() {
	var self = this;

	/*** BASIC DRAWINGS ***/
	// Handles drawing of basic geometric shapes onto the canvas
	this.drawCircle = function(ctx, coords, strokeColor, lineWidth, fillColor) {
        ctx.beginPath();
        ctx.arc(coords.x, coords.y, coords.r, 0, 2*Math.PI, false);

		// Optional: fill the circle area
		if(fillColor) {
			ctx.fillStyle = fillColor;
        	ctx.fill();
		}

        ctx.lineWidth = lineWidth;
        ctx.strokeStyle = strokeColor;
        ctx.stroke();
    };

	this.drawLine = function(ctx, begin, end, color, lineWidth) {
        ctx.beginPath();
        ctx.moveTo(begin.x, begin.y);
        ctx.lineTo(end.x, end.y);
		ctx.lineWidth = lineWidth;
        ctx.strokeStyle = color;
        ctx.stroke();
    };

    this.drawRect = function(ctx, coords, strokeColor, lineWidth, fillColor) {
		ctx.beginPath();
		ctx.rect(coords.x, coords.y, coords.xLen, coords.yLen);
		ctx.lineWidth = lineWidth;
        ctx.strokeStyle = strokeColor;
		ctx.stroke();

		// Optional: fill the rect area
		if(fillColor) {
			ctx.fillStyle = fillColor;
        	ctx.fill();
		}
	};

	/*** SCANPATH SPECIFIC DRAWINGS ***/
	// Advanced scanpath geometry methods
	this.drawLabel = function(ctx, canvasInfo, aoiBox) {
		// Initialize label style
		var fontSize = canvasInfo.fontSize;
		ctx.font = 'bold ' + fontSize + 'px Helvetica, Arial';
		ctx.textAlign = 'center';
		ctx.lineWidth = canvasInfo.lineWidth;

		// Draw the label background rectangle in the center of the AOI box
		var labelBox = {
			x: aoiBox.x + (aoiBox.xLen / 2) - (fontSize / 2), // Center the label horizontally
			y: aoiBox.y + (aoiBox.yLen / 2) - (fontSize - ctx.lineWidth), // Center it vertically
			xLen: fontSize,
			yLen: fontSize
		};
		self.drawRect(ctx, labelBox, '#000', canvasInfo.lineWidth, '#000');

		// Draw text in the exact center of the AOI box
		ctx.fillStyle = '#fff';
		ctx.fillText(aoiBox.name, aoiBox.x + (aoiBox.xLen / 2) , aoiBox.y + (aoiBox.yLen / 2));
	};

	this.drawSaccade = function(ctx, canvasInfo, aois, prevFixation, actFixation) {
		// Draw a line connecting each pair of fixations in the given scanpath
		// Passed fixations are formatted as: [["E", 500], ["C", 350] ... ]

		// Skip undefined AOIs (e.g. wrong user input)
		if(!aois[prevFixation[0]] || !aois[actFixation[0]]) {
			console.error('No such area of interest : ' + prevFixation[0] + ' or ' + actFixation[0]);
			return false;
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

		self.drawLine(ctx, lineFrom, lineTo, '#000', canvasInfo.lineWidth / 2);
	};

	this.drawAois = function(canvas, ctx, canvasInfo, backgroundImg, aoiData) {
		// Reset previously drawn AOIs
		var aoiCanvasData = {};
		// Clear canvas and draw background image
		ctx.clearRect(0, 0, canvas.width, canvas.height);
		ctx.drawImage(backgroundImg, 0, 0, canvas.width, canvas.height);

		// Data from backed is formatted as: ['aoiName', xFrom, xLen, yFrom, yLen, 'aoiShortName']
		aoiData.forEach(function(actAoi, index) {
			var aoiBox = {
				x: (actAoi[1] * canvasInfo.scale) + canvasInfo.offset,
				y: (actAoi[3] * canvasInfo.scale) + canvasInfo.offset,
				xLen: actAoi[2] * canvasInfo.scale,
				yLen: actAoi[4] * canvasInfo.scale,
				name: actAoi[5],
				fullName: actAoi[0]
			};

			// Draw the AOI box
			self.drawRect(ctx, aoiBox, canvasInfo.colors[index], canvasInfo.lineWidth);
			// Draw the AOI label
			self.drawLabel(ctx, canvasInfo, aoiBox);
			// Remember the current AOI data for later access
			aoiCanvasData[aoiBox.name] = aoiBox;
		});
		// Return data (e.g. to be assigned to the scope)
		return aoiCanvasData;
	};
});