#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gdk, GLib

import os
import subprocess
import locale
import threading
import queue
import time
import docsearch
import docextract
from docsearch_functions import files_list, check_database

locale.bindtextdomain('pardus-docsearch', '/usr/share/locale')
locale.textdomain('pardus-docsearch')

GLADE_FILE = os.path.dirname(os.path.abspath(__file__)) + "/../ui/MainWindow.glade"


class pardusdocsearch:
    def __init__(self):
        self.builder = Gtk.Builder()
        self.builder.add_from_file(GLADE_FILE)

        # -------Widget referansları-------
        # Main Window
        self.mainwindow = self.builder.get_object("mainwindow")  # home window
        self.listbox    = self.builder.get_object("listbox")  # listbox object
        self.mainstack      = self.builder.get_object("main_stack")
        self.scrolled_window = self.builder.get_object("scrolled_window")  # scrolled window
        self.scrolled_window.set_min_content_height(400)  # the height of the list window is being adjusted in pixels

        # -------Signals-------
        # Main Window
        self.mainwindow.connect("destroy", self._on_destroy)
        self.mainwindow.show_all()

        check_database()
        self.mainstack.set_visible_child_name("page0")
        GLib.idle_add(self.start_background_once)  # the process will run in the background immediately after the application starts
        self._row_queue = queue.Queue()  # process queue structure  Thread -> main thread data transfer
        self._consuming = False


    def start_background_once(self):
        # start worker thread
        t = threading.Thread(target=self._worker_produce_rows, daemon=True)
        t.start()

        # start the loop that consumes the queue in the main thread
        if not self._consuming:
            self._consuming = True
            GLib.timeout_add(100, self._consume_queue)  # consume at 100 ms intervals
        return False


    def _worker_produce_rows(self):
        # heavy work: listing files, printing to database
        fileslist = files_list()
        for f in fileslist:  # files_list() --- May be CPU/IO bound
            self._row_queue.put(f)

        # report to the main cycle that production is complete
        self._row_queue.put(None)  # sentinel

    # It runs on the main thread (via GLib.timeout_add). It retrieves items from the queue, calling create_row and listbox.add here
    def _consume_queue(self):
        try:
            while True:
                try:
                    item = self._row_queue.get_nowait()
                except queue.Empty:
                    return True  # The queue is currently empty, return True to be called again

                if item is None:
                    # Sentinel: generation finished
                    self.mainstack.set_visible_child_name("mainbox")
                    self.listbox.show_all()
                    return False  # finish consumption, stop timeout
                else:
                    # create and add rows safely in the main thread
                    row = self.create_row(os.path.basename(item), item)
                    self.listbox.add(row)
        except Exception as e:
            print("Error occurring during queue consumption:", e)
            return False


    # row function to be created for each data point
    def create_row(self, filename, fullpath):
        row_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)

        # ICON box
        image = Gtk.Image.new_from_icon_name("text-x-generic",Gtk.IconSize.BUTTON)
        image.set_halign(Gtk.Align.START)

        # TEXT box and labels
        text_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        text_box.set_halign(Gtk.Align.CENTER)
        label_name = Gtk.Label(label=filename)
        label_name.set_xalign(0)

        # the file path text is being shortened
        short_path = fullpath[:50] + "..." if len(fullpath) > 50 else fullpath
        label_path = Gtk.Label(label=short_path)
        label_path.set_xalign(0)

        # BUTTON box and buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        button_box.set_halign(Gtk.Align.END)
        button_open = Gtk.Button(label="Open")
        button_opndir = Gtk.Button(label="Open in directory")

        # -------Signals-------
        button_open.connect("clicked", self.on_open_file, fullpath)
        button_opndir.connect("clicked", self.on_open_in_directory, fullpath)
        # ---------------------

        text_box.pack_start(label_name, False, False, 0)
        text_box.pack_start(label_path, False, False, 0)

        button_box.pack_start(button_open, False, False, 0)
        button_box.pack_start(button_opndir, False, False, 0)

        # ROW placement (efforts were made to minimize gaps)
        row_box.pack_start(image, False, False, 3)
        row_box.pack_start(text_box, False, False, 3)
        row_box.pack_end(button_box, False, False, 3)

        return row_box


    # file open
    def on_open_file(self, button, fullpath):
        subprocess.run(["xdg-open", fullpath])

    # file open in directory
    def on_open_in_directory(self, button, fullpath):
        subprocess.run(["thunar", fullpath])


    def _on_destroy(self, widget):
        Gtk.main_quit()

app = pardusdocsearch()
Gtk.main()

