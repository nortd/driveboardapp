


gcodehandler = {

  gcode_lines : [],

  gcode_from_job : function(job) {

    if ('raster' in job) {

    }

    if ('vector' in job) {
      if ('paths' in job.vector) {
        for (var i = 0; i < job.vector.paths.length; i++) {
          var path = job.vector.paths[i]
        }

      }
    }


  },


  gcode_to_job : function(gcode) {

  }
}
