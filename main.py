import os
import sys
import requests
from PyQt5.QtGui import QPixmap

from PyQt5.QtWidgets import QWidget, QMainWindow, QLabel, QApplication
from PyQt5 import uic


class MainWindow(QMainWindow):
    pos = "58.310022,51.194357"
    staticmap_url = "https://static-maps.yandex.ru/1.x/"
    scale = 19  # 'z' param in api
    map_file = "map.png"

    def __init__(self):
        super(MainWindow, self).__init__()
        self.image = None
        self.pixmap = None
        self.get_image()
        self.loadUI()

    def loadUI(self):
        uic.loadUi("map_v1.ui", self)
        self.setWindowTitle("Большая задача по Maps API. Часть №1")
        self.pixmap = QPixmap(self.map_file)
        self.image = QLabel(self)
        self.image.move(0, 0)
        self.image.resize(800, 600)
        self.image.setPixmap(self.pixmap)

    def get_image(self):
        response = requests.get(url=MainWindow.staticmap_url,
                                params={"z": MainWindow.scale,
                                        "ll": MainWindow.pos,
                                        "l": "map"})
        if not response:
            print("Ошибка выполнения запроса:")
            print(response.url)
            print("Http статус:", response.status_code, "(", response.reason,
                  ")")
            print(response.text)
            sys.exit(1)

        with open(MainWindow.map_file, "wb") as file:
            file.write(response.content)

    def closeEvent(self, event):
        os.remove(MainWindow.map_file)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = MainWindow()
    ex.show()
    sys.exit(app.exec())
