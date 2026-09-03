from PyQt6.QtCore import QEvent,Qt,pyqtSignal
from PyQt6.QtWidgets import QFrame,QHBoxLayout,QLabel,QProgressBar,QPushButton,QVBoxLayout

class Cart(QFrame):
    triggered=pyqtSignal(int); menu_requested=pyqtSignal(int)
    def __init__(self,index):
        super().__init__(); self.index=index; self.color=""
        self.setObjectName("cart"); self.setProperty("playing",False); self.setProperty("alternate",bool(((index//6)+(index%6))%2))
        box=QVBoxLayout(self); box.setContentsMargins(9,5,5,5); box.setSpacing(2)
        top=QHBoxLayout(); self.number=QLabel(f"{index+1:02}"); self.number.setObjectName("number"); top.addWidget(self.number); self.queue_badge=QLabel(); self.queue_badge.setObjectName("queueBadge"); self.queue_badge.hide(); top.addWidget(self.queue_badge); top.addStretch(); self.shortcut=QLabel(); self.shortcut.setObjectName("shortcut"); top.addWidget(self.shortcut)
        self.menu=QPushButton("⋮"); self.menu.setObjectName("dots"); self.menu.setFixedSize(24,24); self.menu.clicked.connect(lambda:self.menu_requested.emit(index)); top.addWidget(self.menu); box.addLayout(top)
        self.button=QPushButton(); self.button.setObjectName("trigger"); self.button.clicked.connect(lambda:self.triggered.emit(index)); box.addWidget(self.button,1)
        self.time=QLabel("00:00 / 00:00"); self.time.setObjectName("cartTime"); self.time.setAlignment(Qt.AlignmentFlag.AlignCenter); self.time.hide(); box.addWidget(self.time)
        self.spectrum=QFrame(); self.spectrum.setFixedHeight(20); spectrum_row=QHBoxLayout(self.spectrum); spectrum_row.setContentsMargins(10,0,10,0); spectrum_row.setSpacing(2)
        self.bars=[]
        for _ in range(18):
            bar=QFrame(); bar.setFixedWidth(4); spectrum_row.addWidget(bar,0,Qt.AlignmentFlag.AlignBottom); self.bars.append(bar)
        self.spectrum.hide(); box.addWidget(self.spectrum)
        self.color_bar=QProgressBar(); self.color_bar.setObjectName("audioProgress"); self.color_bar.setRange(0,1000); self.color_bar.setValue(0); self.color_bar.setTextVisible(False); self.color_bar.setFixedHeight(3); box.addWidget(self.color_bar)
        for widget in (self.number,self.shortcut,self.color_bar,self.spectrum,self.time):
            widget.installEventFilter(self)
    def set_shortcut(self,text): self.shortcut.setText(text)
    def set_queue_position(self,position=None):
        self.setProperty("queued",position is not None)
        self.queue_badge.setText(f"FILA {position}" if position is not None else "")
        self.queue_badge.setVisible(position is not None)
        self.style().unpolish(self); self.style().polish(self)
    def set_locked(self,value): self.menu.setVisible(not value)
    def name(self,text): self.button.setText(text); self.button.setToolTip(text)
    def set_color(self,color):
        self.color=color or ""
        self.setStyleSheet(f"QFrame#cart{{background:{self.color};}}" if self.color else "")
        for bar in self.bars: bar.setStyleSheet("background:#ff8a00;border-radius:1px")
    def playing(self,value):
        self.setProperty("playing",value)
        self.spectrum.setVisible(value); self.time.setVisible(value)
        if not value:self.time.setText("00:00 / 00:00"); self.color_bar.setValue(0)
        self.style().unpolish(self); self.style().polish(self)
    def set_spectrum(self,levels):
        for bar,level in zip(self.bars,levels): bar.setFixedHeight(3+int(16*max(0,min(1,level))))
    def set_time(self,elapsed,duration): self.time.setText(f"{elapsed} / {duration}")
    def set_progress(self,value): self.color_bar.setValue(max(0,min(1000,int(value))))
    def eventFilter(self,obj,event):
        if event.type()==QEvent.Type.MouseButtonRelease and event.button()==Qt.MouseButton.LeftButton:
            self.triggered.emit(self.index); return True
        return super().eventFilter(obj,event)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:self.triggered.emit(self.index)
        super().mouseReleaseEvent(event)
