from IPython.display import HTML, display, clear_output
from collections import defaultdict
import time
import __main__

_CANVAS = '''
<div>
    <canvas class="main-robo-world" width="{0}" height="{1}" style="background:rgba(158, 167, 184, 0.2);" data-world_name="{2}"  onclick="getPosition(this,event)"/>
</div>

<script type="text/javascript">
var all_polygons = {3}
</script>
'''
_JS_MAIN = '''
<script>
var latest_output_area ="NONE"; // Jquery object for the DOM element of output area which was used most recently

function handle_output(out, block){
    var output = out.content.data["text/html"];
    latest_output_area.html(output);
}

function polygon_complete(canvas, vertices){
    latest_output_area = $(canvas).parents('.output_subarea');
    var world_object_name = canvas.dataset.world_name;
    var command = world_object_name + ".add_obstacle(" + JSON.stringify(vertices) + ")";
    console.log("Executing Command: " + command);
    var kernel = IPython.notebook.kernel;
    var callbacks = { 'iopub' : {'output' : handle_output}};
    kernel.execute(command,callbacks);
}

var canvas , ctx;

function drawPolygon(array) {
    ctx.fillStyle = '#f00';
    ctx.beginPath();
    ctx.moveTo(array[0][0],array[0][1]);
    for(var i = 1;i<array.length;++i)
    {
        ctx.lineTo(array[i][0], array[i][1]);
    }
    ctx.closePath();
    ctx.fill();
}

var pArray = new Array();

function getPosition(obj,event) {
    canvas = obj;
    ctx = canvas.getContext('2d');
    var x = new Number();
    var y = new Number();

    x = event.pageX;
    y = event.pageY;

    x -= $(canvas).offset().left;
    y -= $(canvas).offset().top;

    drawPoint(x,y);
    //draw dot
    if(pArray.length>1)
    {
        drawPoint(pArray[0][0],pArray[0][1]);
    }
    //check overlap
    if(ctx.isPointInPath(x, y) && (pArray.length>1)) {
        //Do something
        drawPolygon(pArray);
        polygon_complete(canvas,pArray);
    }
    else {
        var point = new Array();
        point.push(x,y);
        pArray.push(point);
    }
}

function drawPoint(x, y) {
    ctx.beginPath();
    ctx.arc(x, y, 5, 0, Math.PI*2);
    ctx.fillStyle = '#00f';
    ctx.fill();
    ctx.closePath();
}

function initalizeObstacles(objects) {
    canvas = $('canvas.main-robo-world').get(0);
    ctx = canvas.getContext('2d');
    $('canvas.main-robo-world').removeClass('main-robo-world');
    for(var i=0;i<objects.length;++i) {
        drawPolygon(objects[i]);
    }
    pArray.length = 0;
}

initalizeObstacles(all_polygons);

</script>
'''


class ContinuousWorld:
    ''' Heavily borrows ideas from AIMA code's Environment class'''

    def __init__(self, width=400, height=400, fill="#AAA"):
        self.time = time.time()
        self.width = width
        self.height = height
        self.map = {}  # nested list containing vertices of polgon.
        self.map["obstacles"] = []
        self.map["agents"] = []

    def object_name(self):
        globals_in_main = {x: getattr(__main__, x) for x in dir(__main__)}
        # g = locals()
        for x in globals_in_main:
            if isinstance(globals_in_main[x], type(self)):
                if globals_in_main[x].time == self.time:
                    return x

    def move_to(self, thing, destination):
        "Move a thing to a new location."
        # Do in future
        return NotImplementedError

    def add_obstacle(self, vertices):
        """ Vertices must be a nested
        tuple.
        """
        self.map["obstacles"].append(vertices)
        self.show()

    def show(self):
        # add js
        # customize replace name of class
        clear_output()
        total_html = _CANVAS.format(self.width, self.height, self.object_name(), str(self.map["obstacles"])) + _JS_MAIN
        display(HTML(total_html))

