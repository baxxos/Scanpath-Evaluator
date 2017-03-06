angular.module('gazerApp').service('CanvasDrawService', function() {
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

	this.calcBoundingBox = function(data) {
		// Calculates bounding box for a set of square/rectangle AOIs
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
});