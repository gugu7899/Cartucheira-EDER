from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QFrame,QHBoxLayout,QLabel,QPushButton,QVBoxLayout

class Cart(QFrame):
    triggered=pyqtSignal(int); menu_requested=pyqtSignal(int)
    def __init__(self,index):
        super().__init__(); self.index=index; self.setObjectName("cart"); self.setProperty("playing",False)
        box=QVBoxLayout(self); box.setContentsMargins(9,5,5,7)
        top=QHBoxLayout(); number=QLabel(f"{index+1:02}"); number.setObjectName("number"); top.addWidget(number); top.addStretch()
        menu=QPushButton("⋮"); menu.setObjectName("dots"); menu.setFixedSize(24,24); menu.clicked.connect(lambda:self.menu_requested.emit(index)); top.addWidget(menu); box.addLayout(top)
        self.button=QPushButton(); self.button.setObjectName("trigger"); self.button.clicked.connect(lambda:self.triggered.emit(index)); box.addWidget(self.button,1)
    def name(self,text): self.button.setText(text); self.button.setToolTip(text)
    def playing(self,value):
        self.setProperty("playing",value); self.style().unpolish(self); self.style().polish(self)
