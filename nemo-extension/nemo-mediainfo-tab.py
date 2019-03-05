#!/usr/bin/python
#coding: utf-8

import locale, gettext, os

try:
  from urllib import unquote
except ImportError:
  from urllib.parse import unquote

from gi.repository import GObject, Gtk, Nemo

try:
  from MediaInfoDLL import *
except ImportError:
  from MediaInfoDLL3 import *

lang = locale.getdefaultlocale()[0]
locale_path = os.path.join(os.path.dirname(__file__), "nemo-mediainfo-tab/locale")
locale_file = os.path.join(locale_path, lang+".csv")
if(not os.path.isfile(locale_file)):
  lang = lang.split("_")[0]
  locale_file = os.path.join(locale_path, lang+".csv")

excludeList = ["METADATA_BLOCK_PICTURE"]

GUI = """
<interface>
  <requires lib="gtk+" version="3.0"/>
  <object class="GtkScrolledWindow" id="mainWindow">
    <property name="visible">True</property>
    <property name="can_focus">True</property>
    <property name="hscrollbar_policy">never</property>
    <child>
      <object class="GtkViewport" id="viewport1">
        <property name="visible">True</property>
        <property name="can_focus">False</property>
        <child>
          <object class="GtkGrid" id="grid">
            <property name="visible">True</property>
            <property name="can_focus">False</property>
            <property name="vexpand">True</property>
            <property name="row_spacing">4</property>
            <property name="column_spacing">16</property>
          </object>
        </child>
      </object>
    </child>
  </object>
</interface>"""

class MediainfoPropertyPage(GObject.GObject, Nemo.PropertyPageProvider, Nemo.NameAndDescProvider):

  def get_property_pages(self, files):
    # files: list of NemoVFSFile
    if len(files) != 1:
      return

    file = files[0]
    if file.get_uri_scheme() != 'file':
      return

    if file.is_directory():
      return

    filename = unquote(file.get_uri()[7:])

    try:
      filename = filename.decode("utf-8")
    except:
      pass

    MI = MediaInfo()
    MI.Open(filename)
    MI.Option_Static("Complete")
    MI.Option_Static("Language", "file://{}".format(locale_file))
    info = MI.Inform().splitlines()
    if len(info) < 8:
      return

    locale.setlocale(locale.LC_ALL, '')
    gettext.bindtextdomain("nemo-extensions")
    gettext.textdomain("nemo-extensions")
    _ = gettext.gettext

    self.property_label = Gtk.Label(_('Media Info'))
    self.property_label.show()

    self.builder = Gtk.Builder()
    self.builder.set_translation_domain('nemo-extensions')
    self.builder.add_from_string(GUI)

    self.mainWindow = self.builder.get_object("mainWindow")
    self.grid = self.builder.get_object("grid")

    top = 0
    for line in info:
      tag = line[:41].strip()
      if tag not in excludeList:
        label = Gtk.Label()
        label.set_markup("<b>" + tag + "</b>")
        label.set_justify(Gtk.Justification.LEFT)
        label.set_halign(Gtk.Align.START)
        label.show()
        self.grid.attach(label, 0, top, 1, 1)
        label = Gtk.Label()
        label.set_text(line[42:].strip())
        label.set_justify(Gtk.Justification.LEFT)
        label.set_halign(Gtk.Align.START)
        label.set_selectable(True)
        label.set_line_wrap(True)
        label.show()
        self.grid.attach(label, 1, top, 1, 1)
        top += 1

    return Nemo.PropertyPage(name="NemoPython::mediainfo", label=self.property_label, page=self.mainWindow),

  def get_name_and_desc(self):
    return [("Nemo Media Info Tab:::View media information from the properties tab")]
