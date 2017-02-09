# -*- coding: utf-8 -*-

import sys
import os
import time
import glob
import json
import copy
import tempfile
import threading
import webbrowser
import wsgiref.simple_server
import bottle
import traceback
from config import conf, userconfigurable, write_config_fields, conf_defaults

import driveboard
import jobimport


__author__  = 'Stefan Hechenberger <stefan@nortd.com>'

DEBUG = False
bottle.BaseRequest.MEMFILE_MAX = 1024*1024*100 # max 100Mb files
time_status_last = 0


def checkuser(user, pw):
    """Check login credentials, used by auth_basic decorator."""
    return bool(user in conf['users'] and conf['users'][user] == pw)

def checkserial(func):
    """Decorator to call function only when machine connected."""
    def _decorator(*args, **kwargs):
            if driveboard.connected():
                return func(*args, **kwargs)
            else:
                bottle.abort(400, "No machine.")
    return _decorator




### STATIC FILES

@bottle.route('/')
def default_handler():
    return bottle.static_file('app.html', root=os.path.join(conf['rootdir'], 'frontend') )

@bottle.route('/<file>')
def static_bin_handler(file):
    return bottle.static_file(file, root=os.path.join(conf['rootdir'], 'frontend'))

@bottle.route('/css/<path:path>')
def static_css_handler(path):
    return bottle.static_file(path, root=os.path.join(conf['rootdir'], 'frontend', 'css'))

@bottle.route('/fonts/<path:path>')
def static_font_handler(path):
    return bottle.static_file(path, root=os.path.join(conf['rootdir'], 'frontend', 'fonts'))

@bottle.route('/js/<path:path>')
def static_js_handler(path):
    return bottle.static_file(path, root=os.path.join(conf['rootdir'], 'frontend', 'js'))

@bottle.route('/img/<path:path>')
def static_img_handler(path):
    return bottle.static_file(path, root=os.path.join(conf['rootdir'], 'frontend', 'img'))

@bottle.route('/favicon.ico')
def favicon_handler():
    return bottle.static_file('favicon.ico', root=os.path.join(conf['rootdir'], 'frontend', 'img'))


@bottle.route('/temp', method='POST')
@bottle.auth_basic(checkuser)
def temp():
    """Create temp file for downloading."""
    load_request = json.loads(bottle.request.forms.get('load_request'))
    job = load_request.get('job')  # always a string
    fp = tempfile.NamedTemporaryFile(mode='w', delete=False)
    filename = fp.name
    with fp:
        fp.write(job)
        fp.close()
    print job
    print "file stashed: " + os.path.basename(filename)
    # return os.path.basename(filename)
    return json.dumps(os.path.basename(filename))


@bottle.route('/download/<filename>/<dlname>')
@bottle.auth_basic(checkuser)
def download(filename, dlname):
    print "requesting: " + filename
    return bottle.static_file(filename, root=tempfile.gettempdir(), download=dlname)



### LOW-LEVEL

@bottle.route('/config')
@bottle.route('/config/<key>/<value:path>')
@bottle.auth_basic(checkuser)
def config(key=None, value=None):
    if not key or not value:
        confcopy = copy.deepcopy(conf)
        del confcopy['users']
        return json.dumps(confcopy)
    else:
        if key in userconfigurable:
            if value == "_default_":
                value = conf_defaults[key]
            else:
                try:
                    value = json.loads(value)
                except ValueError:
                    pass
            conf[key] = value
            write_config_fields({key:value})
            return "Written to config file."
        else:
            return "Not a user-configurable key."


@bottle.route('/confserial')
@bottle.route('/confserial/<port>')
@bottle.auth_basic(checkuser)
def confserial(port=None):
    """Write serial port to configuration file."""
    if port:
        conf['serial_port'] = port
        write_config_fields({'serial_port':port})
        return "Serial port written to config file."
    else:
        return conf['serial_port']



@bottle.route('/status')
@bottle.auth_basic(checkuser)
def status():
    global time_status_last
    if not driveboard.connected() and (time.time()-time_status_last) > 6.0:
        driveboard.connect_withfind(verbose=False)
    time_status_last = time.time()
    return json.dumps(driveboard.status())


@bottle.route('/homing')
@bottle.auth_basic(checkuser)
@checkserial
def homing():
    driveboard.homing()
    return '{}'

@bottle.route('/feedrate/<val:float>')
@bottle.auth_basic(checkuser)
@checkserial
def feedrate(val):
    driveboard.feedrate(val)
    return '{}'

@bottle.route('/intensity/<val:float>')
@bottle.auth_basic(checkuser)
@checkserial
def intensity(val):
    driveboard.intensity(val)
    return '{}'

@bottle.route('/relative')
@bottle.auth_basic(checkuser)
@checkserial
def relative():
    driveboard.relative()
    return '{}'

@bottle.route('/absolute')
@bottle.auth_basic(checkuser)
@checkserial
def absolute():
    driveboard.absolute()
    return '{}'

@bottle.route('/move/<x:float>/<y:float>/<z:float>')
@bottle.auth_basic(checkuser)
@checkserial
def move(x, y, z):
    driveboard.move(x, y, z)
    return '{}'

@bottle.route('/air_on')
@bottle.auth_basic(checkuser)
@checkserial
def air_on():
    driveboard.air_on()
    return '{}'

@bottle.route('/air_off')
@bottle.auth_basic(checkuser)
@checkserial
def air_off():
    driveboard.air_off()
    return '{}'

@bottle.route('/aux_on')
@bottle.auth_basic(checkuser)
@checkserial
def aux_on():
    driveboard.aux_on()
    return '{}'

@bottle.route('/aux_off')
@bottle.auth_basic(checkuser)
@checkserial
def aux_off():
    driveboard.aux_off()
    return '{}'

@bottle.route('/offset/<x:float>/<y:float>/<z:float>')
@bottle.auth_basic(checkuser)
@checkserial
def offset(x, y, z):
    if not driveboard.status()['ready']:
        bottle.abort(400, "Machine not ready.")
    driveboard.def_offset_custom(x, y, z)
    driveboard.sel_offset_custom()
    return '{}'

@bottle.route('/clear_offset')
@bottle.auth_basic(checkuser)
@checkserial
def clear_offset():
    if not driveboard.status()['ready']:
        bottle.abort(400, "Machine not ready.")
    driveboard.def_offset_custom(0,0,0)
    driveboard.sel_offset_table()
    return '{}'




### JOBS QUEUE

def _get_sorted(globpattern, library=False, stripext=False):
    files = []
    cwd_temp = os.getcwd()
    try:
        if library:
            os.chdir(os.path.join(conf['rootdir'], 'library'))
            files = filter(os.path.isfile, glob.glob(globpattern))
            files.sort()
        else:
            os.chdir(conf['stordir'])
            files = filter(os.path.isfile, glob.glob(globpattern))
            files.sort(key=lambda x: os.path.getmtime(x))
        if stripext:
            for i in range(len(files)):
                if files[i].endswith('.dba'):
                    files[i] = files[i][:-4]
                elif files[i].endswith('.dba.starred'):
                    files[i] = files[i][:-12]
    finally:
        os.chdir(cwd_temp)
    return files

def _get(jobname, library=False):
    # get job as sting
    if library:
        jobpath = os.path.join(conf['rootdir'], 'library', jobname.strip('/\\'))
    else:
        jobpath = os.path.join(conf['stordir'], jobname.strip('/\\'))
    if os.path.exists(jobpath+'.dba'):
        jobpath = jobpath+'.dba'
    elif os.path.exists(jobpath + '.dba.starred'):
        jobpath = jobpath + '.dba.starred'
    else:
        bottle.abort(400, "No such file.")
    with open(jobpath) as fp:
        job = fp.read()
    return job

def _get_path(jobname, library=False):
    if library:
        jobpath = os.path.join(conf['rootdir'], 'library', jobname.strip('/\\'))
    else:
        jobpath = os.path.join(conf['stordir'], jobname.strip('/\\'))
    if os.path.exists(jobpath+'.dba'):
        return jobpath+'.dba'
    elif os.path.exists(jobpath+'.dba.starred'):
        return jobpath+'.dba.starred'
    else:
        bottle.abort(400, "No such file.")

def _exists(jobname):
    namepath = os.path.join(conf['stordir'], jobname.strip('/\\'))
    if os.path.exists(namepath+'.dba') or os.path.exists(namepath+'.dba.starred'):
        bottle.abort(400, "File name exists.")

def _clear(limit=None):
    files = _get_sorted('*.dba')
    if type(limit) is not int and limit is not None:
        raise ValueError
    for filename in files:
        if type(limit) is int and limit <= 0:
            break
        filename = os.path.join(conf['stordir'], filename)
        os.remove(filename);
        print "file deleted: " + filename
        if type(limit) is int:
            limit -= 1

def _add(job, name):
    # add job (dba string)
    # overwrites file if already exists, use _unique_name(name) to avoid
    namepath = os.path.join(conf['stordir'], name.strip('/\\')+'.dba')
    with open(namepath, 'w') as fp:
        fp.write(job)
        print "file saved: " + namepath
    # delete excessive job files
    num_to_del = len(_get_sorted('*.dba')) - conf['max_jobs_in_list']
    _clear(num_to_del)

def _unique_name(jobname):
    files = _get_sorted('*.dba*', stripext=True)
    if jobname in files:
        for i in xrange(2,999):
            altname = "%s_%s" % (jobname, i)
            if altname in files:
                continue
            else:
                jobname = altname
                break
    return jobname



@bottle.route('/load', method='POST')
@bottle.auth_basic(checkuser)
def load():
    """Load a dba, svg, dxf, or gcode job.

    Args:
        (Args come in through the POST request.)
        job: Parsed dba or job string (dba, svg, dxf, or ngc).
        name: name of the job (string)
        optimize: flag whether to optimize (bool)
        overwrite: flag whether to overwite file if present (bool)
    """
    load_request = json.loads(bottle.request.forms.get('load_request'))
    job = load_request.get('job')  # always a string
    name = load_request.get('name')
    # optimize defaults
    if 'optimize' in load_request:
        optimize = load_request['optimize']
    else:
        optimize = True
    # overwrite defaults
    if 'overwrite' in load_request:
        overwrite = load_request['overwrite']
    else:
        overwrite = False
    # sanity check
    if job is None or name is None:
        bottle.abort(400, "Invalid request data.")
    # convert
    try:
        job = jobimport.convert(job, optimize=optimize)
    except TypeError:
        if DEBUG: traceback.print_exc()
        bottle.abort(400, "Invalid file type.")

    if not overwrite:
        name = _unique_name(name)
    _add(json.dumps(job), name)
    return json.dumps(name)



@bottle.route('/listing')
@bottle.route('/listing/<kind>')
@bottle.auth_basic(checkuser)
def listing(kind=None):
    """List all queue jobs by name."""
    if kind is None:
        files = _get_sorted('*.dba*', stripext=True)
    elif kind == 'starred':
        files = _get_sorted('*.dba.starred', stripext=True)
        print files
    elif kind == 'unstarred':
        files = _get_sorted('*.dba', stripext=True)
    else:
        bottle.abort(400, "Invalid kind.")
    return json.dumps(files)


@bottle.route('/get/<jobname>')
@bottle.auth_basic(checkuser)
def get(jobname='woot'):
    """Get a queue job in .dba format."""
    base, name = os.path.split(_get_path(jobname))
    return bottle.static_file(name, root=base, mimetype='application/json')


@bottle.route('/star/<jobname>')
@bottle.auth_basic(checkuser)
def star(jobname):
    """Star a job."""
    jobpath = _get_path(jobname)
    if jobpath.endswith('.dba'):
        os.rename(jobpath, jobpath + '.starred')
    else:
        bottle.abort(400, "No such file.")
    return '{}'


@bottle.route('/unstar/<jobname>')
@bottle.auth_basic(checkuser)
def unstar(jobname):
    """Unstar a job."""
    jobpath = _get_path(jobname)
    if jobpath.endswith('.starred'):
        os.rename(jobpath, jobpath[:-8])
    else:
        bottle.abort(400, "No such file.")
    return '{}'


@bottle.route('/remove/<jobname>')
@bottle.auth_basic(checkuser)
def remove(jobname):
    """Delete a job."""
    jobpath = _get_path(jobname)
    os.remove(jobpath)
    print "INFO: file deleted: " + jobpath
    return '{}'


@bottle.route('/clear')
@bottle.auth_basic(checkuser)
def clear():
    """Clear job list."""
    _clear()
    return '{}'



### LIBRARY

@bottle.route('/listing_library')
@bottle.auth_basic(checkuser)
def listing_library():
    """List all library jobs by name."""
    files = _get_sorted('*.dba', library=True, stripext=True)
    return json.dumps(files)


@bottle.route('/get_library/<jobname>')
@bottle.auth_basic(checkuser)
def get_library(jobname):
    """Get a library job in .dba format."""
    base, name = os.path.split(_get_path(jobname, library=True))
    return bottle.static_file(name, root=base, mimetype='application/json')


@bottle.route('/load_library/<jobname>')
@bottle.auth_basic(checkuser)
def load_library(jobname):
    """Load a library job into the queue."""
    job = _get(jobname, library=True)
    jobname = _unique_name(jobname)
    _add(job, jobname)
    return json.dumps(jobname)



### JOB EXECUTION

@bottle.route('/run/<jobname>')
@bottle.auth_basic(checkuser)
@checkserial
def run(jobname):
    """Send job from queue to the machine."""
    job = _get(jobname)
    if not driveboard.status()['ready']:
        bottle.abort(400, "Machine not ready.")
    driveboard.job(json.loads(job))
    return '{}'


@bottle.route('/run', method='POST')
@bottle.auth_basic(checkuser)
@checkserial
def run_direct():
    """Run an dba job directly, by-passing the queue.
    Args:
        (Args come in through the POST request.)
        job: Parsed dba job.
    """
    load_request = json.loads(bottle.request.forms.get('load_request'))
    job = load_request.get('job')  # always a string
    # sanity check
    if job is None:
        bottle.abort(400, "Invalid request data.")
    driveboard.job(json.loads(job))
    return '{}'


@bottle.route('/pause')
@bottle.auth_basic(checkuser)
@checkserial
def pause():
    """Pause a job gracefully."""
    driveboard.pause()
    return '{}'


@bottle.route('/unpause')
@bottle.auth_basic(checkuser)
@checkserial
def unpause():
    """Resume a paused job."""
    driveboard.unpause()
    return '{}'


@bottle.route('/stop')
@bottle.auth_basic(checkuser)
@checkserial
def stop_():
    """Halt machine immediately and purge job."""
    driveboard.stop()
    return '{}'


@bottle.route('/unstop')
@bottle.auth_basic(checkuser)
@checkserial
def unstop():
    """Recover machine from stop mode."""
    driveboard.unstop()
    return '{}'




### MCU MANAGMENT

@bottle.route('/build')
# @bottle.route('/build/<firmware>')
@bottle.auth_basic(checkuser)
def build(firmware_name=None):
    """Build firmware from firmware/src files."""
    buildname = "DriveboardFirmware_from_src"
    return_code = driveboard.build(firmware_name=buildname)
    if return_code != 0:
        bottle.abort(400, "Build failed.")
    else:
        return '{"flash_url": "/flash/%s.hex"}' % (buildname)


@bottle.route('/flash')
@bottle.route('/flash/<firmware>')
@bottle.auth_basic(checkuser)
def flash(firmware=None):
    """Flash firmware to MCU."""
    if firmware is None:
        return_code = driveboard.flash()
    else:
        return_code = driveboard.flash(firmware_file=firmware)
    if return_code != 0:
        bottle.abort(400, "Flashing failed.")
    else:
        return '{}'


@bottle.route('/reset')
@bottle.auth_basic(checkuser)
def reset():
    """Reset MCU"""
    try:
        driveboard.reset()
    except IOError:
        bottle.abort(400, "Reset failed.")
    return '{}'


@bottle.route('/hello/<name>')
def hello(name):
    return bottle.template('<b>Hello {{name}}</b>!', name=name)

###############################################################################
###############################################################################


class Server(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.server = None
        self.lock = threading.Lock()
        self.stop_server = False

    def run(self):
        while 1:
            try:
                with self.lock:
                    if self.stop_server:
                        break
                self.server.handle_request()
            except KeyboardInterrupt:
                break
        print "\nServer shutting down..."
        driveboard.close()

    def stop(self):
        with self.lock:
            self.stop_server = True
        self.join()

S = Server()


def start(browser=False, debug=False):
    """ Start a bottle web server.
        Derived from WSGIRefServer.run()
        to have control over the main loop.
    """
    global DEBUG
    DEBUG = debug

    class FixedHandler(wsgiref.simple_server.WSGIRequestHandler):
        def address_string(self): # Prevent reverse DNS lookups please.
            return self.client_address[0]
        def log_request(*args, **kw):
            if debug:
                return wsgiref.simple_server.WSGIRequestHandler.log_request(*args, **kw)

    S.server = wsgiref.simple_server.make_server(
        conf['network_host'],
        conf['network_port'],
        bottle.default_app(),
        wsgiref.simple_server.WSGIServer,
        FixedHandler
    )
    S.server.timeout = 0.01
    S.server.quiet = not debug
    if debug:
        bottle.debug(True)
    print "Internal storage root is: " + conf['rootdir']
    print "Persistent storage root is: " + conf['stordir']
    print "-----------------------------------------------------------------------------"
    print "Starting server at http://%s:%d/" % ('127.0.0.1', conf['network_port'])
    print "-----------------------------------------------------------------------------"
    driveboard.connect_withfind()
    # open web-browser
    if browser:
        try:
            webbrowser.open_new_tab('http://127.0.0.1:'+str(conf['network_port']))
        except webbrowser.Error:
            print "Cannot open Webbrowser, please do so manually."
    sys.stdout.flush()  # make sure everything gets flushed
    # start server
    print "INFO: Starting web server thread."
    S.start()



def stop():
    global S
    S.stop()
    # recreate server to unbind
    # and allow restarting
    del S
    S = Server()



if __name__ == "__main__":
    start()
    while 1:  # wait until keyboard interrupt
        try:
            time.sleep(0.1)
        except KeyboardInterrupt:
            break
    stop()
    print "END of DriveboardApp"
