
// Copyright 2021 Johnathan Pennington | All rights reserved.


const FRAME_RATE = 1 / 24;  // seconds
const BLINK_RATE = 2;  // in frames  // Applies when action is 'blink'.
const SPEED_FACTOR = 0.8;

// Creates random triangles using points within these xy coordinates.
const BOUND_SPAN = 80;  // pixels
const UPPER_LEFT_BOUND = [BOUND_SPAN / -2, BOUND_SPAN / -2];
const LOWER_RIGHT_BOUND = [BOUND_SPAN / 2, BOUND_SPAN / 2];

const canvas1 = document.getElementById('canvas1');
const ctx1 = canvas1.getContext('2d');

// Admin alerts
var userStartMsec = null;
var nextAlertMsec = 0;

var resizeLagTimeoutId;
var first_frame = 0;
var prev_frame = 0;
var reset_timestamp = Infinity;
var button_pressed = true;
var action = "rotate";  // rotate, stretch, blink
var lastBlinkVertices = null;
var lastBlinkColor = null;
var global_move_distance;
var triangles;
var num_triangles;
var color;
// hex-string ("#FFFFFF" is white) or color-name-string,
// or "rand-same" (all shapes the same consistent random color),
// or "rand-diff" (each shape a different consistent random color),
// or "rand-blink" (each blink changes each shape's color)


// Event listeners
window.addEventListener('click', button_func);
window.addEventListener('keydown', button_func);
window.addEventListener('resize', () => {
    clearTimeout(resizeLagTimeoutId);
    resizeWindow();
    resizeLagTimeoutId = setTimeout(function() { resizeWindow(); }, 400);
        // Resizes window again after delay to account for lag (debugged for iPhone 7).
});


resizeWindow();

window.requestAnimationFrame(animationFrame);


function resizeWindow() {
    canvas1.width = window.innerWidth;
    canvas1.height = window.innerHeight;
    ctx1.translate(window.innerWidth / 2, window.innerHeight / 2);
};


function button_func() {
    button_pressed = true;
    adminAlert();
};


function animationFrame(timestampMsec) {
    let timestamp = timestampMsec / 1000;
    if (button_pressed || reset_timestamp < timestamp) {
        change_animation_params(timestamp);
    };
    ctx1.fillStyle = 'black';
    ctx1.fillRect(canvas1.width / -2, canvas1.height / -2, canvas1.width, canvas1.height);  // Clear black background.
    if (action !== "blink" || timestamp - prev_frame >= BLINK_RATE * FRAME_RATE || lastBlinkVertices === null) {
        for (n of triangles) {
            let vertices = renderTriangleObject(n, (first_frame - timestamp) * SPEED_FACTOR / FRAME_RATE);
            let frame_n_color = n.color;
            if (n.color === "rand-blink") {
                frame_n_color = rand_hex_pure_hue();
            };
            if (action === 'blink') {
                lastBlinkVertices = vertices;
                lastBlinkColor = frame_n_color;
                prev_frame = timestamp;
            };
            ctx1.fillStyle = frame_n_color;
            ctx1.beginPath();
            ctx1.moveTo(vertices[0][0], vertices[0][1]);
            ctx1.lineTo(vertices[1][0], vertices[1][1]);
            ctx1.lineTo(vertices[2][0], vertices[2][1]);
            ctx1.fill();
        };
    } else {
        ctx1.fillStyle = lastBlinkColor;
        ctx1.beginPath();
        ctx1.moveTo(lastBlinkVertices[0][0], lastBlinkVertices[0][1]);
        ctx1.lineTo(lastBlinkVertices[1][0], lastBlinkVertices[1][1]);
        ctx1.lineTo(lastBlinkVertices[2][0], lastBlinkVertices[2][1]);
        ctx1.fill();
    };
    window.requestAnimationFrame(animationFrame);
};


function change_animation_params(timestamp) {

    first_frame = timestamp;
    prev_frame = timestamp;
    button_pressed = false;

    if (action === 'blink') {
        lastBlinkVertices = null;
        reset_timestamp = timestamp + 8;
        action = 'stretch';
        global_move_distance = 'rand';
        num_triangles = 222;
        color = randChoice(['rand-same', 'rand-same', 'rand-diff']);
    } else {
        reset_timestamp = Infinity;
        action = 'blink';
        global_move_distance = 0;
        num_triangles = 1;
        color = randChoice(['rand-same', 'rand-same', 'rand-blink']);
    };

    if (color === "rand-same") {
        color = rand_hex_pure_hue();  // Assign all triangles the same consistent random color.

    };

    triangles = [];
    for (let n = 0; n < num_triangles; n++) {
        let n_color = color;
        if (color === "rand-diff") {
            n_color = rand_hex_pure_hue();  // Assign each triangle a different consistent random color.
        };
        let newTriangle = newTriangleObject(UPPER_LEFT_BOUND, LOWER_RIGHT_BOUND, action, undefined, global_move_distance, undefined, undefined, undefined, n_color);
        triangles.push(newTriangle);
    };
};


function newTriangleObject(upper_left_bound, lower_right_bound, action, move_direction="rand", move_distance="rand", revolution_amount="rand", stretch_axis="rand", num_sides=3, color="rand") {
    // All points (__bound) are encoded as a list containing the x and y coordinate, i.e. [x, y].
    // Action can be "rotate", "stretch", or "blink".
    // Optional variables (random by default): move_direction, move_distance, revolution_amount, stretch_axis.
    // 0 <= move_direction < 1, move_direction=0 is right, move_direction=0.25 is down.
    // Move_distance is in pixels.
    // If action="rotate", revolution_amount behavior each frame:
    // a full rotation is 1 (clockwise) or -1 (counter-clockwise).
    // If action="stretch", revolution_amount behavior each frame:
    // no stretching is 1, half-width is 0.5, zero-width is 0, mirrored is -1, mirrored and double-width is -2.
    // 0 <= stretch_axis < 0.5.
    // Y is stretch_axis=0, increasing stretch_axis rotates it counter-clockwise, X is stretch_axis=0.25.
    // Num_sides is 3 by default.

    self = {
        upper_left_bound: upper_left_bound,
        lower_right_bound: lower_right_bound,
        init_vertices: rand_ngon_vertices(num_sides, upper_left_bound, lower_right_bound),
        action: action,
    };

    if (move_direction === "rand") { self.move_direction = randUniform(0, 1);
    } else { self.move_direction = move_direction; };

    if (move_distance === "rand") { self.move_distance = randUniform(8, 24);
    } else { self.move_distance = move_distance; };

    if (revolution_amount === "rand") { self.revolution_amount = randUniform(0.08, 0.16) * randChoice([-1, 1]);
    } else { self.revolution_amount = revolution_amount; };

    if (stretch_axis === "rand") { self.stretch_axis = randUniform(0, 0.5);
    } else { self.stretch_axis = stretch_axis; };

    self.num_sides = num_sides;

    if (color == "rand") { self.color = rand_hex_pure_hue();
    } else { self.color = color; };

    return self;
};


function renderTriangleObject(self, frame) {

    let actioned_vertices = [];
    if (self.action === "rotate") {
        for (let ngon_vertex = 0; ngon_vertex < self.init_vertices.length; ngon_vertex++) {
            let actioned_vertex = rotate_point(self.init_vertices[ngon_vertex], centroid(self.init_vertices), self.revolution_amount * frame);
            actioned_vertices.push(actioned_vertex);
        };
    } else if (self.action === "stretch") {
        actioned_vertices = stretch_points(self.init_vertices, self.stretch_axis, Math.cos(self.revolution_amount * 2 * Math.PI * frame));
    } else {  // "blink"
        actioned_vertices = rand_ngon_vertices(self.num_sides, self.upper_left_bound, self.lower_right_bound);
    };
    
    let moved_actioned_vertices = [];
    for (let ngon_vertex = 0; ngon_vertex < actioned_vertices.length; ngon_vertex++) {
        let moved_point = move_point(actioned_vertices[ngon_vertex], self.move_direction, self.move_distance * frame);
        moved_actioned_vertices.push(moved_point);
    };

    return moved_actioned_vertices;
};


function centroid(list_of_points) {
    // All points are encoded as a list containing the x and y coordinate, i.e. [x, y]. Returns centroid point as list.
    let num_points = list_of_points.length;
    let x_sum = 0;
    let y_sum = 0;
    for (point of list_of_points) {
        x_sum += point[0];
        y_sum += point[1];
    };
    x_centroid = x_sum / num_points;
    y_centroid = y_sum / num_points;
    return [x_centroid, y_centroid];
};


function move_point(point, direction, distance) {
    // All points are encoded as a list containing the x and y coordinate, i.e. [x, y].
    // 0 <= direction < 1, right is direction=0, down is direction=0.25. Distance is in pixels. Returns moved point as list.
    let theta = direction * Math.PI * 2;
    let x_point = point[0];
    let y_point = point[1];
    let x_moved_point = distance * Math.cos(theta) + x_point;
    let y_moved_point = distance * Math.sin(theta) + y_point;
    return [Math.round(x_moved_point), Math.round(y_moved_point)];
};


function rotate_point(point, pivot, rotation_amount) {
    // All points (point, pivot) are encoded as a list containing the x and y coordinate, i.e. [x, y].
    // Full rotations are 1 (clockwise) or -1 (counter-clockwise). Returns rotated point as list.
    let x_point = point[0];
    let y_point = point[1];
    let x_pivot = pivot[0];
    let y_pivot = pivot[1];
    let radians = rotation_amount * Math.PI * 2;
    let x_rotated_point = (x_point - x_pivot) * Math.cos(radians) - (y_point - y_pivot) * Math.sin(radians) + x_pivot;
    let y_rotated_point = (x_point - x_pivot) * Math.sin(radians) + (y_point - y_pivot) * Math.cos(radians) + y_pivot;
    return [Math.round(x_rotated_point), Math.round(y_rotated_point)];
};


function stretch_points(list_of_points, axis, stretch_amount) {
    // All points are encoded as a list containing the x and y coordinate, i.e. [x, y].
    // 0 <= axis < 0.5. Y is axis=0, top-left quadrant to bottom-right quadrant is axis=0.125, X is axis=0.25.
    // Stretch_amount: no change is 1, half-width is 0.5, zero-width is 0, mirrored is -1, mirrored and double-width is -2.
    // Returns list of stretched points, with each point as list.

    let points_centroid = centroid(list_of_points);

    let moved_points = [];
    for (point of list_of_points) { moved_points.push([point[0] - points_centroid[0], point[1] - points_centroid[1]]); };
    
    let rotated_points = [];
    for (point of moved_points) { rotated_points.push(rotate_point(point, [0, 0], axis)); };

    let stretched_points = [];
    for (point of rotated_points) { stretched_points.push([point[0] * stretch_amount, point[1]]); };

    let unrotated_points = [];
    for (point of stretched_points) { unrotated_points.push(rotate_point(point, [0, 0], -axis)); };

    let unmoved_points = [];
    for (point of unrotated_points) { unmoved_points.push([point[0] + points_centroid[0], point[1] + points_centroid[1]]); };
    
    let int_unmoved_points = [];
    for (point of unmoved_points) { int_unmoved_points.push([Math.round(point[0]), Math.round(point[1])]); };

    return int_unmoved_points;
};


function rand_ngon_vertices(num_sides, upper_left_bound, lower_right_bound) {
    // All points (__bound) are encoded as a list containing the x and y coordinate, i.e. [x, y].
    // Returns list of vertices, with each vertex point as list.
    let vertices = [];
    for (let vertex = 0; vertex < num_sides; vertex++) {
        let x = randInt(upper_left_bound[0], lower_right_bound[0]);
        let y = randInt(upper_left_bound[1], lower_right_bound[1]);
        vertices.push([x, y]);
    };
    return vertices;
};


function rand_hex_pure_hue() {
    let randHue = randInt(0, 359);
    return `hsl(${randHue}, 100%, 50%)`;
};


function adminAlert () {

    const appName = 'Volatile3gons';
    const firstAlertSec = 15;  // Send first alert after X seconds.
    const alertSpacing = 3;  // exponential proportion for consecutive alert times.
    // thisAlertSec = firstAlertSec * alertSpacing ^ alertNum

    if (Date.now() < nextAlertMsec) { return; };  // Not time for alert yet.

    if (userStartMsec === null) {
        userStartMsec = Date.now();
        nextAlertMsec = userStartMsec + firstAlertSec * 1000;        
    } else {
        nextAlertMsec = userStartMsec + (nextAlertMsec - userStartMsec) * alertSpacing;
    };

    if (Date.now() > nextAlertMsec) {
        // User was idle past threshold. Reset timer.
        userStartMsec = Date.now();
        nextAlertMsec = userStartMsec + firstAlertSec * 1000;     
    };

    let request = new XMLHttpRequest();
    request.open("POST", '/serverterminal', true);
    request.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    let userSecs = Math.floor((Date.now() - userStartMsec) / 1000);
    let requestContent = `appname=${appName}&userstartmsec=${userStartMsec}&usersecs=${Math.floor(userSecs)}`;
    request.send(requestContent);
};


function randUniform(smaller, larger) {
    return Math.random() * (larger - smaller) + smaller;
};


function randInt(min, max, exponCurve=1) {
    // min <= randInt <= max // exponCurve is any positive real number. >1 curves toward min. <1 curves toward max.
    return Math.floor(Math.pow(Math.random(), exponCurve) * (max - min + 1) + min);
};


function randChoice(array) {
    let index = Math.floor(Math.random() * array.length);
    return array[index];
};
