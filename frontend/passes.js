

function passes_clear() {
  $('#job_passes').html("")
}

function passes_add(feedrate, intensity, colors_assigned, images_assigned) {
  // multiple = typeof multiple !== 'undefined' ? multiple : 1  // default to 1
  // var image =  jobhandler.raster.images[images_assigned[0]].data
  var num_passes_already = $('#job_passes').children('.pass_widget').length
  var num = num_passes_already + 1
  var html = passes_pass_html(num, feedrate, intensity)
  if ($('#pass_add_widget').length) {
    var pass_elem = $(html).insertBefore('#pass_add_widget')
  } else {
    var pass_elem = $(html).appendTo('#job_passes')
  }
  // unblur buttons after pressing
  $("#pass_add_widget > .btn").mouseup(function(){
      $(this).blur();
  })

  // assign colors
  for (var i = 0; i < colors_assigned.length; i++) {
    var col_sliced = colors_assigned[i].slice(1)
    $('#passsel_'+num+'_'+col_sliced).hide()
    $('#pass_'+num+'_'+col_sliced).show(300)
    passes_update_handler()
  }

  // bind color assign button
  $('#assign_btn_'+num).click(function(e) {
    if (jobview_color_selected !== undefined) {
      var col_sliced = jobview_color_selected.slice(1)
      $('#passsel_'+num+'_'+col_sliced).hide()
      $('#pass_'+num+'_'+col_sliced).hide()
      $('#pass_'+num+'_'+col_sliced).show(300)
      passes_update_handler()
      return false
    } else {
      return true
    }
  })

  // bind all color add buttons within dropdown
  $('.color_add_btn_'+num).click(function(e) {
    var color = $(this).children('span.colmem').text()
    $('#passsel_'+num+'_'+color.slice(1)).hide()
    $('#pass_'+num+'_'+color.slice(1)).show(300)
    $('#passdp_'+num).dropdown("toggle")
    passes_update_handler()
    return false
  })

  // bind all color remove buttons
  $('.color_remove_btn_'+num).click(function(e) {
    var color = $(this).parent().find('span.colmem').text()
    $('#passsel_'+num+'_'+color.slice(1)).show(0)
    $('#pass_'+num+'_'+color.slice(1)).hide(300)
    passes_update_handler()
    return false
  })

  // bind all color select buttons
  $('.color_select_btn_'+num).click(function(e) {
    var color = $(this).parent().find('span.colmem').text()
    jobhandler.selectColor(color)
    return false
  })

  // hotkey
  // $('#assign_btn_'+num).tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  Mousetrap.bind([num.toString()], function(e) {
      $('#assign_btn_'+num).trigger('click')
      return false;
  })
}



function passes_pass_html(num, feedrate, intensity) {
  // add all color selectors
  var select_html = ''
  var colors_html = ''
  var allcolors = jobhandler.getAllColors()
  for (var i = 0; i < allcolors.length; i++) {
    var color = allcolors[i]
    var is_fill = jobhandler.isColorFill(color)
    if (is_fill) {
      var tag = '<span class="label label-default">fill</span>'
    } else {
      var tag = '<span class="label label-default">path</span>'
    }
    // add color selectors, will be hidden and shown accordingly
    select_html += passes_select_html(num, color, tag)
    // add colors added, will be hidden and shown accordingly
    added_html += passes_added_html(num, color, tag)
  }
  // html template like it's 1999
  var html =
  '<div id="pass_'+num+'" class="row pass_widget" style="margin:0; margin-bottom:20px">'+
    '<label style="color:#666666">Pass '+num+'</label>'+
    '<form class="form-inline">'+
      '<div class="form-group">'+
        '<div class="input-group" style="margin-right:4px">'+
          '<div class="input-group-addon" style="width:10px">F</div>'+
          '<input type="text" class="form-control input-sm feedrate" style="width:50px;" value="'+feedrate+'" title="feedrate">'+
        '</div>'+
        '<div class="input-group" style="margin-right:4px">'+
          '<div class="input-group-addon" style="width:10px">%</div>'+
          '<input type="text" class="form-control input-sm intensity" style="width:44px" value="'+intensity+'" title="intensity 0-100%">'+
        '</div>'+
        '<div class="dropdown input-group">'+
          '<button class="btn btn-primary btn-sm dropdown-toggle" type="button" style="width:34px" '+
            'id="assign_btn_'+num+'" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true" title="['+num+']">'+
            '<span class="glyphicon glyphicon-plus"></span>'+
          '</button>'+
          '<ul id="passdp_'+num+'" class="dropdown-menu dropdown-menu-right pass_color_dropdown" aria-labelledby="assign_btn_'+num+'">'+
            select_html+
          '</ul>'+
        '</div>'+
      '</div>'+
    '</form>'+
    '<div class="pass_colors">'+added_html+'</div>'+
  '</div>'
  return html
}

function passes_select_html(num, color, tag) {
  var html =
  '<li id="passsel_'+num+'_'+color.slice(1)+'" style="background-color:'+color+'">'+
  '<a href="#" class="color_add_btn_'+num+'" style="color:'+color+'">'+
  tag + '<span class="colmem" style="display:none">'+color+'</span></a></li>'
  return html
}

function passes_added_html(num, color, tag) {
  var html =
  '<div id="pass_'+num+'_'+color.slice(1)+'" class="btn-group pull-left" style="margin-top:0.5em; display:none">'+
    '<span style="display:none" class="colmem">'+color+'</span>'+
    '<button id="color_btn" class="btn btn-default btn-sm color_select_btn_'+num+'" '+
      'type="submit" style="width:175px; background-color:'+color+'">'+
      tag +
    '</button>'+
    '<button class="btn btn-default btn-sm color_remove_btn_'+num+'" type="submit" style="width:34px">'+
      '<span class="glyphicon glyphicon-remove"></span>'+
    '</button>'+
  '</div>'
  return html
}



function passes_add_widget() {
  var html =
  '<div id="pass_add_widget" class="row" style="margin:0; margin-bottom:20px">'+
    '<label style="color:#666666">More Passes</label>'+
    '<div>'+
      '<button class="btn btn-default btn-sm dropdown-toggle" type="button" style="width:34px" '+
        'id="pass_add_btn" data-toggle="dropdown" aria-haspopup="true" aria-expanded="true" title="[P]">'+
        '<span class="glyphicon glyphicon-plus"></span>'+
      '</button>'+
    '</div>'+
  '</div>'
  var pass_elem = $(html).appendTo('#job_passes')

  // bind pass_add_btn
  $('#pass_add_btn').click(function(e) {
    passes_add(1500, 100, [], [])
    return false
  })

  // hotkey
  Mousetrap.bind(['p'], function(e) {
      $('#pass_add_btn').trigger('click')
      return false;
  })
}


function passes_get_assignments() {
  var assignments = []
  $('#job_passes').children('.pass_widget').each(function(i) { // each pass
    var feedrate = Math.round(parseFloat($(this).find("input.feedrate").val()))
    var intensity = Math.round(parseFloat($(this).find("input.intensity").val()))
    assignments.push({"colors":[], "feedrate":feedrate, "intensity":intensity})
    $(this).children('div.pass_colors').children('div').filter(':visible').each(function(k) {
      var color = $(this).find('.colmem').text()
      assignments[i].colors.push(color)
      // console.log('assign '+color+' -> '+(i+1))
    })
  })
  return assignments
}


function passes_set_assignments() {
  // set passes in gui from current job
  var any_passes_set = false
  // raster passes in job
  if ('passes' in jobhandler.raster && jobhandler.raster.passes.length ) {
    var raster_passes = jobhandler.raster.passes
    for (var i = 0; i < raster_passes.length; i++) {
      var pass = raster_passes[i]
      var images_assigned = []
      for (var ii = 0; ii < pass.images.length; ii++) {
        var imgidx = pass.images[ii]
        images_assigned.push(imgidx)
        any_passes_set = true
      }
      passes_add(pass.feedrate, pass.intensity, [], images_assigned)
    }
  }
  // vector passes in job
  if ('passes' in jobhandler.vector && jobhandler.vector.passes.length &&
      'colors' in jobhandler.vector && jobhandler.vector.colors.length ) {
    var vector_passes = jobhandler.vector.passes
    var colors = jobhandler.vector.colors
    for (var i = 0; i < vector_passes.length; i++) {
      var pass = vector_passes[i]
      // convert path index to color
      var colors_assigned = []
      for (var ii = 0; ii < pass.paths.length; ii++) {
        var pathidx = pass.paths[ii]
        colors_assigned.push(colors[pathidx])
        any_passes_set = true
      }
      passes_add(pass.feedrate, pass.intensity, colors_assigned, [])
    }
  }
  // empty pass widets
  if (!(any_passes_set)) {
    passes_add(1500, 100, [], [])
    passes_add(1500, 100, [], [])
    passes_add(1500, 100, [], [])
  }
  // add another pass widget
  passes_add_widget()
}


function passes_update_handler() {
  // called whenever passes wiget changes happen (color add/remove)
  // this event handler is debounced to minimize updates
  clearTimeout(window.lastPassesUpdateTimer)
  window.lastPassesUpdateTimer = setTimeout(function() {
    jobhandler.setPassesFromGUI()
    // length
    var length = (jobhandler.getActivePassesLength()/1000.0).toFixed(1)
    if (length != 0) {
      $('#job_info_length').html(' | '+length+'m')
    } else {
      $('#job_info_length').html('')
    }
    // bounds
    jobhandler.renderBounds()
    jobhandler.draw()
  }, 2000)
}
