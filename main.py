import os
import sys
import requests
from PyQt5.QtGui import QPixmap
import math
from PyQt5.QtWidgets import QMainWindow, QLabel, QApplication
from PyQt5 import uic
from PyQt5.QtCore import Qt


class MainWindow(QMainWindow):
    map_file = "map.png"

    def __init__(self):
        super(MainWindow, self).__init__()
        self.pos = "58.310022,51.194357"
        self.staticmap_url = "https://static-maps.yandex.ru/1.x/"
        self.scale = 19  # 'z' param in
        self.k = 1
        self.offset = 3
        self.image = None
        self.pixmap = None
        self.get_image()
        self.loadUI()

    def loadUI(self):
        uic.loadUi("map_v2.ui", self)
        self.setWindowTitle("Большая задача по Maps API. Часть №1")
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(800, 600)
        self.set_map()

    def set_map(self):
        self.pixmap = QPixmap(MainWindow.map_file)
        self.image.setPixmap(self.pixmap)

    def get_image(self):
        response = requests.get(url=self.staticmap_url,
                                params={"z": self.scale,
                                        "ll": self.pos,
                                        "l": "map",
                                        "size": "650,450"})
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
        self.pos = ",".join(str(i) for i in pos)
        self.update_image()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
