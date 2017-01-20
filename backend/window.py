# -*- coding: UTF-8 -*-
import os
import sys
import itertools
import webbrowser

import Queue
import Tkinter as tk

from config import conf

__author__  = 'Stefan Hechenberger <stefan@nortd.com>'


def init():
    root = tk.Tk()
    root.title("DriveboardApp Server")
    img = tk.PhotoImage(file=os.path.join(conf['rootdir'], 'backend', 'icon.gif'))
    root.tk.call('wm', 'iconphoto', root._w, img)
    # root.iconify()  # not working as expected on osx


    # text widget
    text = tk.Text(root)
    text.pack()
    # add copy to clipboard feature
    def copy(event):
        selected = text.get("sel.first", "sel.last")
        if selected:
            root.clipboard_clear()
            root.clipboard_append(selected)
    text.bind("<Control-c>", copy)


    # open frontend button
    def open_browser():
        print('opening in browser')
        try:
            webbrowser.open_new_tab('http://127.0.0.1:4444')
        except webbrowser.Error:
            print("Cannot open Webbrowser, please do so manually.")
    tk.Button(root, text="Open in Browser", command=open_browser).pack()


    # output queue, required because of tkinter thread issues
    q = Queue.Queue()

    class OutputHandler(object):
        def write(self, msg):
            q.put(msg)
        def flush(self):
            pass

    stdout_old = sys.stdout
    stderr_old = sys.stderr
    output = OutputHandler()
    sys.stdout = output
    sys.stderr = output


    # output consumer, a recursive tkinter callback
    update_callback_id = None
    def iterex(function, exception):
        # helper func, like builtin iter() but stops on exception
        try:
            while True:
                yield function()
        except exception:
            return

    def update(q):
        for line in itertools.islice(iterex(q.get_nowait, Queue.Empty), 10000):
            if line is None:
                return  # stop updating
            else:
                text.insert(tk.END, line)
                text.see(tk.END)
                root.focus()
        global update_callback_id
        update_callback_id = root.after(40, update, q)  # schedule next update
    update(q)  # start recursive updates


    # good exiting behavior
    def quit():
        global update_callback_id
        root.after_cancel(update_callback_id)
        sys.stdout = stdout_old
        sys.stderr = stderr_old
        root.destroy()
    root.protocol("WM_DELETE_WINDOW", quit)
    root.bind("<Control-q>", lambda event: quit())


    return root


if __name__ == "__main__":
    root = init()
    root.mainloop()
