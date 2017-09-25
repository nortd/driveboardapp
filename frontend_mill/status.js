
var status_cache = {}
var status_every_default = 500
var status_every = status_every_default
var status_last_refresh = 0
var status_last_interval = 0
var status_refresh_intime_count = 0


function status_init() {
  status_cache = {
    //// always
    'server': false,
    'serial': undefined,            // is serial connected
    'ready': false,                 // is hardware idle (and not stop mode)
    //// when hardware connected
    'appver': undefined,
    'firmver': undefined,
    'paused': false,
    'pos':[0.0, 0.0, 0.0],
    'underruns': 0,          // how many times machine is waiting for serial data
    'stackclear': Infinity,  // minimal stack clearance (must stay above 0)
    'progress': 1.0,

    //// stop conditions
    // indicated when key present
    'stops': {'dirty':true},
    // possible keys:
    // x1, x2, y1, y2, z1, z2,
    // requested, buffer, marker, data, command, parameter, transmission

    'info':{'dirty':true},
    // possible keys: door, chiller

    //// only when hardware idle
    'offset': [0.0, 0.0, 0.0],
    'feedrate': 0.0,
    'intensity': 0.0,
    'duration': 0.0,
    'pixelwidth': 0.0
  }
}


function status_ready() {
  status_init()
  // start polling loop
  // polls at interval set by 'status_every' or however fast it can
  status_refresh()
}


function status_refresh() {
  status_last_interval = Date.now()-status_last_refresh
  // request
  if (status_last_interval > status_every) {
    // refresh inverval throttling
    if (status_last_interval > 1.1*status_every) {
      status_every_default = Math.min(Math.round(1.1*status_every_default), 2000)  // increase interval
      status_set_refresh()
      $("#head_position").clearQueue()
      // $().uxmessage('notice', "status refresh slow. " + status_last_interval + "instead of" + status_every)
    } else {
      status_refresh_intime_count += 1
      if (status_refresh_intime_count > 10) {
        status_refresh_intime_count = 0
        status_every_default = Math.max(Math.round(0.8*status_every_default), 500)  // decrease interval
      }
      status_set_refresh()
    }
    // get appconfig from server
    status_last_refresh = Date.now()
    request_get({
      url:'/status',
      success: function (data) {
        $("#status_glyph").animate({"opacity": 1.0},50).animate({"opacity": 0.5},200)
        // $().uxmessage('success', "status received.")
        // var data = JSON.parse(e.data)
        data.server = true
        status_handle_message(data)
      },
      error: function (data) {
        // $().uxmessage('error', "Failed to receive status.")
        status_handle_message({'server':false, 'serial':false})
      },
      complete: function (data) {
        // recursive call
        status_refresh()
      }
    })
  } else {
    // try again a little later
    setTimeout(status_refresh, 100)
  }
}


function status_handle_message(status) {
  // call handlers for data points, only when a change occurs
  for (var k in status_cache) {
    if (k in status) {
      if (status_check_new(status_cache[k], status[k])) {
        status_handlers[k](status)   // call handler
        status_cache[k] = status[k]  // update cache
      }
    }
  }
}

function status_check_new(data1, data2) {
  // compare strings, numbers bools, and arrays, maps by value
  var flag = false
  if (Array.isArray(data1)) {
    // check array values
    if (data1.length == data2.length) {
      for (var i = 0; i < data1.length; i++) {
        if (data1[i] !== data2[i]) {
          flag = true
          break
        }
      }
    } else {
      flag = true
    }
  } else if (typeof(data1) == 'string'
          || typeof(data1) == 'number'
          || typeof(data1) == 'boolean'
          || typeof(data1) == 'undefined') {
    if (data1 !== data2) {
      flag = true
    }
  } else if (typeof(data1) == 'object' && data1 !== null && data2 !== null) {
    if (Object.keys(data1).length == Object.keys(data2).length) {
      for(var k in data1) {
        if (data1[k] !== data2[k]) {
          flag = true
          break
        }
      }
    } else {
      flag = true
    }
  } else {
    flag = false
  }
  return flag
}


function status_set_main_button(status) {
  if (!status.server) {  // disconnected
    $('#connect_modal').modal('show')
    $("#status_btn").removeClass("btn-warning btn-success").addClass("btn-danger")
  } else {  // connected
    $('#connect_modal').modal('hide')
    if (!$.isEmptyObject(status.stops) || !status.serial) {  // connected but stops, serial down
      $("#status_btn").removeClass("btn-warning btn-success").addClass("btn-danger")
    } else {
      if (!$.isEmptyObject(status.info)) {  // connected, no stops, serial up, warnings
        $("#status_btn").removeClass("btn-danger btn-success").addClass("btn-warning")
      } else {  // connected, no stops, serial up, no warnings
        $("#status_btn").removeClass("btn-danger btn-warning").addClass("btn-success")
      }
    }
  }
}

function status_set_refresh() {
  status_every = status_every_default  // focused and busy
  if (app_visibility) {  // app focused
    if (!status_cache.serial || status_cache.ready) {  // focused and ready -> idle
      status_every = 4000
    }
  } else {  // app blured
    status_every = 10000
  }
  // console.log(status_every)
}


///////////////////////////////////////////////////////////////////////////////
// these functions are called when the various data points change /////////////

var status_handlers = {
  //// always, evn when no hardware connected
  'server': function (status) {
    if (status.server) {  // server connected
      $().uxmessage('success', "Server says HELLO!")
      $("#status_server").removeClass("label-danger").addClass("label-success")
      status_init()
      status.server = true
    } else {  // server disconnected
      $().uxmessage('warning', "Server LOST.")
      $("#status_server").removeClass("label-success").addClass("label-danger")
      // gray-out all dependant indicators
      $('#status_serial').removeClass("label-danger label-success").addClass("label-default")
      $(".status_hw").removeClass("label-success label-danger label-warning").addClass("label-default")
    }
    status_set_main_button(status)
  },
  'serial': function (status) {
    if (status.serial) {  // serial up
      $('#status_serial').removeClass("label-default label-danger").addClass("label-success")
    } else {  // serial down
      $('#status_serial').removeClass("label-default label-success").addClass("label-danger")
      // gray-out all hardware indicators
      $(".status_hw").removeClass("label-success label-danger label-warning").addClass("label-default")
    }
    status_set_main_button(status)
  },
  'ready': function (status) {
    // hardware sends this when idle but not in a "stop mode" (e.g. error)
    if (status.ready) {
      app_run_btn.stop()
      $('#boundary_btn').prop('disabled', false)
      $('#origin_btn').prop('disabled', false)
      $('#homing_btn').prop('disabled', false)
      $('#offset_btn').removeClass('disabled')
      $('#motion_btn').removeClass('disabled')
      $('#jog_btn').removeClass('disabled')
    } else {
      app_run_btn.start()
      $('#boundary_btn').prop('disabled', true)
      $('#origin_btn').prop('disabled', true)
      $('#homing_btn').prop('disabled', true)
      $('#offset_btn').addClass('disabled')
      $('#motion_btn').addClass('disabled')
      $('#jog_btn').addClass('disabled')
    }
    status_cache.ready = status.ready  // deed this before set_refresh
    status_set_refresh()
  },
  //// when hardware connected
  'appver': function (status) {
    if (status.appver) {
      $('#app_version').html(status.appver)
    } else {
      $('#app_version').html('&lt;not received&gt;')
    }
  },
  'firmver': function (status) {
    if (status.firmver) {
      // $().uxmessage('notice', "Firmware v" + status.firmver)
      $('#firm_version').html(status.firmver)
    } else {
      $('#firm_version').html("&lt;unknow&gt;")
    }
  },
  'paused': function (status) {
    if (status.paused) {
      // pause button
      $("#pause_btn").removeClass("btn-default").addClass("btn-primary")
      $("#pause_glyph").hide()
      $("#play_glyph").show()
      // run button
      $('#run_btn span.ladda-spinner').hide()
    } else {
      // pause button
      $("#pause_btn").removeClass("btn-primary").addClass("btn-default")
      $("#play_glyph").hide()
      $("#pause_glyph").show()
      // run button
      $('#run_btn span.ladda-spinner').show()
    }
  },
  'pos':function (status) {
    // jobview_head_move(status.pos, status.offset)
    $("#head_position").animate({
      left: Math.round((status.pos[0]+status.offset[0])*jobview_mm2px-10),
      top: Math.round((status.pos[1]+status.offset[1])*jobview_mm2px-10),
    }, status_every, 'linear' )
  },
  'underruns': function (status) {},
  'stackclear': function (status) {
    if (typeof(status.stackclear) == 'number') {
      if (status.stackclear < 200) {
        $().uxmessage('warn', "Drive hardware low on memory.")
      } else if (status.stackclear < 100) {
        $().uxmessage('error', "Drive hardware low on memory. Stopping!")
        $('#stop_btn').trigger('click')
      }
    }
  },
  'progress': function (status) {
    app_run_btn.setProgress(status.progress)
  },
  //// stop conditions
  'stops': function (status) {
    // reset all stop error indicators
    $(".status_hw").removeClass("label-default")
    $('#status_limit_x1').removeClass("label-danger").addClass("label-success")
    $('#status_limit_x2').removeClass("label-danger").addClass("label-success")
    $('#status_limit_y1').removeClass("label-danger").addClass("label-success")
    $('#status_limit_y2').removeClass("label-danger").addClass("label-success")
    $('#status_limit_z1').removeClass("label-danger").addClass("label-success")
    $('#status_limit_z2').removeClass("label-danger").addClass("label-success")
    $('#status_requested').removeClass("label-danger").addClass("label-success")
    $('#status_buffer').removeClass("label-danger").addClass("label-success")
    $('#status_marker').removeClass("label-danger").addClass("label-success")
    $('#status_data').removeClass("label-danger").addClass("label-success")
    $('#status_command').removeClass("label-danger").addClass("label-success")
    $('#status_parameter').removeClass("label-danger").addClass("label-success")
    $('#status_transmission').removeClass("label-danger").addClass("label-success")
    // set stop error indicators
    if ('stops' in status) {
      if (status.stops.x1) {$('#status_limit_x1').removeClass("label-success").addClass("label-danger")}
      if (status.stops.x2) {$('#status_limit_x2').removeClass("label-success").addClass("label-danger")}
      if (status.stops.y1) {$('#status_limit_y1').removeClass("label-success").addClass("label-danger")}
      if (status.stops.y2) {$('#status_limit_y2').removeClass("label-success").addClass("label-danger")}
      if (status.stops.z1) {$('#status_limit_z1').removeClass("label-success").addClass("label-danger")}
      if (status.stops.z2) {$('#status_limit_z2').removeClass("label-success").addClass("label-danger")}
      if (status.stops.requested) {$('#status_requested').removeClass("label-success").addClass("label-danger")}
      if (status.stops.buffer) {$('#status_buffer').removeClass("label-success").addClass("label-danger")}
      if (status.stops.marker) {$('#status_marker').removeClass("label-success").addClass("label-danger")}
      if (status.stops.data) {$('#status_data').removeClass("label-success").addClass("label-danger")}
      if (status.stops.command) {$('#status_command').removeClass("label-success").addClass("label-danger")}
      if (status.stops.parameter) {$('#status_parameter').removeClass("label-success").addClass("label-danger")}
      if (status.stops.transmission) {$('#status_transmission').removeClass("label-success").addClass("label-danger")}
    }
    status_set_main_button(status)
  },
  'info': function (status) {
    // reset all info indicators
    $(".status_hw").removeClass("label-default")
    $('#status_door').removeClass("label-warning").addClass("label-success")
    $('#status_chiller').removeClass("label-warning").addClass("label-success")
    // set info indicators
    if ('info' in status) {
      if (status.info.door) {$('#status_door').removeClass("label-success").addClass("label-warning")}
      if (status.info.chiller) {$('#status_chiller').removeClass("label-success").addClass("label-warning")}
    }
    status_set_main_button(status)
  },
  //// only when hardware idle
  'offset': function (status) {
    if (status.offset.length == 3) {
      var x_mm = status.offset[0]
      var y_mm = status.offset[1]
      if (x_mm != 0 || y_mm != 0) {
        jobview_offsetLayer.visible = true
      } else {
        jobview_offsetLayer.visible = false
      }
      var x = Math.floor(x_mm*jobview_mm2px)
      var y = Math.floor(y_mm*jobview_mm2px)
      jobview_offsetLayer.position = new paper.Point(x, y)
      jobview_boundsLayer.position = new paper.Point(x, y)
      jobview_seekLayer.position = new paper.Point(x, y)
      jobview_feedLayer.position = new paper.Point(x, y)
      // redraw
      paper.view.draw()
    }
  },
  'feedrate': function (status) {},
  'intensity': function (status) {},
  'duration': function (status) {},
  'pixelwidth': function (status) {}
}
