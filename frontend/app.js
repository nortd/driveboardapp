
var app_config_main = undefined
var app_run_btn = undefined
var app_fill_btn = undefined
var app_visibility = true


// toast messages, install jquery plugin
;(function($){
  $.fn.uxmessage = function(kind, text, max_length) {
    if (max_length == undefined) {
        max_length = 100
    }

    if (max_length !== false && text.length > max_length) {
      text = text.slice(0,max_length) + '\n...'
    }

    text = text.replace(/\n/g,'<br>')

    if (kind == 'notice') {
      $('#log_content').prepend('<div class="log_item log_notice well" style="display:none">' + text + '</div>')
      $('#log_content').children('div').first().show('blind')
      if ($("#log_content").is(':hidden')) {
        $().toastmessage('showToast',
          {text: text, sticky: false, position: 'top-center', type: 'notice'}
        )
      }
    } else if (kind == 'success') {
      $('#log_content').prepend('<div class="log_item log_success well" style="display:none">' + text + '</div>')
      $('#log_content').children('div').first().show('blind')
      if ($("#log_content").is(':hidden')) {
        $().toastmessage('showToast',
          {text: text, sticky: false, position: 'top-center', type: 'success'}
        )
      }
    } else if (kind == 'warning') {
      $('#log_content').prepend('<div class="log_item log_warning well" style="display:none">' + text + '</div>')
      $('#log_content').children('div').first().show('blind')
      if ($("#log_content").is(':hidden')) {
        $().toastmessage('showToast',
          {text: text, sticky: false, position: 'top-center', type: 'warning'}
        )
      }
    } else if (kind == 'error') {
      $('#log_content').prepend('<div class="log_item log_error well" style="display:none">' + text + '</div>')
      $('#log_content').children('div').first().show('blind');
      if ($("#log_content").is(':hidden')) {
        $().toastmessage('showToast',
          {text: text, sticky: false, position: 'top-center', type: 'error'}
        )
      }
    }

    while ($('#log_content').children('div').length > 200) {
      $('#log_content').children('div').last().remove()
    }

  };
})(jQuery)


///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

$(document).ready(function(){
  // $().uxmessage('notice', "Frontend started.")
  // modern browser check
  if(!Object.hasOwnProperty('keys')) {
    alert("Error: Browser may be too old/non-standard.")
  }

  // unblur button after pressing
  $(".btn").mouseup(function(){
      // $(this).blur()
      this.blur()
  })

  // run_btn, make a ladda progress spinner button
  // http://msurguy.github.io/ladda-bootstrap/
  app_run_btn = Ladda.create($("#run_btn")[0])
  app_fill_btn = Ladda.create($("#addfill_btn")[0])

  // page visibility events
  window.onfocus = function() {
    app_visibility = true
    status_set_refresh()
    // console.log("onfocus")
  }
  window.onblur = function() {
    app_visibility = false
    status_set_refresh()
    // console.log("onblur")
  }

  // connecting modal
  $('#connect_modal').modal({
    show: true,
    keyboard: false,
    backdrop: 'static'
  })

  // get appconfig from server
  request_get({
    url:'/config',
    success: function (data) {
      // $().uxmessage('success', "App config received.")
      app_config_main = data
      config_received()
    },
    error: function (data) {
      $().uxmessage('error', "Failed to receive app config.")
    },
    complete: function (data) {}
  })
});



function config_received() {
  // show in config modal
  var html = ''
  var keys_sorted = Object.keys(app_config_main).sort()
  for (var i=0; i<keys_sorted.length; i++) {
    html += keys_sorted[i] + " : " + app_config_main[keys_sorted[i]] + "<br>"
  }
  $('#config_content').html(html)
  // about modal
  $('#app_version').html(app_config_main.version)
  // $('#firmware_version').html(app_config_main.)

  // call 'ready' of jobview
  jobview_ready()
  // call 'ready' of controls
  controls_ready()
  // call 'ready' of queue
  queue_ready()
  // call 'ready' of library
  library_ready()
  // call 'ready' of status
  status_ready()
}
