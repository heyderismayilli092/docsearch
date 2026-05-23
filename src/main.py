#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import gi
gi.require_version("Gtk", "3.0")
from gi.repository import Gtk, GObject, Gdk

import os
import locale
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
        self.scrolled_window = self.builder.get_object("scrolled_window")  # scrolled window
        self.scrolled_window.set_min_content_height(400)  # the height of the list window is being adjusted in pixels

        # -------Signals-------
        # Main Window
        self.mainwindow.connect("destroy", self._on_destroy)
        self.mainwindow.show_all()
        self.other_process()



    # other process functions
    def other_process(self):
        self.cssload()  # load css
        check_database()  # check database status
        # listing files
        for f in files_list():
            row = self.create_row(os.path.basename(f), f)
            self.listbox.add(row)
        self.listbox.show_all()


    # CSS theme
    def cssload(self):
        css = b"""
        #listbox {
          margin-bottom: 20px;
        }
        """
        provider = Gtk.CssProvider()
        provider.load_from_data(css)
        screen = Gdk.Screen.get_default()
        Gtk.StyleContext.add_provider_for_screen(
            screen,
            provider,
            Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION
        )


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
        short_path = fullpath[:15] + "..." if len(fullpath) > 15 else fullpath
        label_path = Gtk.Label(label=short_path)
        label_path.set_xalign(0)

        # BUTTON box and buttons
        button_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=2)
        button_box.set_halign(Gtk.Align.END)
        button_open = Gtk.Button(label="Open")
        button_info = Gtk.Button(label="Info")

        # -------Signals-------
        button_open.connect("clicked", self.on_open_clicked, fullpath)
        button_info.connect("clicked", self.on_info_clicked, fullpath)
        # ---------------------

        text_box.pack_start(label_name, False, False, 0)
        text_box.pack_start(label_path, False, False, 0)

        button_box.pack_start(button_open, False, False, 0)
        button_box.pack_start(button_info, False, False, 0)

        # ROW placement (efforts were made to minimize gaps)
        row_box.pack_start(image, False, False, 3)
        row_box.pack_start(text_box, False, False, 3)
        row_box.pack_end(button_box, False, False, 3)

        return row_box


    # test
    def on_open_clicked(self, button, fullpath):
        print("OPEN:", fullpath)

    # test
    def on_info_clicked(self, button, fullpath):
        print("INFO:", fullpath)


    def _on_destroy(self, widget):
        Gtk.main_quit()

app = pardusdocsearch()
Gtk.main()

