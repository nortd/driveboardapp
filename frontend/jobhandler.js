
// module to handle job data
// read, write, draw, stats, cleanup/filter
//
// {
//      "head": {
//          "noreturn": True,          # do not return to origin, default: False
//          "optimized": 0.08,         # optional, tolerance to which it was optimized, default: 0 (not optimized)
//       },
//      "passes": [
//          {
//              "items": [0],          # item by index
//              "relative": True,      # optional, default: False
//              "seekrate": 6000,      # optional, rate to first vertex
//              "feedrate": 2000,      # optional, rate to other vertices
//              "intensity": 100,      # optional, default: 0 (in percent)
//              "pierce_time": 0,      # optional, default: 0
//              "pxsize": [0.4],       # optional
//              "air_assist": "pass",  # optional (feed, pass, off), default: pass
//              "aux1_assist": "off",  # optional (feed, pass, off), default: off
//          }
//      ],
//     "items": [
//        {"def":0, "translate":[0,0,0], "color":"#BADA55"}
//     ],
//     "defs": [
//        {"kind":"path", "data":[[[0,10,0]]]},
//        {"kind":"fill", "data":[[[0,10,0]]], "pxsize":0.4},
//        {"kind":"image", "data":<data in base64>, "pos":[0,0], "size":[300,200]},
//     ],
//     "stats":{"items":[{"bbox":[x1,y1,x2,y2], "len":100}], "all":{}}
// }


jobhandler = {

  passes : [],
  items : [],
  defs : [],
  stats : {},
  itemidx2group : [],
  name : "",
  path_group : undefined,
  fill_group : undefined,
  image_group : undefined,

  clear : function() {
    this.passes = []
    this.items = []
    this.defs = []
    this.stats = {}
    this.itemidx2group = []
    name = ""
    jobview_clear()
    passes_clear()
    $('#job_info_name').html('')
    $('#job_info_length').html('')
    $('#info_content').html('')
    $('#info_btn').hide()
  },

  isEmpty : function() {
    return (!this.defs.length || !this.items.length)
  },

  hasPasses : function() {
    return !!this.passes.length
  },

  loopItems : function(func, kind) {
    if (kind === undefined) {
      for (var i = 0; i < this.items.length; i++) {
        func(this.items[i], i)
      }
    } else {
      for (var i = 0; i < this.items.length; i++) {
        if (kind.indexOf(this.defs[this.items[i].def].kind) != -1) {
          func(this.items[i], i)
        }
      }
    }
  },

  loopPasses : function(func) {
    for (var i = 0; i < this.passes.length; i++) {
      var pass = this.passes[i]
      var item_idxs = []
      for (var j = 0; j < pass.items.length; j++) {
        item_idxs.push(pass.items[j])
      }
      func(pass, item_idxs)
    }
  },


  // setters //////////////////////////////////

  set : function(job, name, optimize, donefunc) {
    this.clear()
    this.name = name
    $('title').html("DriveboardApp - "+name)
    // handle json string representations as well
    if (typeof(job) === 'string') {
      job = JSON.parse(job)
    }
    // defs and items
    if (job.defs.length && job.items.length) {
      // head
      if ('head' in job) {
        this.head = job.head
      }
      //passes
      if ('passes' in job && job.passes.length) {
        this.passes = job.passes
      }
      // items, defs
      this.defs = job.defs
      this.items = job.items
      if (optimize) {
        this.segmentizeLongLines()
      }

      var image_to_load = -1
      function allImagesLoaded() {
        if (image_to_load <= 0) {
          // passes, show in gui
          passes_set_assignments()
          donefunc()
        } else {
          image_to_load -= 1
        }
      }

      // convert base64 image data to Image objects
      for (var i = 0; i < this.defs.length; i++) {
        var def = this.defs[i]
        if (def.kind == "image") {
          image_to_load += 1
        }
      }
      for (var i = 0; i < this.defs.length; i++) {
        var def = this.defs[i]
        if (def.kind == "image") {
          var img_base64 = def.data
          def.data = new Image()
          def.data.onload = allImagesLoaded
          def.data.src = img_base64  // NOTE: this is async
        }
      }

      // colors
      this.normalizeColors()
      // stats
      if ('stats' in job) {
        this.stats = job.stats
      } else {
        this.calculateStats()
      }
      // job info
      $('#job_info_name').html(this.name)
      $('#info_btn').show()
      // info modal
      var html = ''
      html += "name : " + this.name + "<br>"
      $('#info_content').html(html)

      // no images, still need to run some code
      if (image_to_load == -1) {
        allImagesLoaded()
      }
    }
  },



  // getters //////////////////////////////////

  get : function() {
    // convert images back to base64
    var defs_out = []
    for (var i = 0; i < this.defs.length; i++) {
      var def = this.defs[i]
      if (def.kind == "image") {
        defs_out.push({'kind':"image",
                       'pos':def.pos,
                       'size':def.size,
                       'data':def.data.src})
      } else {
        defs_out.push(def)
      }
    }
    return {'head':this.head, 'passes':this.passes,
            'items':this.items, 'defs':defs_out, 'stats':this.stat}
  },

  getJson : function() {
    // json stringify while limiting numbers to 3 decimals
    return JSON.stringify(this.get() ,function(key, val) {
        if (isNaN(+key)) return val
        return val.toFixed ? Number(val.toFixed(3)) : val
      }, '\t')
  },

  getKind : function(item) {
    return this.defs[item.def].kind
  },

  getAllColors : function() {
    colors = []
    this.loopItems(function(item, i){
      if ("color" in item) {
        colors.push(item.color)
      }
    })
    return colors
  },

  getImageThumb : function(imgitem, width, height) {
    var img = this.defs[imgitem.def]
    if (width <= 0 ) {
      // scale proportionally by height
      var w = img.size[0]*(height/img.size[1])
      if (width < 0) {
        // use this negative value for max width
        width = Math.min(w, -width)
      } else {
        width = w
      }
    } else if (height <= 0) {
      // scale proportionally by width
      var h = img.size[1]*(width/img.size[0])
      if (height < 0) {
        // use this negative value for max height
        height = Math.min(h, -height)
      } else {
        height = h
      }
    }
    var canvas = document.createElement('canvas')
    canvas.width = width
    canvas.height = height
    canvas.getContext('2d').drawImage(img.data, 0, 0, width, height)
    var thumb = new Image()
  	thumb.src = canvas.toDataURL("image/png")
    return thumb
  },


  // rendering //////////////////////////////////

  render : function () {
    var x = 0
    var y = 0
    jobview_clear()
    jobview_feedLayer.activate()
    this.image_group = new paper.Group()
    this.fill_group = new paper.Group()
    this.path_group = new paper.Group()
    // images
    this.loopItems(function(image, i){
      var img = jobhandler.defs[image.def]
      var group = new paper.Group()
      group.itemidx = i
      jobhandler.itemidx2group[i] = group
      jobhandler.image_group.addChild(group)
      var pos_x = img.pos[0]*jobview_mm2px
      var pos_y = img.pos[1]*jobview_mm2px
      var img_w = img.size[0]*jobview_mm2px
      var img_h = img.size[1]*jobview_mm2px
      var img_paper = new paper.Raster(img.data)
      group.addChild(img_paper);
      img_paper.scale(img_w/img.data.width, img_h/img.data.height)
      img_paper.position = new paper.Point(pos_x+0.5*img_w, pos_y+0.5*img_h)
    }, "image")
    // fills
    this.loopItems(function(fill, i){
      add_vector(fill, i, jobhandler.fill_group)
    }, "fill")
    // paths
    this.loopItems(function(path, i){
      add_vector(path, i, jobhandler.path_group)
    }, "path")
    // fills, paths helper function
    function add_vector(item, i, parent_group) {
      var path = jobhandler.defs[item.def].data
      jobview_feedLayer.activate()
      var group = new paper.Group()
      group.itemidx = i
      jobhandler.itemidx2group[i] = group
      parent_group.addChild(group)
      for (var j=0; j<path.length; j++) {
        var pathseg = path[j]
        if (pathseg.length > 0) {
          // seek move
          jobview_seekLayer.activate()
          var p_seek = new paper.Path()
          p_seek.strokeColor = '#dddddd'
          p_seek.add([x,y])
          x = pathseg[0][0]*jobview_mm2px
          y = pathseg[0][1]*jobview_mm2px
          p_seek.add([x,y])
          // feed move
          jobview_feedLayer.activate()
          var p_feed = new paper.Path()
          group.addChild(p_feed)
          p_feed.strokeColor = item.color || '#000000'
          p_feed.add([x,y])
          for (vertex=1; vertex<pathseg.length; vertex++) {
            x = pathseg[vertex][0]*jobview_mm2px
            y = pathseg[vertex][1]*jobview_mm2px
            p_feed.add([x,y])
          }
        }
      }
    }
  },


  renderBounds : function () {
    jobview_boundsLayer.removeChildren()
    jobview_boundsLayer.activate()
    var bbox = this.getActivePassesBbox()
    var all_bounds = new paper.Path.Rectangle(
        new paper.Point(bbox[0]*jobview_mm2px,bbox[1]*jobview_mm2px),
        new paper.Point(bbox[2]*jobview_mm2px,bbox[3]*jobview_mm2px))
    all_bounds.strokeWidth = 2
    all_bounds.strokeColor = '#666666'
    all_bounds.dashArray = [2, 4]
  },


  draw : function () {
    paper.view.draw()
  },


  selectItem : function(idx) {
    var group = this.itemidx2group[idx]
    group.selected = true
    jobview_item_selected = idx
    setTimeout(function() {
      group.selected = false
      jobview_item_selected = undefined
      paper.view.draw()
    }, 1500);
    paper.view.draw()
  },


  // passes and colors //////////////////////////

  normalizeColors : function() {
    this.loopItems(function(path, i){
      if (!('color' in path)) {
        if (path === jobhandler.items[0]) {
          path.color = "#000000"
        } else {
          var random_color = '#'+(Math.random()*0xaaaaaa<<0).toString(16)
          path.color = random_color
        }
      }
    }, "path")
  },



  // stats //////////////////////////////////////

  calculateStats : function() {
    // calculate bounding boxes and feed lengths for each item
    // saves results in this.stats like so:
    // {'all':{'bbox':[xmin,ymin,xmax,ymax], 'len':numeral},
    //  'items':[{'bbox':[xmin,ymin,xmax,ymax], 'len':numeral}, ...],}
    this.stats.items = []
    var length_all = 0
    var bbox_all = [Infinity, Infinity, -Infinity, -Infinity]
    // images
    this.loopItems(function(image, i){
      var img = jobhandler.defs[image.def]
      var width = img.size[0]
      var height = img.size[1]
      var left = img.pos[0]
      var right = img.pos[0]+width
      var top = img.pos[1]
      var bottom = img.pos[1]+height
      var line_count = Math.floor(height/app_config_main.pxsize)
      var image_length = width * line_count
      var image_bbox = [left, top, right, bottom]
      jobhandler.stats.items[i] = {'bbox':image_bbox, 'len':image_length}
      length_all += image_length
      jobhandler.bboxExpand2(bbox_all, image_bbox)
    }, "image")
    // paths and fills
    this.loopItems(function(vectoritem, i){
      var path = jobhandler.defs[vectoritem.def].data
      var path_length = 0
      var path_bbox = [Infinity, Infinity, -Infinity, -Infinity]
      for (var poly = 0; poly < path.length; poly++) {
        var polyline = path[poly]
        var x_prev = 0
        var y_prev = 0
        if (polyline.length > 1) {
          var x = polyline[0][0]
          var y = polyline[0][1]
          jobhandler.bboxExpand(path_bbox, x, y)
          x_prev = x
          y_prev = y
          for (vertex=1; vertex<polyline.length; vertex++) {
            var x = polyline[vertex][0]
            var y = polyline[vertex][1]
            path_length +=
              Math.sqrt((x-x_prev)*(x-x_prev)+(y-y_prev)*(y-y_prev))
            jobhandler.bboxExpand(path_bbox, x, y)
            x_prev = x
            y_prev = y
          }
        }
      }
      jobhandler.stats.items[i] = {'bbox':path_bbox, 'len':path_length}
      length_all += path_length
      jobhandler.bboxExpand(bbox_all, path_bbox[0], path_bbox[1])
      jobhandler.bboxExpand(bbox_all, path_bbox[2], path_bbox[3])
    }, "path fill")
    // store in object var
    this.stats['all'] = {'bbox':bbox_all, 'len':length_all}
  },


  getActivePassesLength : function() {
    var length = 0
    this.loopPasses(function(pass, item_idxs){
      for (var i = 0; i < item_idxs.length; i++) {
        var item = item_idxs[i]
        length += jobhandler.stats.items[item_idxs[i]].len
      }
    })
    return length
  },


  getActivePassesBbox : function() {
    var bbox = [Infinity, Infinity, -Infinity, -Infinity]
    this.loopPasses(function(pass, item_idxs){
      for (var i = 0; i < item_idxs.length; i++) {
        var item = item_idxs[i]
        jobhandler.bboxExpand2(bbox, jobhandler.stats.items[item_idxs[i]].bbox)
      }
    })
    return bbox
  },


  bboxExpand : function(bbox, x, y) {
    if (x < bbox[0]) {bbox[0] = x}
    else if (x > bbox[2]) {bbox[2] = x}
    if (y < bbox[1]) {bbox[1] = y}
    else if (y > bbox[3]) {bbox[3] = y}
  },


  bboxExpand2 : function(bbox, bbox2) {
    this.bboxExpand(bbox, bbox2[0], bbox2[1])
    this.bboxExpand(bbox, bbox2[2], bbox2[3])
  },


  // path optimizations /////////////////////////

  segmentizeLongLines : function() {
    // TODO: make this also work 3D
    var x_prev = 0
    var y_prev = 0
    var d2 = 0
    var length_limit = app_config_main.max_segment_length
    var length_limit2 = length_limit*length_limit
    // lerp helper function
    var lerp = function(x0, y0, x1, y1, t) {
      return [x0*(1-t)+x1*t, y0*(1-t)+y1*t]
    }
    // loop through defs
    for (var i = 0; i < this.defs.length; i++) {
      var def = this.defs[i]
      if (def.kind == "path" || def.kind == "fill") {
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
