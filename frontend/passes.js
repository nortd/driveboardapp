

function passes_clear() {
  $('#job_passes').html("")
}

function passes_add(feedrate, intensity, pxsize, items_assigned) {
  // multiple = typeof multiple !== 'undefined' ? multiple : 1  // default to 1
  var num_passes_already = $('#job_passes').children('.pass_widget').length
  var num = num_passes_already + 1
  var html = passes_pass_html(num, feedrate, intensity, pxsize)
  if ($('#pass_add_widget').length) {
    var pass_elem = $(html).insertBefore('#pass_add_widget')
  } else {
    var pass_elem = $(html).appendTo('#job_passes')
  }
  // unblur buttons after pressing
  $("#pass_"+num+" .btn").mouseup(function(){
      $(this).blur();
  })

  // assign colors
  for (var i = 0; i < items_assigned.length; i++) {
    var idx = items_assigned[i]
    $('#passsel_'+num+'_'+idx).hide()
    $('#pass_'+num+'_'+idx).show(300)
    passes_update_handler()
  }

  // assign image thumbs
  jobhandler.loopItems(function(image, idx){
    var img1 = jobhandler.getImageThumb(image, -100, 50)
    $(img1).appendTo('#passsel_'+num+'_'+idx+' a')
    var img2 = jobhandler.getImageThumb(image, -100, 50)
    $(img2).appendTo('#pass_'+num+'_'+idx+' .color_select_btn_'+num)
  }, "image")

  // bind color assign button
  $('#assign_btn_'+num).click(function(e) {
    if (jobview_item_selected !== undefined) {
      var idx = jobview_item_selected
      $('#passsel_'+num+'_'+idx).hide()
      $('#pass_'+num+'_'+idx).hide()
      $('#pass_'+num+'_'+idx).show(300)
      passes_update_handler()
      return false
    } else {
      return true
    }
  })

  // bind all color add buttons within dropdown
  $('.color_add_btn_'+num).click(function(e) {
    var idx = $(this).children('span.idxmem').text()
    $('#passsel_'+num+'_'+idx).hide()
    $('#pass_'+num+'_'+idx).show(300)
    $('#passdp_'+num).dropdown("toggle")
    passes_update_handler()
    return false
  })

  // bind all color remove buttons
  $('.color_remove_btn_'+num).click(function(e) {
    var idx = $(this).parent().find('span.idxmem').text()
    $('#passsel_'+num+'_'+idx).show(0)
    $('#pass_'+num+'_'+idx).hide(300)
    passes_update_handler()
    return false
  })

  // bind all color select buttons
  $('.color_select_btn_'+num).click(function(e) {
    var idx = $(this).parent().find('span.idxmem').text()
    jobhandler.selectItem(idx)
    return false
  })

  // hotkey
  // $('#assign_btn_'+num).tooltip({placement:'bottom', delay: {show:1000, hide:100}})
  Mousetrap.bind([num.toString()], function(e) {
      $('#assign_btn_'+num).trigger('click')
      return false;
  })
}



function passes_pass_html(num, feedrate, intensity, pxsize) {
  // add all color selectors
  var select_html = ''
  var added_html = ''

  jobhandler.loopItems(function(image, idx){
    var color = '#ffffff'
    select_html += passes_select_html(num, idx, "image", color)
    added_html += passes_added_html(num, idx, "image", color)
  }, "image")

  jobhandler.loopItems(function(fill, idx){
    select_html += passes_select_html(num, idx, "fill", fill.color)
    added_html += passes_added_html(num, idx, "fill", fill.color)
  }, "fill")

  jobhandler.loopItems(function(path, idx){
    select_html += passes_select_html(num, idx, "path", path.color)
    added_html += passes_added_html(num, idx, "path", path.color)
  }, "path")

  // html template like it's 1999
  var html =
  '<div id="pass_'+num+'" class="row pass_widget" style="margin:0; margin-bottom:20px">'+
    '<label style="color:#666666">Pass '+num+'</label>'+

    '<a id="pass_conf_btn_'+num+'" style="margin-left:8px; position:relative; top:1px" role="button"'+
      'data-toggle="collapse" href="#pass_conf_'+num+'" aria-expanded="false" aria-controls="pass_conf_'+num+'"'+
      '<span class="glyphicon glyphicon-cog" style="color:#888888"></span>'+
    '</a>'+
    '<div class="collapse" id="pass_conf_'+num+'"><div class="well" style="margin-bottom:10px">'+
      '<div class="input-group" style="margin-right:4px">'+
        '<div class="input-group-addon">pxsize</div>'+
        '<input type="text" class="form-control input-sm pxsize"'+
          'style="width:44px;" value="'+pxsize+'" title="size of physical raster pixel in mm">'+
      '</div>'+
    '</div></div>'+
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

function passes_select_html(num, idx, kind, color) {
  var html =
  '<li id="passsel_'+num+'_'+idx+'" style="background-color:'+color+'">'+
  '<a href="#" class="color_add_btn_'+num+'" style="color:'+color+'">'+
  '<span class="label label-default kindmem">'+kind+'</span>'+
  '<span class="idxmem" style="display:none">'+idx+'</span></a></li>'
  return html
}

function passes_added_html(num, idx, kind, color) {
  var html =
  '<div id="pass_'+num+'_'+idx+'" class="btn-group pull-left" style="margin-top:0.5em; display:none">'+
    '<span style="display:none" class="idxmem">'+idx+'</span>'+
    '<button class="btn btn-default btn-sm color_select_btn_'+num+'" '+
      'type="submit" style="width:175px; background-color:'+color+'">'+
      '<span class="label label-default kindmem">'+kind+'</span>'+
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
    passes_add(1500, 100, app_config_main.pxsize, [])
    return false
  })

  // hotkey
  Mousetrap.bind(['p'], function(e) {
      $('#pass_add_btn').trigger('click')
      return false;
  })
}


function passes_get_active() {
  var passes = []
  $('#job_passes').children('.pass_widget').each(function(i) { // each pass
    var feedrate = Math.round(parseFloat($(this).find("input.feedrate").val()))
    var intensity = Math.round(parseFloat($(this).find("input.intensity").val()))
    var pxsize = parseFloat($(this).find("input.pxsize").val())
    var pass = {"items":[]}
    if (typeof(feedrate) === 'number' && !isNaN(feedrate)) { pass.feedrate = feedrate }
    if (typeof(intensity) === 'number' && !isNaN(intensity)) { pass.intensity = intensity }
    if (typeof(pxsize) === 'number' && !isNaN(pxsize)) { pass.pxsize = pxsize }
    $(this).children('div.pass_colors').children('div').filter(':visible').each(function(k) {
      var idx = parseFloat($(this).find('.idxmem').text())
      pass.items.push(idx)
    })
    if (pass.items.length) {
      passes.push(pass)
    }
  })
  return passes
}


function passes_set_assignments() {
  // set passes in gui from current job
  if (jobhandler.hasPasses()) {
    jobhandler.loopPasses(function(pass, items){
      passes_add(pass.feedrate, pass.intensity, pass.pxsize, items)
    })
  } else {
    passes_add(1500, 100, app_config_main.pxsize, [])
    passes_add(1500, 100, app_config_main.pxsize, [])
    passes_add(1500, 100, app_config_main.pxsize, [])
  }
  passes_add_widget()
}


function passes_update_handler() {
  // called whenever passes wiget changes happen (color add/remove)
  // this event handler is debounced to minimize updates
  clearTimeout(window.lastPassesUpdateTimer)
  window.lastPassesUpdateTimer = setTimeout(function() {
    jobhandler.passes = passes_get_active()
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
