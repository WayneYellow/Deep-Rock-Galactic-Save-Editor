import json
from PyQt6.QtWidgets import QGridLayout, QLabel, QHBoxLayout, QMessageBox, QGroupBox, QWidget
from PyQt6 import QtCore, QtGui, QtWidgets
from PyQt6.QtCore import QSize, Qt
from PyQt6 import uic
from window import Ui_DeepRockGalaticSaveEditor
from PyQt6.QtWidgets import QFileDialog
import modules
from definitions import (GUID_RE, MAX_BADGES, PROMO_RANKS, RANK_TITLES, RESOURCE_GUIDS,
                                     SEASON_GUID, XP_PER_SEASON_LEVEL,
                                     XP_TABLE)
from typing import Any

class MainWindow(QtWidgets.QMainWindow, Ui_DeepRockGalaticSaveEditor):
    def __init__(self, *args, obj=None, **kwargs):
        super(MainWindow, self).__init__(*args, **kwargs)
        self.setupUi(self)
        self.setFixedSize(QSize(1000, 600))
        self.stackedWidget.setCurrentIndex(0)
        self.Handler = None

        self.pageButton = [self.resources, self.season, self.engineer, self.driller, self.gunner, self.scout]
        self.resources_box = {
            "yeast": self.yeast,
            "starch": self.starch,
            "barley": self.barley,
            "bismor": self.bismor,
            "enor": self.enor,
            "malt": self.malt,
            "umanite": self.umanite,
            "jadiz": self.jadiz,
            "croppa": self.croppa,
            "magnite": self.magnite,
            "error": self.error,
            "core": self.core,
            "data": self.data,
            "phazyonite": self.phazyonite,
            "credits": self.credits,
            "perks" : self.perks,
        }

        for button in self.pageButton:
            button.setEnabled(False)
            button.clicked.connect(self.page_button_was_clicked)
            button.setStyleSheet('''
                QPushButton{
                    background-color: rgb(17, 24, 39);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(255, 156, 0);
                }
                QPushButton:hover{
                    background-color: rgb(31, 41, 55);
                }
                QPushButton:Disabled{
                    gray
                }
            ''')
        self.clicked_button = None

        self.open_button.clicked.connect(self.open_file)
        self.save_button.clicked.connect(self.save_file)
        self.reset.clicked.connect(self.reset_data)

        self.layouts = {
            "Engineer" : self.engineer_layout,
            "Driller" : self.driller_layout,
            "Gunner" : self.gunner_layout,
            "Scout" : self.scout_layout,
        }

        stylesheet = '''
            QScrollBarArea{
                border: 0px;
            }
            QScrollBar:vertical
            {
                background : solid rgb(31,41,55);
            }

            QScrollBar::handle:vertical
            {
                background-color: rgb(255,156,0);
            }

            QScrollBar::groove:vertical
            {
                background-color: rgb(31,41,55);
            }
            '''
        #tempery disable save button
        self.save_button.setEnabled(False)

        
        self.scrollArea.setStyleSheet(stylesheet)
        self.scrollArea_3.setStyleSheet(stylesheet)
        self.scrollArea_4.setStyleSheet(stylesheet)
        self.scrollArea_5.setStyleSheet(stylesheet)
        self.scrollArea_6.setStyleSheet(stylesheet)
    
        self.scrollArea_3.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea_4.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea_5.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.scrollArea_6.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        with open("guids.json", "r") as g:
            self.guid_dict = json.loads(g.read())
        
        #init overclocks ui
        self.engineer_oc_list = []
        self.driller_oc_list = []
        self.gunner_oc_list = []
        self.scout_oc_list = []
        self.oc_buttons = []
        for key, value in self.guid_dict.items():
            oc_box = QWidget()
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(oc_box.sizePolicy().hasHeightForWidth())
            oc_box.setSizePolicy(sizePolicy)
            oc_box.setMinimumSize(QtCore.QSize(300, 62))
            oc_box.setStyleSheet('''
                QWidget{
                    background-color: rgb(17, 24, 39);
                    border: 2px solid rgb(255, 156, 0);
                    border-top-left-radius :7px;
                    border-top-right-radius : 7px;                  
                    border-bottom-left-radius : 7px;
                    border-bottom-right-radius : 7px;
                }
            ''')

            hbox = QHBoxLayout()

            icon_widget = QWidget()
            icon_widget.setFixedSize(40, 40)
            icon_widget.setStyleSheet(
                f"image: url(:/overclocks/overclock_icons/{value['name']} {value['class']}.png);"
                "background-color: rgb(36, 52, 84);"
                "border: 0px solid rgb(255, 156, 0);")
            hbox.addWidget(icon_widget)

            oc_label = QLabel(value["name"])
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Expanding, QtWidgets.QSizePolicy.Policy.Fixed)
            sizePolicy.setHorizontalStretch(1)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(oc_label.sizePolicy().hasHeightForWidth())
            oc_label.setSizePolicy(sizePolicy)
            oc_label.setMinimumHeight(25)
            font = QtGui.QFont()
            font.setFamily("Segoe UI Black")
            font.setPointSize(12)
            font.setBold(True)
            font.setWeight(75)
            oc_label.setFont(font)
            oc_label.setStyleSheet('''
                color:rgb(255, 255, 255);
                border: 0px;
                border-top-left-radius :0px;
                border-top-right-radius : 0px;                  
                border-bottom-left-radius : 0px;
                border-bottom-right-radius : 0px;
            ''')
            hbox.addWidget(oc_label, 1)

            unlock_button = QtWidgets.QPushButton()
            unlock_button.setObjectName(key)
            unlock_button.setCheckable(True)
            unlock_button.setChecked(False)
            sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Policy.Fixed, QtWidgets.QSizePolicy.Policy.Fixed)
            sizePolicy.setHorizontalStretch(0)
            sizePolicy.setVerticalStretch(0)
            sizePolicy.setHeightForWidth(unlock_button.sizePolicy().hasHeightForWidth())
            unlock_button.setSizePolicy(sizePolicy)
            unlock_button.setMinimumSize(QtCore.QSize(40, 40))
            unlock_button.setStyleSheet('''
                QPushButton{
                background-color: rgb(255, 156, 0);
                color: rgb(255, 255, 255);
                border: 2px solid rgb(255, 156, 0);
                border-top-left-radius :7px;
                border-top-right-radius : 7px;
                border-bottom-left-radius : 7px;
                border-bottom-right-radius : 7px;
                }
                QPushButton:hover{
                    background-color: rgb(255, 198, 106);
                    border: 2px solid rgb(255, 198, 106);
                }
            ''')
            icon1 = QtGui.QIcon()
            icon1.addPixmap(QtGui.QPixmap(f":/icons/locked.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
            unlock_button.setIcon(icon1)
            unlock_button.setIconSize(QtCore.QSize(35, 35))
            unlock_button.clicked.connect(self.uclock_button_was_clicked)
            hbox.addWidget(unlock_button)
            hbox.setAlignment(QtCore.Qt.AlignmentFlag.AlignCenter)
            oc_box.setLayout(hbox)
            if value["class"] == "Engineer":
                self.engineer_oc_list.append(oc_box)
            elif value["class"] == "Driller":
                self.driller_oc_list.append(oc_box)
            elif value["class"] == "Gunner":
                self.gunner_oc_list.append(oc_box)
            elif value["class"] == "Scout":
                self.scout_oc_list.append(oc_box)
            self.oc_buttons.append(unlock_button)
        #should do sorted by name here
        self.engineer_oc_list.sort(key=lambda x: x.layout().itemAt(1).widget().text())
        self.driller_oc_list.sort(key=lambda x: x.layout().itemAt(1).widget().text())
        self.gunner_oc_list.sort(key=lambda x: x.layout().itemAt(1).widget().text())
        self.scout_oc_list.sort(key=lambda x: x.layout().itemAt(1).widget().text())

        for value in self.engineer_oc_list:
            self.layouts["Engineer"].addWidget(value)
        for value in self.driller_oc_list:
            self.layouts["Driller"].addWidget(value)
        for value in self.gunner_oc_list:
            self.layouts["Gunner"].addWidget(value)
        for value in self.scout_oc_list:
            self.layouts["Scout"].addWidget(value)


    def open_file(self):
        steam_path = modules.findSteamPath()
        self.file_name = QFileDialog.getOpenFileName(
            None,
            "Open Save File...",
            steam_path,
            "Player Save Files (*.sav);;All Files (*.*)",
        )[0]
        try:
            save_file = modules.load_save_file(self.file_name)
            for button in self.pageButton:
                button.setEnabled(True)
            self.stackedWidget.setCurrentIndex(1)
            self.Handler = modules.SaveDataHandler(save_file)
            self.save_button.setEnabled(True)
            self.reset_data()
        except:
            pass
        

    def reset_data(self):
        self.Handler.init_values()
        data = self.Handler.state
        #season
        season_total_xp = data["season"]["xp"]
        self.seasonXPBox.setValue(season_total_xp % XP_PER_SEASON_LEVEL)
        self.seasonLvlBox.setValue(season_total_xp // XP_PER_SEASON_LEVEL)
        self.scripBox.setValue(data["season"]["scrip"])
        #resources
        for key, value in self.resources_box.items():
            value.setValue(data["resources"][key])
        #dwarves
        lv_xp = self.xp_total_to_level(data["xp"]["engineer"]["xp"])
        self.engineer_lvl.setValue(lv_xp[0])
        self.engineer_xp.setValue(lv_xp[1])
        self.engineer_promotion.setCurrentIndex(
            data["xp"]["engineer"]["promo"]
            if data["xp"]["engineer"]["promo"] < MAX_BADGES
            else MAX_BADGES
        )
        
        lv_xp = self.xp_total_to_level(data["xp"]["driller"]["xp"])
        self.driller_lvl.setValue(lv_xp[0])
        self.driller_xp.setValue(lv_xp[1])
        self.driller_promotion.setCurrentIndex(
            data["xp"]["driller"]["promo"]
            if data["xp"]["driller"]["promo"] < MAX_BADGES
            else MAX_BADGES
        )

        lv_xp = self.xp_total_to_level(data["xp"]["gunner"]["xp"])
        self.gunner_lvl.setValue(lv_xp[0])
        self.gunner_xp.setValue(lv_xp[1])
        self.gunner_promotion.setCurrentIndex(
            data["xp"]["gunner"]["promo"]
            if data["xp"]["gunner"]["promo"] < MAX_BADGES
            else MAX_BADGES
        )

        lv_xp = self.xp_total_to_level(data["xp"]["scout"]["xp"])
        self.scout_lvl.setValue(lv_xp[0])
        self.scout_xp.setValue(lv_xp[1])
        self.scout_promotion.setCurrentIndex(
            data["xp"]["scout"]["promo"]
            if data["xp"]["scout"]["promo"] < MAX_BADGES
            else MAX_BADGES
        )
        # print(data["overclocks"]["unacquired"])
        # print(data["overclocks"]["unforged"])
        #reset overclocks
        #set froged overclocks icon to unlock
        for i in self.oc_buttons:
            if self.Handler.state["overclocks"]["all"][i.objectName()]["status"] == "Forged":
                i.setIcon(QtGui.QIcon(f":/icons/unlock.png"))
                i.setChecked(True)
            elif self.Handler.state["overclocks"]["all"][i.objectName()]["status"] == "Unforged":
                i.setIcon(QtGui.QIcon(f":/icons/unlock.png"))
                i.setChecked(True)
            elif self.Handler.state["overclocks"]["all"][i.objectName()]["status"] == "Unacquired":
                i.setIcon(QtGui.QIcon(f":/icons/locked.png"))
                i.setChecked(False)


    def xp_total_to_level(self, xp: int) -> tuple[int, int]:
        for i in XP_TABLE:
            if xp < i:
                level: int = XP_TABLE.index(i)
                remainder: int = xp - XP_TABLE[level - 1]
                return (level, remainder)
        return (25, 0)
    # switch between pages
    def page_button_was_clicked(self):
        for button in self.pageButton:
            button.setStyleSheet('''
                QPushButton{
                    background-color: rgb(17, 24, 39);
                    color: rgb(255, 255, 255);
                    border: 2px solid rgb(255, 156, 0);
                }
                QPushButton:hover{
                    background-color: rgb(31, 41, 55);
                }
            ''')
            if self.sender() == button:
                self.stackedWidget.setCurrentIndex(self.pageButton.index(button)+1)
                self.clicked_button = button
                self.clicked_button.setStyleSheet('''
                    QPushButton{
                        background-color: rgb(31, 41, 55);
                        color: rgb(255, 255, 255);
                        border: 2px solid rgb(255, 156, 0);
                    }
                    QPushButton:hover{
                        background-color: rgb(31, 41, 55);
                    }
                ''')
    
    def uclock_button_was_clicked(self):
        #chang icon
        if self.Handler.state["overclocks"]["all"][self.sender().objectName()]["status"] == "Unacquired":
            if self.sender().isChecked():
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(f":/icons/unlock.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
                self.sender().setIcon(icon)
                temp = self.Handler.state["overclocks"]["unacquired"][self.sender().objectName()]
                del self.Handler.state["overclocks"]["unacquired"][self.sender().objectName()]
                self.Handler.state["overclocks"]["unforged"][self.sender().objectName()] = temp
                self.Handler.state["overclocks"]["unforged"][self.sender().objectName()]["status"] = "Unforged"
            else:
                icon = QtGui.QIcon()
                icon.addPixmap(QtGui.QPixmap(f":/icons/locked.png"), QtGui.QIcon.Mode.Normal, QtGui.QIcon.State.Off)
                self.sender().setIcon(icon)
                temp = self.Handler.state["overclocks"]["unforged"][self.sender().objectName()]
                del self.Handler.state["overclocks"]["unforged"][self.sender().objectName()]
                self.Handler.state["overclocks"]["unacquired"][self.sender().objectName()] = temp
                self.Handler.state["overclocks"]["unacquired"][self.sender().objectName()]["status"] = "Unacquired"
        

    def save_file(self):
        changes: dict[str, Any] = self.get_values(self.Handler.state)
        changes['overclocks'] = dict()
        changes['overclocks']['unforged'] = self.Handler.state['overclocks']['unforged']
        changes['overclocks']['all'] = self.Handler.state['overclocks']['all']
        changes['overclocks']['unacquired'] = self.Handler.state['overclocks']['unacquired']
        self.Handler.save_changes(changes, self.file_name)
        dlg = QMessageBox(self)
        dlg.setWindowTitle("Saved")
        dlg.setText("Saved successfully!")
        dlg.setStyleSheet('''
            QMessageBox{
                color: white;
            }
            QMessageBox QLabel{
                color: white;
            }
            QMessageBox QPushButton{
                background-color: black;
                color: white;
            }
        ''')
        button = QMessageBox.StandardButton.Close
        dlg.setStandardButtons(button)
        dlg.setIcon(QMessageBox.Icon.Information)
        dlg.exec()


    # get value from ui input
    def get_values(self, state) -> dict[str, Any]:

        ns: dict[str, Any] = dict()
        ns["resources"] = dict()
        ns["xp"] = {
            "driller": dict(),
            "gunner": dict(),
            "scout": dict(),
            "engineer": dict(),
        }


        for key, box in self.resources_box.items():
            ns["resources"][key] = box.value()
        
        
        ns["xp"]["driller"]["xp"] = self.driller_xp.value()
        ns["xp"]["engineer"]["xp"] = self.engineer_xp.value()
        ns["xp"]["gunner"]["xp"] = self.gunner_xp.value()
        ns["xp"]["scout"]["xp"] = self.scout_xp.value()

        driller_promo = int(self.driller_promotion.currentIndex())
        gunner_promo = int(self.gunner_promotion.currentIndex())
        scout_promo = int(self.scout_promotion.currentIndex())
        engineer_promo = int(self.engineer_promotion.currentIndex())

        ns["xp"]["driller"]["promo"] = (
            driller_promo if driller_promo < MAX_BADGES else self.Handler.state["xp"]["driller"]["promo"]
        )
        ns["xp"]["engineer"]["promo"] = (
            engineer_promo
            if engineer_promo < MAX_BADGES
            else self.Handler.state["xp"]["engineer"]["promo"]
        )
        ns["xp"]["gunner"]["promo"] = (
            gunner_promo if gunner_promo < MAX_BADGES else self.Handler.state["xp"]["gunner"]["promo"]
        )
        ns["xp"]["scout"]["promo"] = (
            scout_promo if scout_promo < MAX_BADGES else self.Handler.state["xp"]["scout"]["promo"]
        )

        ns["season"] = {
            "xp": int(self.seasonXPBox.value())
            + (XP_PER_SEASON_LEVEL * int(self.seasonLvlBox.value())),
            "scrip": int(self.scripBox.value()),
        }

        return ns
