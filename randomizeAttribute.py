moduleName = 'randomizeAttribute'
moduleNameLong = 'Randomize Selected Attributes'
moduleUrl = 'https://github.com/PrewizardsStudio/randomize-attribute'
moduleIconUrl = 'https://github.com/PrewizardsStudio/randomize-attribute/blob/main/randomizeAttribute.png?raw=true'
moduleCommand = """
import maya.cmds as cmds
import maya.mel as mel
import os

def initQT():
    import maya.OpenMayaUI as mui
    import imp
    try:
        imp.find_module('PySide')
        from PySide import QtGui, QtCore
        from preDevelopment.Qt.Qt import QtWidgets
        from PySide.phonon import Phonon
        from shiboken import wrapInstance
        sip = None
    except ImportError:
        try:
            imp.find_module('PySide2')
            from PySide2 import QtGui, QtWidgets, QtCore
            from PySide2.QtWidgets import QAction
            from shiboken2 import wrapInstance
            Phonon = None
            sip = None
        except ImportError:
            imp.find_module('PySide6')
            from PySide6 import QtGui, QtWidgets, QtCore
            from PySide6.QtGui import QAction
            from shiboken6 import wrapInstance
            Phonon = None
            sip = None    
    except ImportError:
        from PyQt4 import QtGui, QtCore
        from preDevelopment.Qt.Qt import QtWidgets
        from PyQt4.phonon import Phonon
        import sip
        wrapInstance = None
    return mui, imp, QtGui, QtCore, QtWidgets, Phonon, wrapInstance, sip, QAction

mui, imp, QtGui, QtCore, QtWidgets, Phonon, wrapInstance, sip, QAction = initQT()

def getMainWindow(mui, imp, QtGui, QtCore, QtWidgets, Phonon, wrapInstance, sip):
    main_window_ptr = mui.MQtUtil.mainWindow()
    try:
        imp.find_module('PySide')
        mainWin = wrapInstance(long(main_window_ptr), QtGui.QWidget)
    except ImportError:
        #imp.find_module('PySide2')
        import sys
        if sys.version_info[0] < 3:
            mainWin = wrapInstance(long(main_window_ptr), QtWidgets.QWidget)  
        else:            
            mainWin = wrapInstance(int(main_window_ptr), QtWidgets.QWidget) 
    except ImportError:
        mainWin = sip.wrapinstance(long(main_window_ptr), QtCore.QObject)
    return mainWin

class randomizeAttribute(QtWidgets.QMainWindow):
    def closeExistingWindow(self):
        for qt in QtWidgets.QApplication.topLevelWidgets():
            try:
                if qt.__class__.__name__ == self.__class__.__name__:
                    #pass
                    qt.close()
            except:
                pass

    def __init__(self, parent = getMainWindow(mui, imp, QtGui, QtCore, QtWidgets, Phonon, wrapInstance, sip)):        
        self.closeExistingWindow()
        QtWidgets.QMainWindow.__init__(self, parent)
        self.initUI()

    def initUI(self):        
        # create window
        self.setWindowTitle('Randomize Attributes')    
        self.setFixedSize(260, 120)
        self.statusBar().setSizeGripEnabled(False)
        self.centerWidget = QtWidgets.QWidget()
        self.layout = QtWidgets.QGridLayout() 
        
        # create checkboxes
        self.rangeChkBox = QtWidgets.QCheckBox("Range")
        self.rangeChkBox.setChecked(True)
        self.rangeChkBox.stateChanged.connect(self.checkRange)
        self.relativeChkBox = QtWidgets.QCheckBox("Relative Offset")
        self.relativeChkBox.setChecked(False) 
        
        self.onlyFloat = QtGui.QDoubleValidator()        
        
        self.rangeMinLine = QtWidgets.QLineEdit()
        self.rangeMinLine.setValidator(self.onlyFloat)
        self.rangeMinLine.setText('0.0')
        
        self.rangeMaxLine = QtWidgets.QLineEdit()
        self.rangeMaxLine.setValidator(self.onlyFloat)
        self.rangeMaxLine.setText('1.0')
        
        # create randomize button
        self.randomizeButton = QtWidgets.QPushButton()
        self.randomizeButton.clicked.connect(self.buttonCommand)
        self.randomizeButton.setToolTip('Randomize Selected Channel Box Attributes')

        self.randomizeButton.setIcon(QtGui.QIcon(os.path.join(os.environ['MAYA_APP_DIR'], cmds.about(version=True), "prefs/icons/randomizeAttribute.png")))
        self.randomizeButton.setIconSize(QtCore.QSize(80,80))        
        
        self.layout.addWidget(self.rangeChkBox, 0, 0)
        self.layout.addWidget(self.rangeMinLine, 0, 1)
        self.layout.addWidget(self.rangeMaxLine, 0, 2)
        self.layout.addWidget(self.randomizeButton, 0, 3, 2, 1)
        self.layout.addWidget(self.relativeChkBox, 1, 0, 1, 2)
                
        self.centerWidget.setLayout(self.layout)
        self.setCentralWidget(self.centerWidget)  
        
        self.statusBar().setSizeGripEnabled(False)
        self.statusBar().showMessage("Select objects and attributes from channel box")
        
        self.show()      
    
    def checkRange(self):
        if self.rangeChkBox.isChecked():
            self.rangeMinLine.setEnabled(True)
            self.rangeMaxLine.setEnabled(True)
        else:
            self.rangeMinLine.setEnabled(False)
            self.rangeMaxLine.setEnabled(False)
    
    def getSelectedChannleBoxAttributes(self):
        channelBox = mel.eval('global string $gChannelBoxName; $temp=$gChannelBoxName;')    
        selectedNode = cmds.channelBox(channelBox, mainObjectList=True, query=1)
        selectedMainAttr = cmds.channelBox(channelBox, selectedMainAttributes=True, query=1)
        if selectedMainAttr:
            return selectedNode, selectedMainAttr
        else:
            selectedHistoryNode = cmds.channelBox(channelBox, query=1, historyObjectList=1)
            selectedHistoryAttr = cmds.channelBox(channelBox, selectedHistoryAttributes=True, query=1)
            return selectedHistoryNode, selectedHistoryAttr
    
    def buttonCommand(self):
        selectedNodes = cmds.ls(sl = True)
        n, selectedAttr = self.getSelectedChannleBoxAttributes()
        if selectedNodes == []:
            self.statusBar().setStyleSheet('QStatusBar {color: rgb(255, 0, 0)}')
            self.statusBar().showMessage('Select an object')
        elif not selectedAttr:
            self.statusBar().setStyleSheet('QStatusBar {color: rgb(255, 0, 0)}')
            self.statusBar().showMessage('Select attributes from channel box')
        else:
            self.statusBar().showMessage('')
            if self.rangeChkBox.isChecked():
                range = [float(self.rangeMinLine.text()), float(self.rangeMaxLine.text())]
            else:
                range = None
            if self.relativeChkBox.isChecked():
                relative = True
            else:
                relative = False      
            for node in selectedNodes:            
                for attr in selectedAttr:    
                    self.randomAttribute(node, attr, range=range, relative=relative) 
    
    def getAttributeRange(self, node, attribute):
        try:
            return cmds.attributeQuery(attribute, node=node, range=1)
        except:
            return None
    
    def randomAttribute(self, node, attribute, range=None, relative=False):
        import math
        
        if cmds.attributeQuery(attribute, node=node, exists=True):
            import random
            if range == None:
                queryRange = self.getAttributeRange(node, attribute)
                if queryRange:
                    range = queryRange 
                else:
                    self.statusBar().setStyleSheet('QStatusBar {color: rgb(255, 0, 0)}')
                    self.statusBar().showMessage('You shoud define range!')
                    return
            attributeType = cmds.attributeQuery(attribute, node=node, attributeType=True)
            if attributeType in ['doubleLinear', 'double', 'doubleAngle']: #float
                randomResult = random.uniform(range[0], range[1])
            elif attributeType in ['long', 'bool', 'enum']: #int
                randomResult = random.randint(range[0], range[1])
            elif attributeType in ['typed']:
                cmds.error("Can't randomize " + attribute +  ' because it is ' +  attributeType + ' type')
            if relative:
                cmds.setAttr(node + '.'  + attribute, cmds.getAttr(node + '.'  + attribute) + randomResult)
            else:
                cmds.setAttr(node + '.'  + attribute, randomResult)
     
myRandomizeAttribute = randomizeAttribute()
"""

def onMayaDroppedPythonFile(args):
    import sys
    del sys.modules[moduleName]
    installScript()
    
def installScript():
    import requests, os
    import maya.mel as mel
    import maya.cmds as cmds

    iconImageName = moduleIconUrl.split('/')[-1].replace('?raw=true','')

    # Get current maya version
    version = cmds.about(version=True)

    # Download Icon
    appPath = os.environ['MAYA_APP_DIR']
    iconPath = os.path.join(appPath, version, "prefs/icons", iconImageName)

    if not os.path.exists(iconPath):
        result = requests.get(moduleIconUrl, allow_redirects=True)
        open(iconPath, 'wb').write(result.content)  

    # Add to current shelf
    topShelf = mel.eval('$nul = $gShelfTopLevel')
    currentShelf = cmds.tabLayout(topShelf, q=1, st=1)
    cmds.shelfButton(parent=currentShelf, image=iconPath, command=moduleCommand, label=moduleNameLong, annotation=moduleNameLong)