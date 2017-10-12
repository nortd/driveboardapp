
function control_visible_click(elem, class_) {
  elem.trigger('click')
  elem.addClass(class_)
  setTimeout(function() {
    elem.removeClass(class_)
  }, 100)
}


function controls_ready() {


  // dropdown //////////////////////////////////////////////////////////////

  $("#info_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#info_btn").click(function(e){
    $('#info_modal').modal('toggle')
    return false
  })

  $("#export_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#export_btn").click(function(e){
    if (!jobhandler.isEmpty()) {
      var filename = jobhandler.name
      if (filename.length > 4 && filename.slice(-4,-3) == '.') {
        filename = filename.slice(0,-4)+'.dba'
      } else {
        filename = filename+'.dba'
      }
      jobhandler.passes = passes_get_active()
      var blob = new Blob([jobhandler.get_json()], {type: "application/json;charset=utf-8"})
      saveAs(blob, filename)
    } else {
      $().uxmessage('notice', "Cannot Export. No job loaded.")
    }
    $("body").trigger("click")
    return false
  })

  $("#clear_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#clear_btn").click(function(e){
    jobhandler.clear()
    tools_addfill_init()
    $("body").trigger("click")
    return false
  })

  $("#queue_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#queue_btn").click(function(e){
    $("body").trigger("click")
    $('#queue_modal').modal('toggle')
    return false
  })

  $("#library_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#library_btn").click(function(e){
    $("body").trigger("click")
    $('#library_modal').modal('toggle')
    return false
  })

  $("#flash_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#flash_btn").click(function(e){
    request_get({
      url:'/flash',
      success: function (data) {
        status_cache.firmver = undefined
        $().uxmessage('success', "Flashing successful.")
      }
    })
    $("body").trigger("click")
    return false
  })

  $("#rebuild_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#rebuild_btn").click(function(e){
    request_get({
      url:'/build',
      success: function (data) {
        $().uxmessage('notice', "Firmware build successful.")
      }
    })
    $("body").trigger("click")
    return false
  })

  $("#reset_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#reset_btn").click(function(e){
    request_get({
      url:'/reset',
      success: function (data) {
        status_cache.firmver = undefined
        $().uxmessage('success', "Reset successful.")
      }
    })
    $("body").trigger("click")
    return false
  })



  // navbar ////////////////////////////////////////////////////////////////


  $("#open_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#open_btn").click(function(e){
    $('#open_file_fld').trigger('click')
    return false
  })

  $("#run_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#run_btn").click(function(e){
    // jobhandler.passes = passes_get_active()
    // check for job
    if (jobhandler.isEmpty()) {
      $().uxmessage('notice', "Cannot run. No job loaded.")
      return false
    }
    // check for machine
    // if (!status_cache.serial) {
    //   $().uxmessage('error', "No machine.")
    //   return false
    // }
    // button feedback
    app_run_btn.start()
    $('#boundary_btn').prop('disabled', true)
    status_cache.ready = true  // prevent ready update
    // save job to queue, in-place
    var load_request = {
      'job':jobhandler.get_pass_json(),
      'name':jobhandler.name,
      'optimize':true,
      // 'optimize':false,
      'overwrite':true
    }
    request_post({
      url:'/load',
      data: load_request,
      success: function (jobname) {
        // $().uxmessage('notice', "Saved to queue: "+jobname)
        // run job
        request_get({
          url:'/run/'+jobname,
          success: function (data) {
            jobhandler.job_start()
            // $().uxmessage('success', "Running job ...")
          },
          error: function (data) {
            $().uxmessage('error', "/run error.")
            app_run_btn.stop()
          },
          complete: function (data) {
            // console.log("complete run")
          }
        })
      },
      error: function (data) {
        $().uxmessage('error', "/load error.")
        $().uxmessage('error', JSON.stringify(data), false)
        app_run_btn.stop()
      },
      complete: function (data) {
        status_cache.ready = undefined  // allow ready update
        // console.log("complete load")
      }
    })
    return false
  })

  $("#boundary_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#boundary_btn").click(function(e){
    jobhandler.passes = passes_get_active()
    // check for job
    if (jobhandler.isEmpty()) {
      $().uxmessage('notice', "Cannot run. No job loaded.")
      return false
    }
    // check for passes
    if (!jobhandler.hasPasses()) {
      $().uxmessage('notice', "No passes assigned to this job.")
      return false
    }
    // check for machine
    if (!status_cache.serial) {
      $().uxmessage('error', "No machine.")
      return false
    }
    // send bounds request
    var bounds = jobhandler.getActivePassesBbox()
    request_boundary(bounds, app_config_main.seekrate)
    return false
  })

  $("#pause_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#pause_btn").click(function(e){
    if (status_cache.paused) {  // unpause
      request_get({
        url:'/unpause',
        success: function (data) {
          // $().uxmessage('notice', "Continuing...")
        }
      })
    } else {  // pause
      request_get({
        url:'/pause',
        success: function (data) {
          // $().uxmessage('notice', "Pausing in a bit...")
        }
      })
    }
    return false
  })

  $("#stop_btn").tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  $("#stop_btn").click(function(e){
    request_get({
      url:'/stop',
      success: function (data) {
        setTimeout(function() {
          request_get({
            url:'/unstop',
            success: function (data) {
              request_get({
                url:'/retract',
                success: function (jobname) {
                  $().uxmessage('notice', "Retracting...")
                },
                error: function (data) {},
                complete: function (data) {}
              })
            }
          })
        }, 1500)
      }
    });
    return false
  })



  // footer buttons /////////////////////////////////////////////////////////

  $("#origin_btn").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#origin_btn").click(function(e){
    request_get({
      url:'/retract',
      success: function (data) {
        $().uxmessage('notice', "Retracting to machine zero ...")
      }
    })
    return false
  })

  $("#homing_btn").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#homing_btn").click(function(e){
    request_get({
      url:'/reset',
      success: function (data) {
        request_get({
          url:'/homing',
          success: function (data) {
            $().uxmessage('notice', "Homing ...")
          }
        })
      }
    })
    return false
  })


  // offsets all
  $("#offset_btn").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#offset_btn").click(function(e){
    var xoff = parseFloat($('#x_off_ro').val())
    var yoff = parseFloat($('#y_off_ro').val())
    var zoff = parseFloat($('#z_off_ro').val())
    if (isNaN(xoff)) {xoff=0}
    if (isNaN(yoff)) {yoff=0}
    if (isNaN(zoff)) {zoff=0}
    request_get({
      url:'/offset/'+xoff+'/'+yoff+'/'+zoff,
      success: function (data) {
        $().uxmessage('notice', "X,Y,Z zero'd.")
      }
    })
    return true
  })
  // offset X
  $("#offset_x_btn").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#offset_x_btn").click(function(e){
    var xoff = parseFloat($('#x_off_ro').val())
    if (isNaN(xoff)) {xoff=0}
    request_get({
      url:'/offsetx/'+xoff,
      success: function (data) {
        $().uxmessage('notice', "X zero'd.")
      }
    })
    return true
  })
  // offset Y
  $("#offset_y_btn").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#offset_y_btn").click(function(e){
    var yoff = parseFloat($('#y_off_ro').val())
    if (isNaN(yoff)) {yoff=0}
    request_get({
      url:'/offsety/'+yoff,
      success: function (data) {
        $().uxmessage('notice', "Y zero'd.")
      }
    })
    return true
  })
  // offset Z
  $("#offset_z_btn").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#offset_z_btn").click(function(e){
    var zoff = parseFloat($('#z_off_ro').val())
    if (isNaN(zoff)) {zoff=0}
    request_get({
      url:'/offsetz/'+zoff,
      success: function (data) {
        $().uxmessage('notice', "Z zero'd.")
      }
    })
    return true
  })



  // move X
  $("#move_x_btn").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#move_x_btn").click(function(e){
    var x = parseFloat($('#x_ro').val())
    if (isNaN(x)) {x=0}
    request_get({
      url:'/movex/'+x,
      success: function (data) {
        $().uxmessage('notice', "Moving X ...")
      }
    })
    return true
  })
  // move X
  $("#move_y_btn").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#move_y_btn").click(function(e){
    var y = parseFloat($('#y_ro').val())
    if (isNaN(y)) {y=0}
    request_get({
      url:'/movey/'+y,
      success: function (data) {
        $().uxmessage('notice', "Moving Y ...")
      }
    })
    return true
  })
  // move Z
  $("#move_z_btn").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#move_z_btn").click(function(e){
    var z = parseFloat($('#z_ro').val())
    if (isNaN(z)) {z=0}
    request_get({
      url:'/movez/'+z,
      success: function (data) {
        $().uxmessage('notice', "Moving Z ...")
      }
    })
    return true
  })



  // Jog X
  $("#jog_x_minus").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#jog_x_minus").click(function(e){
    var djog = parseFloat($('#jog_delta input:radio:checked').val())
    request_jog(-djog, 0, 0, "X-"+djog)
    return true
  })
  $("#jog_x_plus").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#jog_x_plus").click(function(e){
    var djog = parseFloat($('#jog_delta input:radio:checked').val())
    request_jog(djog, 0, 0, "X"+djog)
    return true
  })
  // Jog Y
  $("#jog_y_minus").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#jog_y_minus").click(function(e){
    var djog = parseFloat($('#jog_delta input:radio:checked').val())
    request_jog(0, -djog, 0, "Y-"+djog)
    return true
  })
  $("#jog_y_plus").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#jog_y_plus").click(function(e){
    var djog = parseFloat($('#jog_delta input:radio:checked').val())
    request_jog(0, djog, 0, "Y"+djog)
    return true
  })
  // Jog Z
  $("#jog_z_minus").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#jog_z_minus").click(function(e){
    var djog = parseFloat($('#jog_delta input:radio:checked').val())
    request_jog(0, 0, -djog, "Z-"+djog)
    return true
  })
  $("#jog_z_plus").tooltip({placement:'top', delay: {show:1000, hide:100}})
  $("#jog_z_plus").click(function(e){
    var djog = parseFloat($('#jog_delta input:radio:checked').val())
    request_jog(0, 0, djog, "Z"+djog)
    return true
  })




  // shortcut keys //////////////////////////////////////////////////////////


  Mousetrap.bind(['i'], function(e) {
    $('#info_btn').trigger('click')
    return false;
  })

  Mousetrap.bind(['e'], function(e) {
    $('#export_btn').trigger('click')
    return false;
  })

  Mousetrap.bind(['del', 'backspace'], function(e) {
    $('#clear_btn').trigger('click')
    return false;
  })

  Mousetrap.bind(['q'], function(e) {
    $('#queue_btn').trigger('click')
    return false;
  })

  Mousetrap.bind(['l'], function(e) {
    $('#library_btn').trigger('click')
    return false;
  })

  Mousetrap.bind(['c'], function(e) {
    $('#config_btn').trigger('click')
    return false;
  })

  Mousetrap.bind(['shift+l'], function(e) {
    $('#log_btn').trigger('click')
    return false;
  })

  Mousetrap.bind(['enter'], function(e) {
    control_visible_click($('#open_btn'), 'btn-info')
    return false;
  })

  Mousetrap.bind(['command+enter', 'ctrl+enter'], function(e) {
    control_visible_click($('#run_btn'), 'btn-info')
    return false;
  })

  Mousetrap.bind(['command+shift+enter', 'ctrl+shift+enter'], function(e) {
    control_visible_click($('#boundary_btn'), 'btn-info')
    return false;
  })

  Mousetrap.bind(['space'], function(e) {
    control_visible_click($('#pause_btn'), 'btn-info')
    return false;
  })

  Mousetrap.bind(['ctrl+esc', 'command+esc'], function(e) {
    control_visible_click($('#stop_btn'), 'btn-info')
    return false;
  })


  Mousetrap.bind(['s'], function(e) {
    $('#status_btn').trigger('click')
    return false;
  })

  Mousetrap.bind(['t'], function(e) {
    $('#tool_btn').trigger('click')
    return false;
  })

  Mousetrap.bind(['r'], function(e) {
    control_visible_click($('#origin_btn'), 'btn-info')
    return false;
  })

  Mousetrap.bind(['h'], function(e) {
    control_visible_click($('#homing_btn'), 'btn-info')
    return false;
  })

  Mousetrap.bind(['0'], function(e) {
    control_visible_click($('#offset_btn'), 'btn-info')
    return false;
  })
  Mousetrap.bind(['7'], function(e) {
    control_visible_click($('#offset_x_btn'), 'btn-info')
    return false;
  })
  Mousetrap.bind(['8'], function(e) {
    control_visible_click($('#offset_y_btn'), 'btn-info')
    return false;
  })
  Mousetrap.bind(['9'], function(e) {
    control_visible_click($('#offset_z_btn'), 'btn-info')
    return false;
  })

  // X
  Mousetrap.bind(['left'], function(e) {
    control_visible_click($('#jog_x_minus'), 'btn-info')
    return false;
  })
  Mousetrap.bind(['right'], function(e) {
    control_visible_click($('#jog_x_plus'), 'btn-info')
    return false;
  })
  // Y
  Mousetrap.bind(['up'], function(e) {
    control_visible_click($('#jog_y_plus'), 'btn-info')
    return false;
  })
  Mousetrap.bind(['down'], function(e) {
    control_visible_click($('#jog_y_minus'), 'btn-info')
    return false;
  })
  // Z
  Mousetrap.bind(['pageup'], function(e) {
    control_visible_click($('#jog_z_plus'), 'btn-info')
    return false;
  })
  Mousetrap.bind(['pagedown'], function(e) {
    control_visible_click($('#jog_z_minus'), 'btn-info')
    return false;
  })


  // jog distance
  Mousetrap.bind(['['], function(e) {
      $('#jog_delta input:radio:checked').parent().prev().children('input').trigger('click')
      return false;
  })
  Mousetrap.bind([']'], function(e) {
      $('#jog_delta input:radio:checked').parent().next().children('input').trigger('click')
      return false;
  })


  // debug
  Mousetrap.bind(['b'], function(e) {
    request_get({
      url:'/build',
      success: function (data) {
        status_cache.firmver = undefined
        $().uxmessage('success', "Building successful.")
      }
    })
    return false;
  })

  Mousetrap.bind(['f'], function(e) {
    request_get({
      url:'/flash',
      success: function (data) {
        status_cache.firmver = undefined
        $().uxmessage('success', "Flashing successful.")
      }
    })
    return false;
  })

}
