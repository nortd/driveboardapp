#!/usr/bin/python
"""
- read output from a subprocess in a background thread
- show the output in the GUI
- stop subprocess using a Tkinter button
"""
from __future__ import print_function
from collections import deque
from itertools import islice
import subprocess
from threading import Thread
import webbrowser

try:
    import Tkinter as tk
except ImportError:
    import tkinter as tk # Python 3

try:
    from Queue import Queue, Empty
except ImportError:
    from queue import Queue, Empty # Python 3


def iter_except(function, exception):
    """Works like builtin iter(), but stops on exception."""
    try:
        while True:
            yield function()
    except exception:
        return

class SubprocessInGUI:
    def __init__(self, root):
        self.root = root
        self.root.bind("<Control-q>", lambda event: self.stop())
        self.proc = subprocess.Popen(['/usr/bin/python', 'backend/app.py'],
                                     stdout=subprocess.PIPE,
                                     stderr=subprocess.STDOUT)
        # launch thread to read the subprocess output
        q = Queue()
        t = Thread(target=self.reader_thread, args=[q]).start()

        # text widget
        self.text = tk.Text(root)
        self.text.pack()
        # add copy to clipboard feature
        def copy(event):
            selected = self.text.get("sel.first", "sel.last")
            if selected:
                self.root.clipboard_clear()
                self.root.clipboard_append(selected)
        self.text.bind("<Control-c>", copy)
        # start update loop
        self.update(q)

        # open frontend button
        tk.Button(root, text="Open in Browser", command=self.open_browser).pack()
        # stop subprocess using a button
        # tk.Button(root, text="Close Server", command=self.stop).pack()

    def reader_thread(self, q):
        """Read subprocess output and put it into the queue."""
        for line in iter(self.proc.stdout.readline, b''):
            q.put(line)
        print('done reading')

    def update(self, q):
        """Update GUI with items from the queue."""
        for line in islice(iter_except(q.get_nowait, Empty), 10000):
            if line is None:
                return # stop updating
            else:
                # self._var.set(line) # update GUI
                self.text.insert(tk.END, line)
                self.text.see(tk.END)
                self.root.focus()
        self.root.after(40, self.update, q) # schedule next update

    def open_browser(self):
        """Open frontend in browser."""
        print('opening in browser')
        try:
            # webbrowser.open_new_tab('http://127.0.0.1:'+str(conf['network_port']))
            webbrowser.open_new_tab('http://127.0.0.1:4444')
        except webbrowser.Error:
            print("Cannot open Webbrowser, please do so manually.")

    def stop(self):
        """Stop subprocess and quit GUI."""
        print('stoping')
        self.proc.terminate() # tell the subprocess to exit

        # kill subprocess if it hasn't exited after a countdown
        def kill_after(countdown):
            if self.proc.poll() is None: # subprocess hasn't exited yet
                countdown -= 1
                if countdown < 0: # do kill
                    print('killing')
                    self.proc.kill() # more likely to kill on *nix
                else:
                    self.root.after(1000, kill_after, countdown)
                    return # continue countdown in a second
            # clean up
            self.proc.stdout.close()  # close fd
            self.proc.wait()          # wait for the subprocess' exit
            self.root.destroy()       # exit GUI
        kill_after(countdown=5)


root = tk.Tk()
root.title("DriveboardApp Server")
app = SubprocessInGUI(root)
root.protocol("WM_DELETE_WINDOW", app.stop) # exit subprocess if GUI is closed
root.mainloop()
print('exited')



#
#
# #!/usr/bin/env python
# """
# - read subprocess output without threads using Tkinter
# - show the output in the GUI
# - stop subprocess on a button press
# """
# import logging
# import os
# import sys
# from subprocess import Popen, PIPE, STDOUT
#
# try:
#     import Tkinter as tk
# except ImportError: # Python 3
#     import tkinter as tk
#
# info = logging.getLogger(__name__).info
#
# # cmd
# cmd = ['/usr/bin/python', 'backend/app.py']
#
# class ShowProcessOutputDemo:
#     def __init__(self, root):
#         """Start subprocess, make GUI widgets."""
#         self.root = root
#
#         # start subprocess
#         self.proc = Popen(cmd, stdout=PIPE, stderr=STDOUT)
#
#         # show subprocess' stdout in GUI
#         self.root.createfilehandler(
#             self.proc.stdout, tk.READABLE, self.read_output)
#         self._var = tk.StringVar() # put subprocess output here
#
#         root.title("DriveboardApp Server")
#         # tk.Text(root, textvariable=self._var).pack()
#         tk.Label(root, textvariable=self._var).pack()
#
#         # stop subprocess using a button
#         tk.Button(root, text="Stop subprocess", command=self.stop).pack()
#
#     def read_output(self, pipe, mask):
#         """Read subprocess' output, pass it to the GUI."""
#         data = os.read(pipe.fileno(), 1 << 20)
#         if not data:  # clean up
#             info("eof")
#             self.root.deletefilehandler(self.proc.stdout)
#             self.root.after(5000, self.stop) # stop in 5 seconds
#             return
#         info("got: %r", data)
#         self._var.set(data.strip(b'\n').decode())
#
#     def stop(self, stopping=[]):
#         """Stop subprocess and quit GUI."""
#         if stopping:
#             return # avoid killing subprocess more than once
#         stopping.append(True)
#
#         info('stopping')
#         self.proc.terminate() # tell the subprocess to exit
#
#         # kill subprocess if it hasn't exited after a countdown
#         def kill_after(countdown):
#             if self.proc.poll() is None: # subprocess hasn't exited yet
#                 countdown -= 1
#                 if countdown < 0: # do kill
#                     info('killing')
#                     self.proc.kill() # more likely to kill on *nix
#                 else:
#                     self.root.after(1000, kill_after, countdown)
#                     return # continue countdown in a second
#
#             self.proc.stdout.close()  # close fd
#             self.proc.wait()          # wait for the subprocess' exit
#             self.root.destroy()       # exit GUI
#         kill_after(countdown=5)
#
# logging.basicConfig(level=logging.INFO, format='%(asctime)s %(message)s')
# root = tk.Tk()
# app = ShowProcessOutputDemo(root)
# root.protocol("WM_DELETE_WINDOW", app.stop) # exit subprocess if GUI is closed
# root.mainloop()
# info('exited')
#


# #!/usr/bin/python
#
# import subprocess
# import threading
# import Tkinter
#
#
# proc = subprocess.Popen(['/usr/bin/python', 'backend/app.py'],
#                         stdout=subprocess.PIPE,
#                         stderr=subprocess.STDOUT,
#                         universal_newlines=True)
#
# while True:
#     line = proc.stdout.readline()
#     if not line:
#         break
#     self.addText(line)
#     #this triggers an update of the text area, otherwise it doesn't update
#     self.textarea.update_idletasks()
#

#
# p = Popen(['/usr/bin/python', 'backend/app.py'], stdout=PIPE, stderr=STDOUT)
#
#
# class ReaderThread(threading.Thread):
#     def __init__(self, stream):
#         threading.Thread.__init__(self)
#         self.stream = stream
#
#     def run(self):
#         while True:
#             line = self.stream.readline()
#             if len(line) == 0:
#                 break
#             print line,
#
#
# reader = ReaderThread(p.stdout)
# reader.start()
#
#
# # tkinter
# tkroot = Tkinter.Tk()
# tkroot.title("DriveboardApp Server")
# tktext = Tkinter.Text(tkroot)
# tktext.pack()
# # tkroot.iconify()
# bClosed = False
# def on_closing():
#     global bClosed
#     bClosed = True
#     p.terminate()
#     tkroot.destroy()
#     print "closing"
# tkroot.protocol("WM_DELETE_WINDOW", on_closing)
# tkroot.mainloop()
# #
# # while True:
# #     try:
# #         c = p.stdout.read()
# #         out += c
# #         if c == '\n':
# #             sys.stdout.write(out)
# #             sys.stdout.flush()
# #             tktext.insert(Tkinter.END, out)
# #             tktext.see(Tkinter.END)
# #             if "END of DriveboardApp" in out or bClosed:
# #                 tkroot.destroy()
# #                 break
# #             out = ''
# #         tkroot.update()
# #         time.sleep(0.02)
# #     except KeyboardInterrupt:
# #         pass
# #         # print "term"
# #         # p.close()
# #         # break
# #
#
#
# # Wait until subprocess is done
# print "waiting"
# p.wait()
#
# # Wait until we've processed all output
# reader.join()
#
# print "Done!"




#
#
# import os
# import time
# import sys
# import Tkinter
# import subprocess as sub
# p = sub.Popen(['/usr/bin/python', 'backend/app.py'], shell=False, stdout=sub.PIPE, stderr=sub.STDOUT)
#
#
# # Tkinter window
# tkroot = Tkinter.Tk()
# tkroot.title("DriveboardApp Server")
# tktext = Tkinter.Text(tkroot)
# tktext.pack()
# # tkroot.iconify()
# bClosed = False
# def on_closing():
#     global bClosed
#     bClosed = True
#     p.terminate()
#     print "closing"
# tkroot.protocol("WM_DELETE_WINDOW", on_closing)
# tkroot.update()
#
# out = ''
# while True:
#     try:
#         c = p.stdout.read()
#         out += c
#         if c == '\n':
#             sys.stdout.write(out)
#             sys.stdout.flush()
#             tktext.insert(Tkinter.END, out)
#             tktext.see(Tkinter.END)
#             if "END of DriveboardApp" in out or bClosed:
#                 tkroot.destroy()
#                 break
#             out = ''
#         tkroot.update()
#         time.sleep(0.02)
#     except KeyboardInterrupt:
#         pass
#         # print "term"
#         # p.close()
#         # break
