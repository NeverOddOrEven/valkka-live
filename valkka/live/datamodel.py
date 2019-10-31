"""
datamodel.py : Datatypes that can be saved and visualized using cute_mongo_forms

Copyright 2018 Sampsa Riikonen

Authors: Sampsa Riikonen

This file is part of the Valkka Live video surveillance program

Valkka Live is free software: you can redistribute it and/or modify it under the terms of the GNU Affero General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU Affero General Public License for more details.

You should have received a copy of the GNU Affero General Public License along with this program.  If not, see <https://www.gnu.org/licenses/>

@file    datamodel.py
@author  Sampsa Riikonen
@date    2018
@version 0.8.0 
@brief   Datatypes that can be saved and visualized using cute_mongo_forms
"""

from PySide2 import QtWidgets, QtCore, QtGui  # Qt5
import sys
import os
# from valkka.core import *
from valkka.api2.tools import parameterInitCheck

from cute_mongo_forms.db import SimpleCollection
from cute_mongo_forms.column import LineEditColumn, IntegerColumn, ConstantIntegerColumn, IPv4AddressColumn, LabelColumn, CheckBoxColumn
from cute_mongo_forms.row import ColumnSpec, Row, RowWatcher
from cute_mongo_forms.container import List, SimpleForm

from valkka.live import default
from valkka.live.form import SlotFormSet, USBCameraColumn
from valkka.live import constant, tools, style


class ListAndForm:
    """Creates a composite widget using a List and a FormSet
    """

    def __init__(self, lis, form, title="", parent=None):
        self.title = title
        self.lis = lis
        self.form = form

        self.widget = QtWidgets.QWidget(parent)  # create a new widget
        self.lay = QtWidgets.QVBoxLayout(
            self.widget)  # attach layout to that widget
        self.label = QtWidgets.QLabel(self.title, self.widget)

        self.subwidget = QtWidgets.QWidget(self.widget)
        self.sublay = QtWidgets.QHBoxLayout(self.subwidget)

        self.lay.addWidget(self.label)
        self.lay.addWidget(self.subwidget)

        self.subwidget.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Expanding)
        self.lis.widget.setSizePolicy(
            QtWidgets.QSizePolicy.Minimum,
            QtWidgets.QSizePolicy.Minimum)
        self.lis.widget.setMaximumWidth(100)

        # get widget from List and set its parent to widget
        self.lis. widget.setParent(self.subwidget)
        self.form.widget.setParent(self.subwidget)
        # add List's internal widget to widget's layout
        self.sublay. addWidget(self.lis.widget)
        self.sublay. addWidget(self.form.widget)
        self.lis.widget.currentItemChanged. connect(
            self.form.chooseForm_slot)  # connections between list and the form
        self.form.signals.modified.connect(self.lis.update_slot)
        self.modified = self.form.signals.modified  # shorthand

    def update(self):
        """Widgets might have drop-down menus and sublists that depend on other document collections
        """
        self.form.updateWidget()

    def getForm(self):
        return self.form

    def choose_first_slot(self):
        self.lis.widget.setCurrentItem(self.lis.widget.item(0))
        
        
class DataModel:

    # Device collection: RTSP Cameras, SDP files, etc.

    class EmptyRow(Row):
        name = "<Empty>"
        columns = [
            ColumnSpec(
                ConstantIntegerColumn,
                key_name="slot",
                label_name="Slot"),
            ]
            
        def isActive(self):
            """Is this row class visible in the form drop-down menu
            """
            return True
            
            
    class USBCameraRow(Row):
        name = "H264 USB Camera"
        columns = [
            ColumnSpec(ConstantIntegerColumn, key_name="slot", label_name="Slot"),
            ColumnSpec(USBCameraColumn, key_name ="address", label_name="Device")
            ]
        
        def isActive(self):
            """Show only if there are USB cams
            """
            return len(tools.getH264V4l2())>0
        
    
        
    class RTSPCameraRow(Row):
        name = "RTSP Camera"
        columns = [
            ColumnSpec(
                ConstantIntegerColumn,
                key_name="slot",
                label_name="Slot"),
            ColumnSpec(
                IPv4AddressColumn,
                key_name="address",
                label_name="IP Address"),
            ColumnSpec(
                LineEditColumn,
                key_name="username",
                label_name="Username"),
            ColumnSpec(
                LineEditColumn,
                key_name="password",
                label_name="Password"),
            ColumnSpec(
                LineEditColumn,
                key_name="port",
                label_name="Port"),
            ColumnSpec(
                LineEditColumn, 
                key_name="tail", 
                label_name="Tail"),
            
            ColumnSpec(
                LineEditColumn, 
                key_name="subaddress_main", 
                label_name="Subaddress"),
            ColumnSpec(
                CheckBoxColumn, 
                key_name="live_main", 
                label_name="Use stream",
                def_value=True),
            ColumnSpec(
                CheckBoxColumn, 
                key_name="rec_main", 
                label_name="Record stream",
                def_value=False),
            
            ColumnSpec(
                LineEditColumn, 
                key_name="subaddress_sub", 
                label_name="Subaddress"),
            ColumnSpec(
                CheckBoxColumn, 
                key_name="live_sub", 
                label_name="Use stream",
                def_value=False),
            ColumnSpec(
                CheckBoxColumn, 
                key_name="rec_sub", 
                label_name="Record stream",
                def_value=False)
            ]
        
        def isActive(self):
            return True
        
        
        
        @classmethod
        def getMainAddressFromDict(cls, dic):
            st = "rtsp://"
            st += dic["username"] + ":"
            st += dic["password"] + "@"
            st += dic["address"]
            if (dic["port"].strip() != ""):
                st += ":" + dic["port"].strip()
            if (len(dic["tail"]) > 0):
                st += "/" + dic["tail"]
            if (len(dic["subaddress_main"]) > 0):
                st += "/" + dic["subaddress_main"]
            return st
    
        @classmethod
        def getSubAddressFromDict(cls, dic):
            st = "rtsp://"
            st += dic["username"] + ":"
            st += dic["password"] + "@"
            st += dic["address"]
            if (dic["port"].strip() != ""):
                st += ":" + dic["port"].strip()
            if (len(dic["tail"]) > 0):
                st += "/" + dic["tail"]
            if (len(dic["subaddress_main"]) > 0):
                st += "/" + dic["subaddress_sub"]
            return st


        def makeWidget(self):
            """Subclassed from Row : custom form.  Add a summary RTSP address in the end of the form, etc.
            """
            # super().makeWidget() # do all by hand
            
            class FormWidget(QtWidgets.QWidget):
                """Just a QWidget that sends a signal when its shown
                """
            
                class Signals(QtCore.QObject):
                    show = QtCore.Signal()
            
                def __init__(self, parent = None):
                    super().__init__(parent)
                    self.signals = self.Signals()
            
                def showEvent(self, e):
                    self.signals.show.emit()
                    e.accept()
        
            self.widget = FormWidget()
            self.lay = QtWidgets.QGridLayout(self.widget)
            
            cc=0;
            self.placeWidget(cc, "slot"); cc+=1
            self.placeWidget(cc, "address"); cc+=1
            self.placeWidget(cc, "username"); cc+=1
            self.placeWidget(cc, "password"); cc+=1
            self.placeWidget(cc, "port"); cc+=1
            self.placeWidget(cc, "tail"); cc+=1
            
            # Mainstream
            self.label_mainstream = QtWidgets.QLabel("Mainstream", self.widget)
            self.label_mainstream.setStyleSheet(style.form_highlight)
            self.placeWidgetPair(cc, (self.label_mainstream, None)); cc+=1
            self.placeWidget(cc, "subaddress_main"); cc+=1
            # complete RTSP address
            self.label_mainstream_address = QtWidgets.QLabel("RTSP address", self.widget)
            self.mainstream_address = QtWidgets.QLabel("", self.widget)
            self.placeWidgetPair(cc, (self.label_mainstream_address, self.mainstream_address)); cc+=1
            # live and rec
            self.placeWidget(cc, "live_main"); cc+=1
            self.placeWidget(cc, "rec_main"); cc+=1
            
            # Substream
            self.label_substream = QtWidgets.QLabel("Substream", self.widget)
            self.label_substream.setStyleSheet(style.form_highlight)
            self.placeWidgetPair(cc, (self.label_substream, None)); cc+=1
            self.placeWidget(cc, "subaddress_sub"); cc+=1
            # complete RTSP address
            self.label_substream_address = QtWidgets.QLabel("RTSP address", self.widget)
            self.substream_address = QtWidgets.QLabel("", self.widget)
            self.placeWidgetPair(cc, (self.label_substream_address, self.substream_address)); cc+=1
            # live and rec
            self.placeWidget(cc, "live_sub"); cc+=1
            self.placeWidget(cc, "rec_sub"); cc+=1
            
            """ # definitely NOT here!
            # self.copy_label = QtWidgets.QLabel("Copy this camera", self.widget)
            self.copy_button = QtWidgets.QPushButton("Copy", self.widget)
            self.placeWidgetPair(cc, (self.copy_button, None))
            self.copy_button.clicked.connect(self.copy_slot)
            """
            
            self.connectNotifications()
        
            def rec_main_clicked():
                if not self["live_main"].widget.isChecked(): # rec requires live
                    print("live_main is NOT checked")
                    self["rec_main"].widget.setChecked(False)
                if self["rec_main"].widget.isChecked(): # rec main excludes rec sub
                    self["rec_sub"].widget.setChecked(False)
            
            def rec_sub_clicked():
                if not self["live_sub"].widget.isChecked(): # rec requires live
                    print("live_sub is NOT checked")
                    self["rec_sub"].widget.setChecked(False)
                if self["rec_sub"].widget.isChecked(): # rec sub excludes rec main
                    self["rec_main"].widget.setChecked(False)
                    
            self["rec_main"].widget.clicked.connect(rec_main_clicked)
            self["rec_sub"]. widget.clicked.connect(rec_sub_clicked)
            self.widget.signals.show.connect(self.show_slot)
            
            # TODO: remove these restrictions once functional:
            self["subaddress_main"].widget.setEnabled(False)
            self["subaddress_sub"].widget.setEnabled(False)
            self["live_main"].widget.setEnabled(False)
            self["rec_main"].widget.setEnabled(False)
            self["live_sub"].widget.setEnabled(False)
            self["rec_sub"].widget.setEnabled(False)
            
            
            
        """
        def get(self, collection, _id):
            #Subclassed from Row : Load one entry from db to QtWidgets
            super().get(collection, _id)
            self.update_notify_slot()
        """
           
            
        def getMainAddress(self):
            # e.g. : rtsp://admin:12345@192.168.1.4/tail
            dic = self.__collect__()  # returns a dictionary of column values
            return DataModel.RTSPCameraRow.getMainAddressFromDict(dic)

        def getSubAddress(self):
            # e.g. : rtsp://admin:12345@192.168.1.4/tail
            dic = self.__collect__()  # returns a dictionary of column values
            return DataModel.RTSPCameraRow.getSubAddressFromDict(dic)

        def update_notify_slot(self):
            """This slot gets pinged always when the form fields have been updated
            """
            # pass
            # print("RTSPCameraRow: value changed")
            self.mainstream_address.setText(self.getMainAddress())
            self.substream_address.setText(self.getSubAddress())
            # self.copy_button.setEnabled(False) # must save before can copy # nopes ..
            
            # rec main and sub exclude each other
            # rec requires live
            
        def show_slot(self):
            self.mainstream_address.setText(self.getMainAddress())
            self.substream_address.setText(self.getSubAddress())
                
                
    class RTSPCameraDevice:
        """Device class used in drag'n'drop.  Copies the members of RTSPCameraRow
        """

        parameter_defs = {
            "_id"       : int,
            "slot"      : int,
            "address"   : str,
            "username"  : str,
            "password"  : str,
            "port"      : (str, ""),
            "tail"      : (str, ""),
            "subaddress_main" : (str, ""),
            "live_main" : (bool, True),
            "rec_main"  : (bool, False),
            "subaddress_sub"  : (str, ""),
            "live_sub" : (bool, False),
            "rec_sub"  : (bool, False)
        }

        def __init__(self, **kwargs):
            # auxiliary string for debugging output
            self.pre = self.__class__.__name__ + " : "
            # check for input parameters, attach them to this instance as
            # attributes
            parameterInitCheck(DataModel.RTSPCameraDevice.parameter_defs, kwargs, self)

        def __eq__(self, other):
            return self._id == other._id
                        
        def getMainAddress(self):
            st = "rtsp://" + self.username + ":" + self.password + "@" + self.address 
            if (len(self.tail)>0):
                st += "/" + self.tail 
            if (len(self.subaddress_main)>0):
                st += "/" + self.subaddress_main
            return st

        def getSubAddress(self):
            st = "rtsp://" + self.username + ":" + self.password + "@" + self.address
            if (len(self.tail)>0):
                st += "/" + self.tail 
            if (len(self.subaddress_sub)>0):
                st += "/" + self.subaddress_main
            return st

        def getLabel(self):
            st = "rtsp://" + self.address
            if (len(self.tail)>0):
                st += "/" + self.tail
            return st
        
        # the following methods give the true slot numbers used by Valkka
        # one slot for main, sub and recorded stream per camera
        # 1..3, 4..6, 7..9, etc.
        def getLiveMainSlot(self):
            return (self.slot-1)*3+1
        
        def getLiveSubSlot(self):
            return (self.slot-1)*3+2
        
        def getRecSlot(self):
            return (self.slot-1)*3+3
            

    class USBCameraDevice:
        """Device class used in drag'n'drop.  Copies the members of RTSPCameraRow
        """

        parameter_defs = {
            "_id"       : int,
            "slot"      : int,
            "address"   : str
        }

        def __init__(self, **kwargs):
            # auxiliary string for debugging output
            self.pre = self.__class__.__name__ + " : "
            # check for input parameters, attach them to this instance as
            # attributes
            parameterInitCheck(DataModel.USBCameraDevice.parameter_defs, kwargs, self)

        def __eq__(self, other):
            return self._id == other._id
                        
        def getMainAddress(self):
            return self.address

        def getSubAddress(self):
            return self.address
        
        def getLabel(self):
            return "usb:"+self.address
            

        # the following methods give the true slot numbers used by Valkka
        # one slot for main, sub and recorded stream per camera
        # 1..3, 4..6, 7..9, etc.
        def getLiveMainSlot(self):
            return (self.slot-1)*3+1
        
        def getLiveSubSlot(self):
            return (self.slot-1)*3+2
        
        def getRecSlot(self):
            return (self.slot-1)*3+3
    


    # A general collection for misc. stuff: configuration, etc.

    class MemoryConfigRow(Row):

        columns = [
            ColumnSpec(
                IntegerColumn,
                key_name="msbuftime",
                label_name="Buffering time (ms)",
                min_value=50,
                max_value=1000,
                def_value=default.memory_config["msbuftime"]),
            ColumnSpec(
                IntegerColumn,
                key_name="n_720p",
                label_name="Number of 720p streams",
                min_value=0,
                max_value=1024,
                def_value=default.memory_config["n_720p"]),
            ColumnSpec(
                IntegerColumn,
                key_name="n_1080p",
                label_name="Number of 1080p streams",
                min_value=0,
                max_value=1024,
                def_value=default.memory_config["n_1080p"]),
            ColumnSpec(
                IntegerColumn,
                key_name="n_1440p",
                label_name="Number of 2K streams",
                min_value=0,
                max_value=1024,
                def_value=default.memory_config["n_1440p"]),
            ColumnSpec(
                IntegerColumn,
                key_name="n_4K",
                label_name="Number of 4K streams",
                min_value=0,
                max_value=1024,
                def_value=default.memory_config["n_4K"]),
            ColumnSpec(
                CheckBoxColumn,
                key_name="bind",
                label_name="Bind Valkka threads to cores",
                def_value=default.memory_config["bind"])
        ]

        def getNFrames(self, key):
            """Get number of necessary frames for certain camera resolution

            :param key:   n720p, n1080p, etc.
            """

            buftime = self["buftime"]
            ncam = self[key]

            # assume 25 fps cameras
            return int((buftime / 1000) * 25 * ncam)

    # *** Simple lists ***

    class DeviceList(List):

        class SortableWidgetItem(QtWidgets.QListWidgetItem):
            """A sortable listwidget item class
            """

            def __init__(self):
                super().__init__()
                # self.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)

            def __lt__(self, other):
                try:
                    return int(self.slot) < int(other.slot)
                except Exception:
                    return QListWidgetItem.__lt__(self, other)

        def makeWidget(self):
            super().makeWidget()
            # self.widget.setSizePolicy(QtWidgets.QSizePolicy.Minimum, QtWidgets.QSizePolicy.Expanding)


        def update(self):
            # Fills the root and subwidgets with data.
            self.widget.clear()
            self.items_by_id={}
            for entry in self.collection.get():
                item  =self.createItem()
                label =self.makeLabel(entry)
                item.setText(label)
                item._id         =entry["_id"]
                item.slot        =int(entry["slot"]) # add an extra attribute
                try:
                    item.classname =entry["classname"]
                except KeyError:
                    raise(KeyError("Your database contains crap.  Do a purge"))
                self.items_by_id[item._id]=item
                self.widget.addItem(item)
            self.widget.sortItems()
            self.widget.setMinimumWidth(self.widget.sizeHintForColumn(0))


        def createItem(self):
            """Overwrite in child classes to create custom items (say, sortable items, etc.)
            """
            return self.SortableWidgetItem()

        def makeLabel(self, entry):
            # print("DataModel : makeLabel :", entry["classname"])
            st = str(entry["slot"])
            if (entry["classname"] == "RTSPCameraRow"):
                st += " RTSP ("+entry["address"]+")"
            elif (entry["classname"] == "USBCameraRow"):
                st += " USB ("+str(entry["address"])+")" # could be NoneType
            return st

    # *** A stand-alone form for MemoryConfigRow ***

    class MemoryConfigForm(SimpleForm):

        class Signals(QtCore.QObject):
            save = QtCore.Signal()

        parameter_defs = {
            "row_class": RowWatcher,
            "collection": None
        }

        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.signals = self.Signals()
            self.load()

        def makeWidget(self):
            super().makeWidget()

            self.button_row = QtWidgets.QWidget(self.widget)
            self.button_lay = QtWidgets.QHBoxLayout(self.button_row)
            self.lay.addWidget(self.button_row)

            self.reset_button = QtWidgets.QPushButton("Reset", self.button_row)
            self.save_button = QtWidgets.QPushButton("Save", self.button_row)
            self.button_lay.addWidget(self.reset_button)
            self.button_lay.addWidget(self.save_button)

            self.info_label = QtWidgets.QLabel("Saving restarts all Valkka services", self.widget)
            self.lay.addWidget(self.info_label)
            
            self.reset_button.clicked.connect(self.row_instance.clear)
            self.save_button.clicked.connect(self.save_slot)

        def load(self):
            try:
                el = next(self.collection.get(
                    {"classname": DataModel.MemoryConfigRow.__name__}))
            except StopIteration:
                print(self.pre, "no row!")
            else:
                print(self.pre, "reading saved")
                self.row_instance.get(self.collection, el["_id"])

        def save_slot(self):
            try:
                el = next(self.collection.get(
                    {"classname": DataModel.MemoryConfigRow.__name__}))
            except StopIteration:
                print(self.pre, "new row")
                _id = self.row_instance.new(
                    self.collection)  # create a new instance
            else:
                print(self.pre, "update row")
                _id = el["_id"]
                self.row_instance.update(self.collection, _id)

            self.signals.save.emit()
            
    
    # ** phew, internal classes end.  DataModel methods follow **
    def __init__(self, directory="."):
        """DataModel ctor
        """
        self.directory = directory
        self.define()

    def __del__(self):
        # self.close()
        pass

    def close(self):
        # print("close: ",self.area_rights_collection)
        for collection in self.collections:
            collection.close()

    def clearAll(self):
        # print("DataModel", "clearAll")
        self.clearCameraCollection()
        self.config_collection.clear()

    def saveAll(self):
        self.camera_collection.save()
        self.config_collection.save()

    def clearCameraCollection(self):
        self.camera_collection.clear()
        for i in range(1, constant.max_devices + 1):
            self.camera_collection.new(self.EmptyRow, {"slot": i})

    def checkCameraCollection(self):
        c=0
        for c, device in enumerate(self.camera_collection.get()):
            pass
        if (c != constant.max_devices - 1):
            return False
        return True

    def autoGenerateCameraCollection(self, base_address, nstart, n, port, tail, username, password):
        """
        :param:  base_address    str, e.g. "192.168.1"
        :param:  nstart          int, e.g. 24
        :param:  n               int, how many ips generated 
        """
        self.camera_collection.clear()
        self.camera_collection.save()
        cc = nstart
        for i in range(1, min((n + 1, constant.max_devices + 1))):
            print(i)
            self.camera_collection.new(
                self.RTSPCameraRow, 
                {
                    "slot":         i, 
                    "address":      base_address+"."+str(cc),
                    "username":     username,
                    "password":     password,
                    "port":         port,
                    "tail":         tail,
                    
                    "subaddress_main" : "",
                    "live_main"       : True,
                    "rec_main"        : False,
                    
                    "subaddress_sub"  : "",
                    "live_sub"        : False,
                    "rec_sub"         : False
                })
            cc +=1
        
        print("Camera addesses now:")
        for c, device in enumerate(self.camera_collection.get()):
            print(c+1, self.RTSPCameraRow.getMainAddressFromDict(device))
        
        for i in range(n+1, constant.max_devices + 1):
            self.camera_collection.new(self.EmptyRow, {"slot": i})

        self.camera_collection.save()
        
        print("Camera collection now:")
        for c, device in enumerate(self.camera_collection.get()):
            print(c+1, device)
        

            
    def purge(self):
        """For migrations / cleanup.  Collections should be in correct order.
        """
        for collection in self.collections:
            # print("purging",collection)
            collection.purge()

    def define(self):
        """Define column patterns and collections
        """
        self.collections = []

        self.camera_collection = \
            SimpleCollection(filename=os.path.join(self.directory, "devices.dat"),
                             row_classes=[
                DataModel.EmptyRow,
                DataModel.RTSPCameraRow,
                DataModel.USBCameraRow
            ]
            )
        self.collections.append(self.camera_collection)

        self.config_collection = \
            SimpleCollection(filename=os.path.join(self.directory, "config.dat"),
                             row_classes=[  # we could dump here all kinds of info related to different kind of configuration forms
                DataModel.MemoryConfigRow
            ]
            )
        self.collections.append(self.config_collection)

    def getDeviceList(self):
        return DataModel.DeviceList(collection=self.camera_collection)

    def getDeviceListAndForm(self, parent):
        device_list = DataModel.DeviceList(collection=self.camera_collection)
        device_form = SlotFormSet(collection=self.camera_collection)
        return ListAndForm(device_list, device_form,
                           title="Camera configuration", parent=parent)

    def getConfigForm(self):
        return DataModel.MemoryConfigForm(
            row_class=DataModel.MemoryConfigRow, collection=self.config_collection)


    def getRowsById(self, query):
        rows = self.camera_collection.get(query)
        rows_by_id = {}
        for row in rows:
            rows_by_id[row["_id"]] = row
        
        return rows_by_id
    
    
    def getDevicesById(self): # , query):
        """
        rows = self.camera_collection.get(query)
        devices_by_id = {}
        for row in rows:
            row.pop("classname")
            device = DataModel.RTSPCameraDevice(**row)
            devices_by_id[device._id] = device
        return devices_by_id
        """
        rows = self.camera_collection.get()
        devices_by_id = {}
        for row in rows:
            classname=row.pop("classname")
            if (classname == "RTSPCameraRow"):
                device = DataModel.RTSPCameraDevice(**row)
            elif (classname == "USBCameraRow"):
                device = DataModel.USBCameraDevice(**row)
            else:
                device = None
            if (device):
                devices_by_id[device._id] = device
        return devices_by_id
        


class MyGui(QtWidgets.QMainWindow):

    def __init__(self, parent=None):
        super(MyGui, self).__init__()
        self.initVars()
        self.setupUi()
        self.openValkka()

    def initVars(self):
        self.dm = DataModel()
        self.dm.clearAll()  # run this when using db for the first time
        # self.dm.saveAll() # use this when leaving the menu
        # self.dm.close() # use this at exit

    def setupUi(self):
        self.setGeometry(QtCore.QRect(100, 100, 500, 500))

        self.w = QtWidgets.QWidget(self)
        self.lay = QtWidgets.QVBoxLayout(self.w)

        self.setCentralWidget(self.w)

        # self.device_list_form = self.dm.getDeviceListAndForm(self.w)
        # self.lay.addWidget(self.device_list_form.widget)

        self.device_list_form = self.dm.getDeviceListAndForm(None)
        self.device_list_form.widget.show()

        # self.config_form = self.dm.getConfigForm()
        # self.config_form.widget.setParent(self.w)

    def openValkka(self):
        pass

    def closeValkka(self):
        pass

    def closeEvent(self, e):
        print("closeEvent!")
        self.closeValkka()
        e.accept()


def main():
    app = QtWidgets.QApplication(["test_app"])
    mg = MyGui()
    mg.show()
    app.exec_()


def test1():
    dm = DataModel()
    col = dm.camera_collection
    col.new(dm.RTSPCameraRow,
            {"slot"    : 1,
             "address" : "192.168.1.41",
             "username": "admin",
             "password": "1234",
             "port"    : "",
             "tail"    : "",
             "subaddress_main" : "",
             "live_main" : True,
             "rec_main"  : False,
             "subaddress_sub"  : "",
             "live_sub" : False,
             "rec_sub"  : False
                 })
            
    """
    "_id"       : int,
    "slot"      : int,
    "address"   : str,
    "username"  : str,
    "password"  : str,
    "port"      : (str, ""),
    "tail"      : (str, ""),
    "subaddress_main" : (str, ""),
    "live_main" : bool,
    "rec_main"  : bool,
    "subaddress_sub"  : (str, ""),
    "live_sub" : bool,
    "rec_sub"  : bool
    """
       
    for element in col.get():
        print(element)


def test2():
    dm = DataModel()
    for entry in dm.camera_collection.get():
        print(entry)
    
    devices_by_id = dm.getDevicesById({"classname" : DataModel.RTSPCameraRow.__name__})
    print(devices_by_id)
    
    
def test3():
    dm = DataModel(directory = tools.getConfigDir())
    dm.autoGenerateCameraCollection("192.168.1", 24, 100, "", "kokkelis/", "admin", "12345")
    dm.saveAll()
    dm.close()
    

if (__name__ == "__main__"):
    test1()
    # test3()
    
    
    
