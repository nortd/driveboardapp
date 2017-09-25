var jobview_scene = undefined
var jobview_camera = undefined
var jobview_controls = undefined

var jobview_path_geometry = undefined
var jobview_path_material = undefined

var jobview_tool = undefined


var jobview_width = 0
var jobview_height = 0
var jobview_mm2px = 1.0

var jobview_gridLayer = undefined
var jobview_boundsLayer = undefined
var jobview_seekLayer = undefined
var jobview_feedLayer = undefined
var jobview_headLayer = undefined
var jobview_offsetLayer = undefined
var jobview_moveLayer = undefined
var jobview_jogLayer = undefined

var nav_height_init = 0
var footer_height = 0
var info_width_init = 0

var jobview_width_last = 0
var jobview_height_last = 0

var jobview_item_selected = undefined



function jobview_clear(){
  // TODO: delete scene content
  jobview_render()
}


function jobview_reset_layer(layer) {
  if (layer) {
    layer.remove()
  }
  layer = new paper.Layer()
  layer.pivot = new paper.Point(0,0)
  var x = 0
  var y = 0
  if ('offset' in status_cache) {
    var x_mm = status_cache.offset[0]
    var y_mm = status_cache.offset[1]
    x = Math.floor(x_mm*jobview_mm2px)
    y = Math.floor(y_mm*jobview_mm2px)
  }
  console.log("status_cahce.offset: "+x_mm+","+y_mm)
  layer.position = new paper.Point(x,y)
  return layer
}


function jobview_resize() {
  var max_canvas_width = $(window).innerWidth()-info_width_init-2
  var max_canvas_height = $(window).innerHeight()-nav_height_init-footer_height_init

  // calculate jobview_mm2px
  // used to scale mm geometry to be displayed on canvas
  if (app_config_main !== undefined) {
    var wk_width = app_config_main.workspace[0]
    var wk_height = app_config_main.workspace[1]
    // get aspects, portrait: < 1, landscape: > 1
    var aspect_workspace = wk_width/wk_height
    var aspect_canvas_void = max_canvas_width/max_canvas_height
    if (aspect_canvas_void > aspect_workspace) {  // workspace is narrower
      // canvas wider, fit by height
      jobview_mm2px = max_canvas_height/wk_height
      $("#job_canvas").width(Math.floor(wk_width*jobview_mm2px))
      $("#main_container").height(max_canvas_height)
      $("#info_panel").height(max_canvas_height)
    } else if (aspect_workspace > aspect_canvas_void) {  // workspace is wider
      // canvas taller, fit by width
      jobview_mm2px = max_canvas_width/wk_width
      $("#job_canvas").width(max_canvas_width)
      var h_scaled = Math.floor(wk_height*jobview_mm2px)
      if (h_scaled < 400) {  // keep sane height
        $("#main_container").height(h_scaled)
        $("#info_panel").height(max_canvas_height)
      } else {
        $("#main_container").height(h_scaled)
        $("#info_panel").height(h_scaled)
      }
    } else {
      // excact fit
      jobview_mm2px = max_canvas_width/wk_width
      $("#job_canvas").width(max_canvas_width)
      $("#main_container").height(max_canvas_height)
      $("#info_panel").height(max_canvas_height)
    }
  } else {
    console.log("config retrieve error")
  }
  jobview_width = $('#job_canvas').innerWidth()
  jobview_height = $('#job_canvas').innerHeight()

  // resize content
  clearTimeout(window.lastResizeTimer)
  window.lastResizeTimer = setTimeout(function() {
    var resize_scale = jobview_width/jobview_width_last
    jobview_width_last = jobview_width
    jobview_height_last = jobview_height
    for (var i=0; i<paper.project.layers.length; i++) {
      var layer = paper.project.layers[i]
      for (var j=0; j<layer.children.length; j++) {
        var child = layer.children[j]
        child.scale(resize_scale, new paper.Point(0,0))
      }
    }
    paper.view.draw()
  }, 300)
}


function jobview_deselect_all() {
  for (var i=0; i<paper.project.layers.length; i++) {
    var layer = paper.project.layers[i]
    for (var j=0; j<layer.children.length; j++) {
      var child = layer.children[j]
      child.selected = false
    }
  }
}


///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

$(window).resize(function() {
  // jobview_resize()
})


function jobview_ready() {
  // This function is called after appconfig received.

    var container = document.getElementById('job_canvas');

    nav_height_init = $('#main_navbar').outerHeight(true)
    footer_height_init = $('#main_footer').outerHeight(true)
    info_width_init = $("#info_panel").outerWidth(true)
    var width = window.innerWidth - info_width_init - 2
    var height = window.innerHeight - nav_height_init - footer_height_init

    jobview_scene = scene = new THREE.Scene();
    jobview_scene.background = new THREE.Color(0xf0f0f0);

    jobview_camera = new THREE.PerspectiveCamera(70, width / height, 1, 10000);
    jobview_camera.position.set(0, 250, 1000);
    // jobview_camera.up.set( 0, 0, 1);
    jobview_scene.add(jobview_camera);

    jobview_scene.add(new THREE.AmbientLight(0xf0f0f0));
    var light = new THREE.SpotLight(0xffffff, 1.5);
    light.position.set(0, 1500, 200);
    // light.castShadow = true;
    // light.shadow = new THREE.LightShadow(new THREE.PerspectiveCamera(70, 1, 200, 2000));
    // light.shadow.bias = -0.000222;
    // light.shadow.mapSize.width = 1024;
    // light.shadow.mapSize.height = 1024;
    jobview_scene.add(light);
    spotlight = light;

    var planeGeometry = new THREE.PlaneGeometry(2000, 2000);
    planeGeometry.rotateX(-Math.PI / 2);
    var planeMaterial = new THREE.ShadowMaterial({
      opacity: 0.2
    });

    var plane = new THREE.Mesh(planeGeometry, planeMaterial);
    plane.position.y = -200;
    plane.receiveShadow = true;
    jobview_scene.add(plane);

    var helper = new THREE.GridHelper(2000, 100);
    helper.position.y = -199;
    helper.material.opacity = 0.25;
    helper.material.transparent = true;
    jobview_scene.add(helper);

    var axis = new THREE.AxisHelper(100);
    // axis.position.set(-500, -500, -500);
    jobview_scene.add(axis);

    jobview_renderer = new THREE.WebGLRenderer({
      antialias: true
    });
    jobview_renderer.setPixelRatio(window.devicePixelRatio);
    // renderer.setSize(window.innerWidth-400, window.innerHeight-150);
    jobview_renderer.setSize(width, height);
    // renderer.shadowMap.enabled = true;
    container.appendChild(jobview_renderer.domElement);

    // Controls
    jobview_controls = new THREE.OrbitControls(jobview_camera, jobview_renderer.domElement);
    jobview_controls.damping = 0.2;
    jobview_controls.addEventListener('change', jobview_render);
    jobview_controls.addEventListener('start', function() {});
    jobview_controls.addEventListener('end', function() {});


    // tool cone
    var cone_geometry = new THREE.ConeGeometry( 6, 20, 32 );
    cone_geometry.translate(0,-10,0)
    var cone_material = new THREE.MeshBasicMaterial( {color: 0xff0000} );
    jobview_tool = new THREE.Mesh( cone_geometry, cone_material );
    jobview_tool.rotateX(-Math.PI/2)
    jobview_scene.add( jobview_tool );

    // jobview_testpath()

    jobview_render()
}


function jobview_render() {
  jobview_renderer.render(jobview_scene, jobview_camera)
}


function jobview_fit_camera_to_object(object, offset) {

  const boundingBox = new THREE.Box3();
  boundingBox.setFromObject( object );

  const center = boundingBox.getCenter();
  const size = boundingBox.getSize();

  // get the max side of the bounding box
  const maxDim = Math.max( size.x, size.y, size.z );
  const fov = jobview_camera.fov * ( Math.PI / 180 );
  let cameraZ = Math.abs( maxDim / 4 * Math.tan( fov * 2 ) );

  // offset the camera as desired - usually a value of ~ 1.25 is good to prevent
  // object filling the whole canvas
  if( offset !== undefined && offset !== 0 ) cameraZ *= offset;

  jobview_camera.position.set( center.x, center.y, cameraZ );

  // set the far plane of the camera so that it easily encompasses the whole object
  const minZ = boundingBox.min.z;
  const cameraToFarEdge = ( minZ < 0 ) ? -minZ + cameraZ : cameraZ - minZ;

  jobview_camera.far = cameraToFarEdge * 3;
  jobview_camera.updateProjectionMatrix();

  if ( jobview_controls !== undefined ) {

    // set camera to rotate around center of loaded object
    jobview_controls.target = center;

    // prevent camera from zooming out far enough to create far plane cutoff
    jobview_controls.maxDistance = cameraToFarEdge * 2;
  }
}


function jobview_grid(){
  if (!('workspace' in app_config_main) || !('grid_mm' in app_config_main) ) {
    return
  }
  var w_mm = app_config_main.workspace[0]
  var line_every_mm = app_config_main.grid_mm
  var every_px = (jobview_width*line_every_mm)/w_mm
  jobview_gridLayer = new paper.Layer()
  jobview_gridLayer.transformContent = false
  jobview_gridLayer.pivot = new paper.Point(0,0)
  jobview_gridLayer.activate()
  var grid_group = new paper.Group()
  // vertical
  var x = every_px
  while (x < jobview_width) {
    var line = new paper.Path()
    line.add([x,0], [x,jobview_height])
    grid_group.addChild(line);
    x += every_px
  }
  // horizontal
  var y = every_px
  while (y < jobview_height) {
    var line = new paper.Path()
    line.add([0,y], [jobview_width,y])
    grid_group.addChild(line);
    y += every_px
  }
  grid_group.strokeColor = '#dddddd';
}


function jobview_head(){
  jobview_headLayer = new paper.Layer()
  jobview_headLayer.transformContent = false
  jobview_headLayer.pivot = new paper.Point(0,0)
  jobview_headLayer.activate()
  var head_group = new paper.Group()

  var line1 = new paper.Path()
  line1.add([-10,0],[10,0])
  head_group.addChild(line1)

  var line2 = new paper.Path()
  line2.add([0,-10],[0,10])
  head_group.addChild(line2)

  var circ1 = new paper.Path.Circle([0,0],5)
  head_group.addChild(circ1)

  head_group.strokeColor = '#aa0000';
}

function jobview_head_move(pos, offset) {
  jobview_tool.position.set(pos[0], pos[1], pos[2])
  jobview_render()
  // var x = (pos[0]+offset[0])*jobview_mm2px
  // var y = (pos[1]+offset[1])*jobview_mm2px
  // jobview_headLayer.position = new paper.Point(x, y)
  // paper.view.draw()
}


function jobview_testpath(){
  var material = new THREE.LineBasicMaterial({
    color: 0x0000ff
  });

  var geometry = new THREE.Geometry();
  geometry.vertices.push(
    new THREE.Vector3(-100, 0, 0),
    new THREE.Vector3(0, 100, 0),
    new THREE.Vector3(100, 0, 0)
  );

  var line = new THREE.Line(geometry, material);
  jobview_scene.add(line);
}
