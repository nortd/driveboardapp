


function request_get(args) {
  // args items: url, success, error, complete
  $.ajax({
    type: "GET",
    url: args.url,
    dataType: "json",
    username: "laser",
    password: "laser",
    statusCode: {
      400: function(s) {
        // alert(JSON.stringify(s))
        if ('responseText' in s) {
          r = s.responseText;
          var error_txt = r.slice(r.indexOf('<pre>')+5,r.lastIndexOf('</pre>'))
          $().uxmessage('error', error_txt)
        }
      },
      401: function() {
        $().uxmessage('error', "Wrong password/username.")
      }
    },
    success: function (data) {
      if ('success' in args) {
        args.success(data)
      }
    },
    error: function (data) {
      if ('error' in args) {
        args.error(data)
      }
    },
    complete: function (data) {
      if ('complete' in args) {
        args.complete(data)
      }
    }
  })
}



function request_post(args) {
  // args items: url, data, success, error, complete

  var formData = new FormData();
  if(args.url == '/load' && app_config_main.enable_gzip) {
    job = new File([pako.gzip(args.data.job)], 'upload.gz');
    formData.append('job', job);
    args.data.job = 'upload'
  }

  formData.append('load_request', JSON.stringify(args.data))

  $.ajax({
    type: "POST",
    url: args.url,
    data: formData,
    dataType: "json",
    contentType: false,
    processData: false,
    cache: false,
    username: "laser",
    password: "laser",
    statusCode: {
      400: function(s) {
        // alert(JSON.stringify(s))
        if ('responseText' in s) {
          r = s.responseText;
          var error_txt = r.slice(r.indexOf('<pre>')+5,r.lastIndexOf('</pre>'))
          $().uxmessage('error', error_txt)
        }
      },
      401: function() {
        $().uxmessage('error', "Wrong password/username.")
      }
    },
    success: function (data) {
      if ('success' in args) {
        args.success(data)
      }
    },
    error: function (data) {
      // $().uxmessage('error', args.url)
      if ('error' in args) {
        args.error(data)
      }
    },
    complete: function (data) {
      if ('complete' in args) {
        args.complete(data)
      }
    }
  })
}


function request_boundary(bounds, seekrate) {
  var job = {
    "passes":[
      {
        "items":[0],
        "seekrate":seekrate,
        "feedrate":seekrate,
        "air_assist":"off"
      }
    ],
    "items":[{"def":0}],
    "defs":[
        {"kind":"path", "data":[[
        [bounds[0],bounds[1],0],
        [bounds[2],bounds[1],0],
        [bounds[2],bounds[3],0],
        [bounds[0],bounds[3],0],
        [bounds[0],bounds[1],0] ]]}
      ],
  }
  request_post({
    url:'/run',
    data: {'job':request_stringify(job)},
    success: function (data) {
      $().uxmessage('notice', "Running boundary.")
    }
  })
}


function request_relative_move(x, y, z, seekrate, success_msg) {
  var job = {
    "head":{"noreturn":true},
    "passes":[
      {
        "items":[0],
        "relative":true,
        "seekrate":seekrate,
        "air_assist":"off"
      }
    ],
    "items":[{"def":0}],
    "defs":[{"kind":"path", "data":[[[x,y,z]]] }],
  }
  request_post({
    url:'/run',
    data: {'job':request_stringify(job)},
    success: function (data) {
      $().uxmessage('notice', success_msg)
    }
  })
}


function request_absolute_move(x, y, z, seekrate, success_msg) {
  var job = {
    "head":{"noreturn":true},
    "passes":[
      {
        "items":[0],
        "seekrate":seekrate,
        "air_assist":"off"
      }
    ],
    "items":[{"def":0}],
    "defs":[{"kind":"path", "data":[[[x,y,z]]] }]
  }
  request_post({
    url:'/run',
    data: {'job':request_stringify(job)},
    success: function (data) {
      $().uxmessage('notice', success_msg)
    }
  })
}



function request_path_job(path, seekrate, feedrate, air_assist, success_msg) {
  // Args:
  //     path: [[[0,-10, 0],],]
  //         list of polylines, list of points, list of coordinates
  //     seekrate:
  //     feedrate:
  //     air_assist: one of "feed", "pass", "off"
  var job = {
    "passes":[
      {
        "items":[0],
        "seekrate":seekrate,
        "feedrate":feedrate,
        "air_assist":air_assist
      }
    ],
    "items":[{"def":0}],
    "defs":[{"kind":"path", "data":path}]
  }
  // json stringify while limiting numbers to 3 decimals
  var json_job = JSON.stringify(job,
    function(key, val) {
      return val.toFixed ? Number(val.toFixed(3)) : val
    })
  request_post({
    url:'/run',
    data: {'job':json_job},
    success: function (data) {
      $().uxmessage('notice', success_msg)
    }
  })
}


function request_stringify(data) {
  // json stringify while limiting numbers to 3 decimals
  return JSON.stringify(data ,function(key, val) {
      return val.toFixed ? Number(val.toFixed(3)) : val
    })
}
