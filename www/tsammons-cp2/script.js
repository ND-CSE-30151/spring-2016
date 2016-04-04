var canvas = document.getElementById('canvas');
var ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;
ctx.strokeStyle= "#00FF00";
 
var deg_to_rad = Math.PI/180.0;
var old = 50;
var old2 = 50;
var depth = parseInt(document.getElementById("depth").value);
var param = 0;
 
function drawLine(x1, y1, x2, y2){
    ctx.moveTo(x1, y1);
    ctx.lineTo(x2, y2);
}


function myFunction(e) {    
    if (document.getElementById("tree").checked) {
	// get mouse position
	depth = parseInt(document.getElementById("depth").value);
	var x = e.clientX;
	var y = e.clientY;
	var x_start = canvas.width/1.8;
	var y_start = canvas.height-100;
	var param = Math.atan2(x-(x_start), (y_start)-y);
	var d = Math.sqrt( (x-x_start)*(x-x_start) + (y_start-y)*(y_start-y) );
	d = d/600 + 1;

	// draw
	if ((Math.abs(old-param) > .1 || Math.abs(old2 - d) > 0.1) && document.getElementById("tree").checked) {
	    ctx.clearRect(0, 0, canvas.width, canvas.height);
	    ctx.beginPath();
	    drawTree(canvas.width/2.5, canvas.height-100, -90, depth, param, 6*d);
	    ctx.closePath();
	    ctx.stroke();
	    old = param;
	    old2 = d;
	}
    }
}
 
function begin() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    ctx.beginPath();
    drawTree(canvas.width/2.5, canvas.height-100, -90, document.getElementById("depth").value, 0, 6);
    ctx.closePath();
    ctx.stroke();
}

function drawTree(x1, y1, angle, depth, p, l){
    if (depth !== 0){
	var ang = parseInt(document.getElementById("angle").value);
	var x2 = x1 + (Math.cos(angle * deg_to_rad) * depth * l);
	var y2 = y1 + (Math.sin(angle * deg_to_rad) * depth * l);
	drawLine(x1, y1, x2, y2);
	drawTree(x2, y2, angle - ang + 50*p, depth - 1, p, l);
	drawTree(x2, y2, angle + ang + 50*p, depth - 1, p, l);
    }
}

function sierpinski(Ax,Ay,Bx,By,Cx,Cy,d) {
    if(d>0) {
        var pointAx = (Bx + Cx) / 2;
        var pointAy = (By + Cy) / 2;
     
        var pointBx = (Ax + Cx) / 2;
        var pointBy = (Ay + Cy) / 2;
     
        var pointCx = (Ax + Bx) / 2;
        var pointCy = (Ay + By) / 2;
     
        var d2 = d-1;
        sierpinski(Ax,Ay,pointBx,pointBy,pointCx,pointCy,d2);
        sierpinski(pointCx,pointCy,pointAx,pointAy,Bx,By,d2);
        sierpinski(pointBx,pointBy,pointAx,pointAy,Cx,Cy,d2);
    }
    else {
        ctx.moveTo(Ax,Ay);
        ctx.lineTo(Bx,By);
        ctx.lineTo(Cx,Cy);
        ctx.lineTo(Ax,Ay);
    }
}
     
     
function drawSierpinski() {
    var midPointX = canvas.width/2.5;
    var midPointY = canvas.height/2+100;
     
    //var deep = 6;
    var deep  = document.getElementById("deep").value;
    var size = document.getElementById("size").value;
 
    var ri = (size/6) * Math.sqrt(3);
    var ru = (size/3) * Math.sqrt(3);
     
    var pointAx = midPointX-(size/2);
    var pointAy = midPointY+ri;
     
    var pointBx = midPointX+(size/2);
    var pointBy = midPointY+ri;
     
    var pointCx = midPointX;
    var pointCy = midPointY-ru;
 
    sierpinski(pointAx,pointAy,pointBx,pointBy,pointCx,pointCy,deep);
}   


function triangle(){
    if (document.getElementById("tri").checked) { 
	ctx.clearRect(0, 0, canvas.width, canvas.height);
	ctx.beginPath();
       	drawSierpinski();
	ctx.closePath();
	ctx.stroke();
    }
}

