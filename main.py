import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QSystemTrayIcon, QMenu, QAction, QHBoxLayout
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QSettings, QByteArray, QTimer, QEvent
import requests
import webbrowser


# 获取天气API数据
def get_weather_data(api_key, location):
    url = f"https://devapi.qweather.com/v7/weather/now?location={location}&key={api_key}"
    response = requests.get(url)
    return response.json()


# 根据天气状况加载对应图标
def load_weather_icon(icon_code):
    # 这里假设你已经从GitHub下载并组织好图片资源，icon_code对应实际图片文件名
    icon_path = f'icons-64/{icon_code}.png'  # 替换为实际图标路径
    pixmap = QPixmap(icon_path)
    return pixmap


class WeatherWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("setting.ini", QSettings.IniFormat)
        self.start_pos = None
        self.init_ui()

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_weather)
        self.timer.start(1800 * 1000)  # 每1800秒触发一次

        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.tray_icon = QSystemTrayIcon(self)
        self.create_tray_menu()

        # 从配置中加载窗口位置
        self.restoreGeometry(self.settings.value("window_geometry", QByteArray()))

        # 安装全局事件过滤器以捕获窗口的鼠标双击事件
        self.installEventFilter(self)

    def eventFilter(self, obj, event):
        if event.type() == QEvent.MouseButtonDblClick:
            if event.button() == Qt.LeftButton:  # 只处理左键双击事件
                url = f'http://www.weather.com.cn/weather1d/{self.settings.value("location")}.shtml'  # 替换为你要打开的实际网址
                webbrowser.open(url, new=2)
                return True

        return super(WeatherWidget, self).eventFilter(obj, event)

    def update_weather(self):
        print("开始更新天气")
        api_key = self.settings.value("api_key")
        location = self.settings.value("location")
        weather_data = get_weather_data(api_key, location)
        now = weather_data['now']
        self.text_label.setText(f"{now['text']}\n"
                                f"{now['temp']}℃")
        self.text_label.setStyleSheet("color: white;")

        icon_code = now['icon']
        icon_pixmap = load_weather_icon(icon_code)
        print("icon", icon_code)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(icon_pixmap)

    def init_ui(self):
        self.setWindowTitle('实时天气')

        # 假设已获取到API key和地点信息
        api_key = self.settings.value("api_key")
        location = self.settings.value("location")

        weather_data = get_weather_data(api_key, location)
        now = weather_data['now']

        # 显示天气文字
        self.text_label = QLabel(f"{now['text']}\n"
                                 f"{now['temp']}℃")
        self.text_label.setStyleSheet("color: white;")

        # 加载并显示天气图标
        icon_code = now['icon']
        icon_pixmap = load_weather_icon(icon_code)
        print("icon", icon_code)
        self.icon_label = QLabel()
        self.icon_label.setPixmap(icon_pixmap)

        hb_layout = QHBoxLayout()

        layout = QVBoxLayout()
        # 天气信息布局部分保持不变...
        hb_layout.addWidget(self.icon_label)
        hb_layout.addWidget(self.text_label)
        hb_layout.addStretch()
        layout.addLayout(hb_layout)
        self.setLayout(layout)
        self.resize(int(self.settings.value("w")), int(self.settings.value("h")))

    def create_tray_menu(self):
        tray_menu = QMenu()
        show_action = QAction('&打开配置文件', self, triggered=self.showNormal)
        quit_action = QAction('&退出', self, triggered=self.close)
        tray_menu.addAction(show_action)
        tray_menu.addSeparator()
        tray_menu.addAction(quit_action)

        self.tray_icon.setIcon(QIcon('icons-64/100.png'))
        self.tray_icon.setToolTip('实时天气')
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.show()

        self.hide()  # 程序启动时隐藏主窗口，只在托盘显示

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.start_pos = event.pos()

    def mouseMoveEvent(self, event):
        if not self.start_pos:
            return

        if event.buttons() == Qt.LeftButton:
            diff = event.pos() - self.start_pos
            new_pos = self.pos() + diff
            self.move(new_pos)

    def closeEvent(self, event):
        # 保存窗口位置到配置文件

        self.settings.setValue("window_geometry", self.saveGeometry())
        print("保存窗口信息")

        self.tray_icon.hide()
        QApplication.quit()


if __name__ == "__main__":
    app = QApplication(sys.argv)

    widget = WeatherWidget()
    widget.show()
    # 当程序退出时也保存窗口位置
    app.aboutToQuit.connect(widget.close)
    sys.exit(app.exec_())
