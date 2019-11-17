// set canvas id to variable
var canvas = document.getElementById("draw");

// get canvas 2D ctx and set it to the correct size
var ctx = canvas.getContext("2d");

// add event listeners to specify when functions should be triggered
canvas.addEventListener("mousemove", draw);
canvas.addEventListener("mousedown", setPosition);
canvas.addEventListener("mouseenter", setPosition);

// last known position
var pos = { x: 0, y: 0 };

// new position from mouse events
function setPosition(e) {
	var rect = canvas.getBoundingClientRect();
	pos.x = e.clientX-rect.left;
	pos.y = e.clientY-rect.top;
};

function draw(e) {
	if (e.buttons !== 1) return; // if mouse is pressed.....
	ctx.beginPath(); // begin the drawing path
	ctx.lineWidth = 15; // width of line
	ctx.lineCap = "round"; // rounded end cap
	ctx.moveTo(pos.x, pos.y); // from position
	setPosition(e);
	ctx.lineTo(pos.x, pos.y); // to position
	ctx.stroke(); // draw it!
	ctx.closePath();
};

function redraw(){
	ctx.clearRect(0, 0, ctx.canvas.width, ctx.canvas.height); // Clears the canvas
};

function submit(){
	var arr = resize_to_array(canvas);
	var xhr = new XMLHttpRequest();
	xhr.open('POST', 'http://127.0.0.1:5000/submit', true);
	xhr.setRequestHeader('Content-type', 'application/x-www-form-urlencoded');
	xhr.onload = function () {
    	var resp = JSON.parse(this.responseText);
    	console.log(resp);
    	// alert(this.responseText);
	};
	xhr.send("input="+arr);
};

function resize_to_array(canvas) {
	var rz = document.createElement('canvas');
	var cx = rz.getContext('2d');
	rz.width = 28
	rz.height = 28
	cx.drawImage(canvas, 0, 0, 28, 28);
	var arr = [];
	var imgData=cx.getImageData(0,0,rz.width,rz.height);
	for (var i = 3; i < imgData.data.length; i+=4) {
		arr.push(imgData.data[i]);
	}
	return arr;
}