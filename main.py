import os, sys
os.environ.setdefault("PYGAME_HIDE_SUPPORT_PROMPT", "1")
from PyQt6.QtWidgets import QApplication, QMessageBox
from cartucheira.app import MainWindow

def main():
    app = QApplication(sys.argv)
    app.setApplicationName("Cartucheira MBS")
    app.setOrganizationName("SO M.Soares")
    try:
        window = MainWindow()
    except Exception as exc:
        QMessageBox.critical(None, "Cartucheira MBS", f"Não foi possível iniciar.\n\n{exc}")
        return 1
    window.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
