
// module to handle job data
// read, write, draw, stats, cleanup/filter
//
// {
//     "passes": [{"items": [0]}],
//     "items": [{"def": 0}],
//     "defs": [
//        {"data":[["S",950],["G0",[0,0,0]]],
//         "tool":"T1",
//         "toolinfo":"ball nose",
//         "rates":[], "freqs":[],
//         "mists":True,
//         "floods":True,
//         "bbox":[xmin,ymin,zmin,xmax,ymax,zmax]},
//     ]
// }


jobhandler = {

  head : {},
  defs : [],
  name : "",
  pass : 0,
  feed_length : 0,
  bbox : [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity],
  job_active_ : false,

  clear : function() {
    this.head = {}
    this.defs = []
    name = ""
    this.pass = 0
    this.feed_length = 0
    this.bbox = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity]
    job_active_ = false
    jobview_clear()
    $('#job_info_name').html('')
    $('#job_info_length').html('')
    $('#info_content').html('')
    $('#info_btn').hide()
    $('#passes_status').html('')
    $('#tool_btn_lable').html('Tx')
  },

  isEmpty : function() {
    return (!this.defs.length)
  },

  job_start : function() {
    this.job_active_ = true
  },

  job_active : function() {
    return this.job_active_
  },

  job_end : function() {
    this.job_active_ = false
    this.next_pass()
  },


  // setters //////////////////////////////////

  set : function(job, name, optimize) {
    this.clear()
    // handle json string representations as well
    if (typeof(job) === 'string') {
      job = JSON.parse(job)
    }
    // check head and defs
    if ('head' in job && 'kind' in job.head && job.head.kind == 'mill' &&
        'defs' in job && job.defs.length) {
      // set name
      this.name = name
      $('title').html("DriveboardApp - "+name)
      // head
      if ('head' in job) {
        this.head = job.head
      }
      // defs
      for (var i = 0; i < job.defs.length; i++) {
        var def = job.defs[i]
        this.defs.push(def)
      }
      // optimize
      if (optimize) {
        // this.segmentizeLongLines()
      }
      // stats
      this.calculate_stats()
      // job info
      $('#job_info_name').html(this.name)
      $('#info_btn').show()
      // info modal
      var html = ''
      html += "name : " + this.name + "<br>"
      html += "length : " + (this.feed_length/1000).toFixed(2) + "m<br>"
      html += "bbox : x["+this.bbox[0].toFixed(0)+", "+this.bbox[3].toFixed(0)+
                   "] y["+this.bbox[1].toFixed(0)+", "+this.bbox[4].toFixed(0)+
                   "] z["+this.bbox[2].toFixed(0)+", "+this.bbox[5].toFixed(0)+"]<br>"
      $('#info_content').html(html)
      // handle passes
      this.add_passes()
    } else {
      $().uxmessage('warn', "Invalid. No job loaded.")
    }
  },



  // getters //////////////////////////////////

  get : function() {
    return {'head':this.head, 'defs':this.defs}
  },

  get_pass : function() {
    return {'head':this.head, 'defs':[this.defs[this.pass]]}
  },

  get_json : function() {
    return this.jsonify(this.get())
  },

  get_pass_json : function() {
    return this.jsonify(this.get_pass())
  },

  get_pass_xybbox_json : function() {
    var def = this.defs[this.pass]  // active pass/def
    var data = []
    if ('bbox' in def) {
      var bbox = def.bbox
      data.push(['G0', [bbox[0],bbox[1],null]])
      data.push(['G0', [bbox[0],bbox[4],null]])
      data.push(['G0', [bbox[3],bbox[4],null]])
      data.push(['G0', [bbox[3],bbox[1],null]])
      data.push(['G0', [bbox[0],bbox[1],null]])
    }
    return this.jsonify({'head':this.head, 'defs':[{'data':data}]})
  },

  jsonify : function(job) {
    // json stringify while limiting numbers to 3 decimals
    return JSON.stringify(job ,function(key, val) {
      if (isNaN(+key) || val === null) return val
      return val.toFixed ? Number(val.toFixed(3)) : val
    }, '\t')
  },


  // rendering //////////////////////////////////

  add_to_scene : function () {
    jobview_clear()
    // add all defs
    for (var i = 0; i < this.defs.length; i++) {
      var def = this.defs[i]
      var material = new THREE.LineBasicMaterial({
        // color: 0x0000ff
        color: (Math.random()*0xaaaaaa<<0)
      })
      var geometry = new THREE.Geometry();

      for (var j=0; j<def.data.length; j++) {
        var pathitem = def.data[j]
        if (pathitem[0] == "G0" || pathitem[0] == "G1") {
          var vert = pathitem[1]
          geometry.vertices.push(
            new THREE.Vector3(vert[0], vert[1], vert[2])
          )
        }
      }
      var path = new THREE.Line(geometry, material)
      jobview_path.add(path)
      // jobview_fit_camera_to_object(jobview_path, 10)
      // fitCameraToObject(jobview_path, 3)
    }
  },


  bounds_add_to_scene : function () {

  },



  // passes  ////////////////////////////////////

  add_passes : function() {
    $('#passes_status').append('<tr class="nodrag"><th>T#</th><th>Tool \
                                Info</th><th>RPMs</th><th>Feedrates</th></tr>')
    for (var i = 0; i < this.defs.length; i++) {
      var def = this.defs[i]
      var cells = ""
      cells += "<td>"+def.tool+"</td>"
      cells += "<td>"+def.toolinfo+"</td>"
      cells += "<td>"+Math.min(...def.freqs)+"-"+Math.max(...def.freqs)+"</td>"
      cells += "<td>"+Math.min(...def.rates)+"-"+Math.max(...def.rates)+"</td>"
      $('#passes_status').append('<tr class="nodrag">'+cells+"</tr>")
    }
    $('#tool_btn_lable').html(this.defs[this.pass].tool)
    $('#passes_status tr').eq(this.pass+1).addClass('info')
    $('#passes_status tr').click(function(e){
      jobhandler.pass = $(this).index()-1
      $('#passes_status tr').removeClass('info')
      $(this).addClass('info')
      var tool = jobhandler.defs[jobhandler.pass].tool
      $('#tool_btn_lable').html(tool)
    })

  },

  next_pass : function() {
    this.pass = (this.pass+1) % this.defs.length
    $('#passes_status tr').removeClass('info')
    $('#passes_status tr').eq(this.pass+1).addClass('info')
    $('#tool_btn_lable').html(this.defs[this.pass].tool)
  },



  // stats //////////////////////////////////////

  calculate_stats : function() {
    // calculate bounding boxes and feed lengths for each def
    // loop through defs
    for (var i = 0; i < this.defs.length; i++) {
      var def = this.defs[i]
      var x_prev = 0
      var y_prev = 0
      var z_prev = 0
      var length = 0
      var bbox = [Infinity, Infinity, Infinity, -Infinity, -Infinity, -Infinity]
      for (var j=0; j<def.data.length; j++) {
        var action = def.data[j]
        if (action[0] == 'G0' || (action[0] == 'G1')) {
          var x = action[1][0]
          var y = action[1][1]
          var z = action[1][2]
          if (action[0] == 'G1') {
            length += Math.sqrt((x-x_prev)*(x-x_prev)+(y-y_prev)*(y-y_prev)+(z-z_prev)*(z-z_prev))
            this.bboxExpand(bbox, x, y, z)
          }
          x_prev = x
          y_prev = y
          z_prev = z
        }
      }
      this.feed_length += length
      this.bboxExpand2(this.bbox, bbox)
    }
  },


  bboxExpand : function(bbox, x, y, z) {
    if (x < bbox[0]) {bbox[0] = x}
    else if (x > bbox[3]) {bbox[3] = x}
    if (y < bbox[1]) {bbox[1] = y}
    else if (y > bbox[4]) {bbox[4] = y}
    if (z < bbox[2]) {bbox[2] = z}
    else if (z > bbox[5]) {bbox[5] = z}
  },


  bboxExpand2 : function(bbox, bbox2) {
    this.bboxExpand(bbox, bbox2[0], bbox2[1], bbox2[2])
    this.bboxExpand(bbox, bbox2[3], bbox2[4], bbox2[5])
  },


  // path optimizations /////////////////////////

  segmentizeLongLines : function() {
    // TODO: make this also work 3D
    var x_prev = 0
    var y_prev = 0
    var z_prev = 0
    var d2 = 0
    var length_limit = app_config_main.max_segment_length
    var length_limit2 = length_limit*length_limit
    // lerp helper function
    var lerp = function(x0, y0, z0, x1, y1, z1, t) {
      return [x0*(1-t)+x1*t, y0*(1-t)+y1*t, z0*(1-t)+z1*t]
    }
    // loop through defs
    for (var i = 0; i < this.defs.length; i++) {
      var def = this.defs[i]
      if (def.kind == "mill") {
        var path = def.data
        if (path.length > 1) {
          var new_path = []
          var copy_from = 0
          var x = path[0][0]
          var y = path[0][1]
          // ignore seek lines for now
          x_prev = x
          y_prev = y
          for (vertex=1; vertex<path.length; vertex++) {
            var x = path[vertex][0]
            var y = path[vertex][1]
            d2 = (x-x_prev)*(x-x_prev) + (y-y_prev)*(y-y_prev)
            // check length for each feed line
            if (d2 > length_limit2) {
              // copy previous verts
              for (var n=copy_from; n<vertex; n++) {
                new_path.push(path[n])
              }
              // add lerp verts
              var t_step = 1/(Math.sqrt(d2)/length_limit)
              for(var t=t_step; t<0.99; t+=t_step) {
                new_path.push(lerp(x_prev, y_prev, x, y, t))
              }
              copy_from = vertex
            }
            x_prev = x
            y_prev = y
          }
          if (new_path.length > 0) {
            // add any rest verts from path
            for (var p=copy_from; p<path.length; p++) {
              new_path.push(path[p])
            }
            copy_from = 0
            paths[k] = new_path
          }
        }
      }
    }
  },


}
