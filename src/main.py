from PyQt6.QtWidgets import QApplication
import ui
from modules import QSSLoader

app = QApplication([])
window = ui.MainWindow()

# style_file = './style.qss'
# style_sheet = QSSLoader.read_qss_file(style_file)
# window.setStyleSheet(style_sheet)

window.show()
app.exec()
