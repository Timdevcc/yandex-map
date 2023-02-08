import os
import sys
import requests
from PyQt5.QtGui import QPixmap
from gui import Ui_mainWindow
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication
from PyQt5.QtCore import Qt


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
        self.sender().clearFocus()
        self.map_params.pop("pt", "")
        self.mark = None
        self.update_image()

    def find_object(self):
        self.lineEdit.clearFocus()
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
        self.sender().clearFocus()
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

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_PageUp:
            self.scale += 1
            if self.scale > 23:
                self.scale = 23
            self.k -= 0.6
        elif event.key() == Qt.Key_PageDown:
            self.scale -= 1
            if self.scale < 1:
                self.scale = 1
            self.k += 0.6

        pos = [float(i) for i in self.pos.split(",")]
        if event.key() == Qt.Key_Up:
            pos[1] += self.offset ** self.k * 0.0001
        elif event.key() == Qt.Key_Down:
            pos[1] -= self.offset ** self.k * 0.0001
        elif event.key() == Qt.Key_Left:
            pos[0] -= self.offset ** self.k * 0.0001
        elif event.key() == Qt.Key_Right:
            pos[0] += self.offset ** self.k * 0.0001
        print(pos)
        if 0 < pos[0] < 90 and 0 < pos[1] < 90:
            self.pos = ",".join(str(i) for i in pos)

        self.update_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
