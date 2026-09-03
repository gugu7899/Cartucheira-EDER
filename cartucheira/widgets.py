from PyQt6.QtCore import QEvent,QRectF,Qt,pyqtSignal
from PyQt6.QtGui import QColor,QLinearGradient,QPainter
from PyQt6.QtWidgets import QFrame,QHBoxLayout,QLabel,QProgressBar,QPushButton,QVBoxLayout,QWidget

class Spectrum(QWidget):
    def __init__(self,bars=24):
        super().__init__(); self.levels=[0.0]*bars; self.peaks=[0.0]*bars; self.setFixedHeight(24)
    def set_levels(self,values):
        for i,target in enumerate(values[:len(self.levels)]):
            target=max(0.0,min(1.0,float(target))); speed=.52 if target>self.levels[i] else .20
            self.levels[i]+=((target-self.levels[i])*speed); self.peaks[i]=max(self.levels[i],self.peaks[i]-.035)
        self.update()
    def paintEvent(self,event):
        painter=QPainter(self); painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        count=len(self.levels); gap=2.0; width=max(2.0,(self.width()-gap*(count-1))/count); height=self.height()-3
        gradient=QLinearGradient(0,self.height(),0,0); gradient.setColorAt(0,QColor("#ff7a00")); gradient.setColorAt(.65,QColor("#ff9d22")); gradient.setColorAt(1,QColor("#ffd166"))
        painter.setPen(Qt.PenStyle.NoPen)
        for i,(level,peak) in enumerate(zip(self.levels,self.peaks)):
            x=i*(width+gap); bar_height=max(2.0,height*level); painter.setBrush(gradient); painter.drawRoundedRect(QRectF(x,self.height()-bar_height,width,bar_height),1.2,1.2)
            if peak>.08:
                painter.setBrush(QColor("#fff1cf")); peak_y=max(0.0,self.height()-height*peak-2); painter.drawRoundedRect(QRectF(x,peak_y,width,1.5),.7,.7)

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
        self.spectrum=Spectrum(24); self.bars=self.spectrum.levels
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
    def playing(self,value):
        self.setProperty("playing",value)
        self.spectrum.setVisible(value); self.time.setVisible(value)
        if not value:self.time.setText("00:00 / 00:00"); self.color_bar.setValue(0)
        self.style().unpolish(self); self.style().polish(self)
    def set_spectrum(self,levels):
        self.spectrum.set_levels(levels)
    def set_time(self,elapsed,duration): self.time.setText(f"{elapsed} / {duration}")
    def set_progress(self,value): self.color_bar.setValue(max(0,min(1000,int(value))))
    def eventFilter(self,obj,event):
        if event.type()==QEvent.Type.MouseButtonRelease and event.button()==Qt.MouseButton.LeftButton:
            self.triggered.emit(self.index); return True
        return super().eventFilter(obj,event)
    def mouseReleaseEvent(self,event):
        if event.button()==Qt.MouseButton.LeftButton:self.triggered.emit(self.index)
        super().mouseReleaseEvent(event)
