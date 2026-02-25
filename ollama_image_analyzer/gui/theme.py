"""Modern dark theme stylesheet for Ollama Image Analyzer.

Beautiful, polished dark theme with rounded corners and clean typography.
"""

DARK_THEME = """
/* ===== Global Styles ===== */
QWidget {
    background-color: #1e1e2e;
    color: #cdd6f4;
    font-family: "Segoe UI", "SF Pro Display", "Helvetica Neue", Arial, sans-serif;
    font-size: 10pt;
}

/* ===== Main Window ===== */
QMainWindow {
    background-color: #181825;
}

/* ===== Buttons ===== */
QPushButton {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    min-height: 24px;
}

QPushButton:hover {
    background-color: #3d3f54;
    border-color: #585b70;
}

QPushButton:pressed {
    background-color: #292a3d;
    border-color: #6c7086;
}

QPushButton:disabled {
    background-color: #242435;
    color: #6c7086;
    border-color: #313244;
}

QPushButton#primaryButton {
    background-color: #89b4fa;
    color: #1e1e2e;
    border: none;
    font-weight: 600;
}

QPushButton#primaryButton:hover {
    background-color: #a6c9ff;
}

QPushButton#primaryButton:pressed {
    background-color: #6a95d6;
}

QPushButton#primaryButton:disabled {
    background-color: #45475a;
    color: #6c7086;
}

QPushButton#dangerButton {
    background-color: #f38ba8;
    color: #1e1e2e;
    border: none;
}

QPushButton#dangerButton:hover {
    background-color: #ffa8c0;
}

QPushButton#successButton {
    background-color: #a6e3a1;
    color: #1e1e2e;
    border: none;
}

/* ===== Text Edits ===== */
QTextEdit, QPlainTextEdit {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px;
    selection-background-color: #585b70;
    selection-color: #cdd6f4;
}

QTextEdit:focus, QPlainTextEdit:focus {
    border-color: #89b4fa;
}

/* ===== Line Edits ===== */
QLineEdit {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 8px 12px;
    selection-background-color: #585b70;
}

QLineEdit:focus {
    border-color: #89b4fa;
}

QLineEdit:disabled {
    background-color: #181825;
    color: #6c7086;
}

/* ===== Combo Boxes ===== */
QComboBox {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 12px;
    min-height: 24px;
}

QComboBox:hover {
    border-color: #585b70;
}

QComboBox:focus {
    border-color: #89b4fa;
}

QComboBox::drop-down {
    border: none;
    width: 20px;
}

QComboBox::down-arrow {
    image: none;
    border-left: 4px solid transparent;
    border-right: 4px solid transparent;
    border-top: 6px solid #cdd6f4;
    margin-right: 6px;
}

QComboBox QAbstractItemView {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    selection-background-color: #585b70;
    selection-color: #cdd6f4;
    border-radius: 6px;
    padding: 4px;
}

/* ===== Labels ===== */
QLabel {
    background-color: transparent;
    color: #cdd6f4;
}

QLabel#titleLabel {
    font-size: 14pt;
    font-weight: 600;
    color: #89b4fa;
}

QLabel#subtitleLabel {
    font-size: 9pt;
    color: #a6adc8;
}

QLabel#errorLabel {
    color: #f38ba8;
}

QLabel#successLabel {
    color: #a6e3a1;
}

QLabel#statusLabel {
    font-size: 10pt;
    font-weight: 500;
    color: #cdd6f4;
}

/* ===== Status Panel ===== */
QWidget#statusPanel {
    background-color: #181825;
    border: 1px solid #45475a;
    border-radius: 8px;
}

/* ===== Group Boxes ===== */
QGroupBox {
    background-color: #1e1e2e;
    border: 1px solid #45475a;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 16px;
    font-weight: 600;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 4px 8px;
    color: #89b4fa;
}

/* ===== Dialogs ===== */
QDialog {
    background-color: #1e1e2e;
}

/* ===== Scroll Bars ===== */
QScrollBar:vertical {
    background-color: #1e1e2e;
    width: 12px;
    border-radius: 6px;
}

QScrollBar::handle:vertical {
    background-color: #45475a;
    border-radius: 6px;
    min-height: 20px;
}

QScrollBar::handle:vertical:hover {
    background-color: #585b70;
}

QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
    height: 0px;
}

QScrollBar:horizontal {
    background-color: #1e1e2e;
    height: 12px;
    border-radius: 6px;
}

QScrollBar::handle:horizontal {
    background-color: #45475a;
    border-radius: 6px;
    min-width: 20px;
}

QScrollBar::handle:horizontal:hover {
    background-color: #585b70;
}

QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {
    width: 0px;
}

/* ===== Progress Bar ===== */
QProgressBar {
    background-color: #1e1e2e;
    border: 1px solid #45475a;
    border-radius: 6px;
    text-align: center;
    color: #cdd6f4;
    height: 20px;
}

QProgressBar::chunk {
    background-color: #89b4fa;
    border-radius: 5px;
}

/* ===== Splitter ===== */
QSplitter::handle {
    background-color: #313244;
}

QSplitter::handle:horizontal {
    width: 2px;
}

QSplitter::handle:vertical {
    height: 2px;
}

QSplitter::handle:hover {
    background-color: #89b4fa;
}

/* ===== Tool Tips ===== */
QToolTip {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 4px;
    padding: 4px 8px;
}

/* ===== Menu Bar ===== */
QMenuBar {
    background-color: #181825;
    color: #cdd6f4;
    border-bottom: 1px solid #313244;
    padding: 4px;
}

QMenuBar::item {
    background-color: transparent;
    padding: 6px 12px;
    border-radius: 4px;
}

QMenuBar::item:selected {
    background-color: #313244;
}

QMenuBar::item:pressed {
    background-color: #45475a;
}

/* ===== Menus ===== */
QMenu {
    background-color: #313244;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 4px;
}

QMenu::item {
    padding: 6px 24px 6px 12px;
    border-radius: 4px;
}

QMenu::item:selected {
    background-color: #585b70;
}

QMenu::separator {
    height: 1px;
    background-color: #45475a;
    margin: 4px 8px;
}

/* ===== Status Bar ===== */
QStatusBar {
    background-color: #181825;
    color: #a6adc8;
    border-top: 1px solid #313244;
}

/* ===== Tab Widget ===== */
QTabWidget::pane {
    border: 1px solid #45475a;
    border-radius: 6px;
    background-color: #1e1e2e;
}

QTabBar::tab {
    background-color: #313244;
    color: #a6adc8;
    border: 1px solid #45475a;
    border-bottom: none;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
    padding: 8px 16px;
    margin-right: 2px;
}

QTabBar::tab:selected {
    background-color: #1e1e2e;
    color: #89b4fa;
    border-bottom: 2px solid #89b4fa;
}

QTabBar::tab:hover:!selected {
    background-color: #3d3f54;
}

/* ===== Check Boxes ===== */
QCheckBox {
    spacing: 8px;
}

QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #45475a;
    border-radius: 4px;
    background-color: #1e1e2e;
}

QCheckBox::indicator:hover {
    border-color: #585b70;
}

QCheckBox::indicator:checked {
    background-color: #89b4fa;
    border-color: #89b4fa;
    image: none;
}

/* ===== Spin Boxes ===== */
QSpinBox, QDoubleSpinBox {
    background-color: #1e1e2e;
    color: #cdd6f4;
    border: 1px solid #45475a;
    border-radius: 6px;
    padding: 6px 8px;
}

QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #89b4fa;
}

QSpinBox::up-button, QDoubleSpinBox::up-button {
    background-color: #313244;
    border: none;
    border-top-right-radius: 6px;
    width: 16px;
}

QSpinBox::down-button, QDoubleSpinBox::down-button {
    background-color: #313244;
    border: none;
    border-bottom-right-radius: 6px;
    width: 16px;
}
"""
