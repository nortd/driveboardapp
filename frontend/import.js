
var import_name = ""


///////////////////////////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////


$(document).ready(function(){
  // file upload form
  $('#open_file_fld').change(function(e){
    e.preventDefault()
    $('#open_btn').button('loading')
    var input = $('#open_file_fld').get(0)

    // file API check
    var browser_supports_file_api = true
    if (typeof window.FileReader !== 'function') {
      browser_supports_file_api = false
    } else if (!input.files) {
      browser_supports_file_api = false
    }

    // setup onload handler
    if (browser_supports_file_api) {
      if (input.files[0]) {
        var fr = new FileReader()
        fr.onload = sendToBackend
        fr.readAsText(input.files[0])
      } else {
        $().uxmessage('error', "No file was selected.")
      }
    } else {  // fallback
      $().uxmessage('error', "Requires browser with File API support.")
    }

    // reset file input form field so change event also triggers again
    var file_fld = $('#open_file_fld').val()
    file_fld = file_fld.slice(file_fld.lastIndexOf('\\')+1) || file_fld  // drop unix path
    file_fld = file_fld.slice(file_fld.lastIndexOf('/')+1) || file_fld   // drop windows path
    import_name = file_fld.slice(0, file_fld.lastIndexOf('.')) || file_fld  // drop extension
    $('#open_file_fld').val('')
  })



  function sendToBackend(e) {
    var job = e.target.result

    // notify parsing started
    $().uxmessage('notice', "parsing "+import_name+" ...")
    // large file note
    if (job.length > 102400) {
      $().uxmessage('notice', "Big file! May take a few minutes.")
    }

    // send to backend
    var load_request = {'job':job, 'name':import_name, 'optimize':true}
    request_post({
      url:'/load',
      data: load_request,
      success: function (jobname) {
        $().uxmessage('notice', "Parsed "+jobname+".")
        queue_update()
        import_open(jobname)
      },
      error: function (data) {
        $().uxmessage('error', "/load error.")
        $().uxmessage('error', JSON.stringify(data), false)
      },
      complete: function (data) {
        $('#open_btn').button('reset')
      }
    })

  }

})  // ready



function import_open(jobname, from_library) {
  from_library = typeof from_library !== 'undefined' ? from_library : false  // default to false
  // get job in dba format
  var url = '/get/'+jobname
  if (from_library === true) {
    url = '/get_library/'+jobname
  }
  request_get({
    url: url,
    success: function (job) {
      // alert(JSON.stringify(data))
      // $().uxmessage('notice', data)

      function jobhandler_done() {
        tools_addfill_init()
        jobhandler.render()
        jobhandler.draw()
      }
      
      jobhandler.set(job, jobname, true, jobhandler_done)

      // debug, show image, stats
      // if ('defs' in job) {
      //   for (var i=0; i<job.defs.length; i++) {
      //     var rasterdef = job.defs[i];
      //     if (rasterdef.kind == "image") {
      //       $('#log_content').prepend('<img src="'+rasterdef.data.src+'">')
      //       if ('data' in rasterdef) {
      //         $().uxmessage('notice'," data: " + rasterdef.data)
      //       } else {
      //         $().uxmessage('notice', "no raster data")
      //       }
      //     }
      //   }
      // }
    },
    error: function (data) {
      $().uxmessage('error', "/get error.")
      $().uxmessage('error', JSON.stringify(data), false)
    }
  })
}
