import os
import sys
import requests
from PyQt5.QtGui import QPixmap, QColor, QKeyEvent
from gui import Ui_main_window
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication
from PyQt5 import uic
from PyQt5.QtCore import Qt, QEvent


def except_hook(cls, exception, traceback):
    sys.__excepthook__(cls, exception, traceback)


class MainWindow(QMainWindow, Ui_mainWindow):
    map_file = "map.png"

    def __init__(self):
        super().__init__()
        self.pos = "58.310022,51.194357"
        self.setupUi(self)
        self.setup_buttons()
        self.staticmap_url = "https://static-maps.yandex.ru/1.x/"
        self.search_url = "https://search-maps.yandex.ru/v1/"
        self.scale = 19  # 'z' param in
        self.map_type = "map"
        self.map_params = {"z": self.scale,
                           "ll": self.pos,
                           "l": self.map_type,
                           "size": "650,450"}
        self.mark = None
        self.k = 1
        self.offset = 3

        self.image = None
        self.pixmap = None
        self.move_from_scale = {
            19: 0.0001,
            18: 0.0002,
            17: 0.0003,
            16: 0.0004,
            15: 0.001,
            14: 0.002,
            13: 0.003,
            12: 0.004,
            11: 0.005,
            10: 0.04,
            9: 0.06,
            8: 0.08,
            7: 0.1,
            6: 0.3,
            5: 0.5,
            4: 0.7,
            3: 0.9,
            2: 1,
            1: 1
        }
        self.get_image()
        self.loadUi()

    def loadUi(self):
        self.setWindowTitle("Большая задача по Maps API. Часть №1")
        self.image = self.label
        self.set_map()

    def setup_buttons(self):
        self.map_btn.clicked.connect(lambda: self.change_map_type("map"))
        self.sput_btn.clicked.connect(lambda: self.change_map_type("sat"))
        self.gibr_btn.clicked.connect(lambda: self.change_map_type("skl"))
        self.pushButton.clicked.connect(self.delete_mark)

        self.lineEdit.editingFinished.connect(self.find_object)

    def delete_mark(self):
        self.map_params.pop("pt", "")
        self.mark = None
        self.update_image()

    def find_object(self):
        name = self.lineEdit.text()
        if name == "": return
        params = {"text": name,
                  "lang": "ru_RU",
                  "apikey": 'dda3ddba-c9ea-4ead-9010-f43fbc15c6e3'}
        response = requests.get(self.search_url, params)
        if not response: return
        json_response = response.json()

        obj = json_response["features"][0]

        point = obj["geometry"]["coordinates"]
        org_point = "{0},{1}".format(point[0], point[1])
        self.pos = org_point
        self.mark = org_point
        self.update_image()

    def change_map_type(self, typ):
        self.map_type = typ
        self.update_image()

    def set_map_params(self):
        self.map_params = {"z": self.scale,
                           "ll": self.pos,
                           "l": self.map_type,
                           "size": "650,450"}
        if self.mark:
            self.map_params["pt"] = self.mark

    def set_map(self):
        self.pixmap = QPixmap(MainWindow.map_file)
        color = self.pixmap.toImage().pixelColor(0, 0)
        if color == QColor("#BEBEBE"):
            print(QEvent.KeyPress)
            self.keyPressEvent(event=QKeyEvent(
                QEvent.Type(6), self.last_move_back,
                Qt.KeyboardModifier.NoModifier),
                is_real_event=False)
            return
        self.image.setPixmap(self.pixmap)

    def get_image(self):
        response = requests.get(url=self.staticmap_url,
                                params=self.map_params)
        if not response:
            print("Ошибка выполнения запроса:")
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason,
                  ")")
            print(response.text)
            sys.exit(1)

        with open(MainWindow.map_file, "wb") as file:
            file.write(response.content)

    def update_image(self):
        self.set_map_params()
        self.get_image()
        self.set_map()
        self.update()

    def closeEvent(self, event):
        os.remove(MainWindow.map_file)

    def keyPressEvent(self, event, is_real_event=True):
        self.last_move_back = 0
        if event.key() == Qt.Key_PageUp:
            self.scale += 1
            if self.scale > 23:
                self.scale = 23
            self.last_move_back = Qt.Key_PageDown
        elif event.key() == Qt.Key_PageDown:
            self.scale -= 1
            if self.scale < 1:
                self.scale = 1
            self.last_move_back = Qt.Key_Up
        elif event.key() == Qt.Key_Up:
            self.pos[1] = self.pos[1] + self.move_from_scale[self.scale]
            self.last_move_back = Qt.Key_Down
        elif event.key() == Qt.Key_Down:
            self.pos[1] = self.pos[1] - self.move_from_scale[self.scale]
            self.last_move_back = Qt.Key_Up
        elif event.key() == Qt.Key_Left:
            self.pos[0] = self.pos[0] - self.move_from_scale[self.scale]
            self.last_move_back = Qt.Key_Right
        elif event.key() == Qt.Key_Right:
            self.pos[0] = self.pos[0] + self.move_from_scale[self.scale]
            self.last_move_back = Qt.Key_Left
        if is_real_event:
            self.update_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.excepthook = except_hook
    sys.exit(app.exec())
