import math
from PyQt6.QtCore import QEvent,QTimer,Qt,pyqtSignal
from PyQt6.QtWidgets import QFrame,QHBoxLayout,QLabel,QPushButton,QVBoxLayout

class Cart(QFrame):
    triggered=pyqtSignal(int); menu_requested=pyqtSignal(int)
    def __init__(self,index):
        super().__init__(); self.index=index; self.color="#ff8a00"
        self.setObjectName("cart"); self.setProperty("playing",False)
        box=QVBoxLayout(self); box.setContentsMargins(9,5,5,5); box.setSpacing(2)
        top=QHBoxLayout(); self.number=QLabel(f"{index+1:02}"); self.number.setObjectName("number"); top.addWidget(self.number); top.addStretch()
        self.led=QLabel("●"); self.led.setObjectName("led"); self.led.setProperty("active",False); top.addWidget(self.led)
        self.menu=QPushButton("⋮"); self.menu.setObjectName("dots"); self.menu.setFixedSize(24,24); self.menu.clicked.connect(lambda:self.menu_requested.emit(index)); top.addWidget(self.menu); box.addLayout(top)
        self.button=QPushButton(); self.button.setObjectName("trigger"); self.button.clicked.connect(lambda:self.triggered.emit(index)); box.addWidget(self.button,1)
        self.spectrum=QFrame(); self.spectrum.setFixedHeight(20); spectrum_row=QHBoxLayout(self.spectrum); spectrum_row.setContentsMargins(10,0,10,0); spectrum_row.setSpacing(2)
        self.bars=[]
        for _ in range(18):
            bar=QFrame(); bar.setFixedWidth(4); spectrum_row.addWidget(bar,0,Qt.AlignmentFlag.AlignBottom); self.bars.append(bar)
        self.spectrum.hide(); box.addWidget(self.spectrum)
        self.color_bar=QFrame(); self.color_bar.setFixedHeight(3); box.addWidget(self.color_bar)
        self.phase=0; self.animator=QTimer(self); self.animator.setInterval(75); self.animator.timeout.connect(self.animate_spectrum)
        for widget in (self.number,self.led,self.color_bar,self.spectrum):
            widget.installEventFilter(self)
    def name(self,text): self.button.setText(text); self.button.setToolTip(text)
    def set_color(self,color):
        self.color=color or "#ff8a00"; self.color_bar.setStyleSheet(f"background:{self.color};border-radius:1px")
        for bar in self.bars: bar.setStyleSheet(f"background:{self.color};border-radius:1px")
    def playing(self,value):
        self.setProperty("playing",value); self.led.setProperty("active",value)
        self.led.setStyleSheet(f"color:{self.color if value else '#444'}")
        self.spectrum.setVisible(value)
        self.animator.start() if value else self.animator.stop()
        for w in (self,self.led): w.style().unpolish(w); w.style().polish(w)
    def animate_spectrum(self):
        self.phase+=1
        for i,bar in enumerate(self.bars):
            height=4+int(14*abs(math.sin(self.phase*.32+i*.71)*math.cos(self.phase*.17+i*.23)))
            bar.setFixedHeight(height)
    def eventFilter(self,obj,event):
        if event.type()==QEvent.Type.MouseButtonRelease and event.button()==Qt.MouseButton.LeftButton:
            self.triggered.emit(self.index); return True
        return super().eventFilter(obj,event)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:self.triggered.emit(self.index)
        super().mouseReleaseEvent(event)
