from pathlib import Path
from PyQt6.QtCore import Qt,QTimer
from PyQt6.QtGui import QAction,QCloseEvent
from PyQt6.QtWidgets import (QFileDialog,QFrame,QGridLayout,QHBoxLayout,QInputDialog,QLabel,QMainWindow,QMenu,QMessageBox,QProgressBar,QPushButton,QSlider,QVBoxLayout,QWidget)
from .audio import Audio
from .config import Config
from .widgets import Cart

STYLE='''
QWidget{background:#0d0e10;color:#f3f3f3;font-family:"Segoe UI";font-size:10pt} QMainWindow{background:#0d0e10}
#header,#player,#footer{background:#15171a;border:1px solid #303238;border-radius:7px} #brand{font-size:18pt;font-weight:800} #brandAccent{color:#ff8a00}
#logo{color:#ff8a00;font-size:27pt;font-weight:900} #small{color:#aaa;font-size:8pt;font-weight:600}
QPushButton{background:#1d1f22;border:1px solid #484b50;border-radius:6px;padding:7px 12px;font-weight:600} QPushButton:hover{border-color:#ff8a00;background:#25272b} QPushButton:pressed{background:#ff8a00;color:#111}
#stop{min-width:120px} #cart{background:#17191b;border:1px solid #55585d;border-bottom:2px solid #ff8a00;border-radius:8px} #cart:hover{background:#202225;border-color:#888}
#cart[playing="true"]{border:2px solid #ff8a00;background:#292016} #number{color:#bfc0c2;font-size:10pt;font-weight:700} #dots{background:transparent;border:0;padding:0;font-size:16pt}
#trigger{background:transparent;border:0;font-size:11pt;font-weight:700;padding:0} #trigger:hover,#trigger:pressed{background:transparent;color:#ff9d2e}
QProgressBar{background:#333;border:0;border-radius:3px;max-height:7px;color:transparent} QProgressBar::chunk{background:#ff8a00;border-radius:3px}
QSlider::groove:horizontal{height:5px;background:#444;border-radius:2px} QSlider::handle:horizontal{width:15px;margin:-5px 0;background:#ff8a00;border-radius:7px}
QMenu{background:#202225;border:1px solid #555;padding:5px} QMenu::item{padding:7px 30px 7px 10px} QMenu::item:selected{background:#ff8a00;color:#111}
'''

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.config=Config(); self.audio=Audio(); self.current=None; self.elapsed=0
        self.setWindowTitle("Cartucheira EDER"); self.setMinimumSize(1024,720); self.resize(1300,900); self.setStyleSheet(STYLE)
        self.build(); self.refresh(); self.timer=QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(100)
    def panel(self,name): f=QFrame(); f.setObjectName(name); return f
    def build(self):
        center=QWidget(); self.setCentralWidget(center); main=QVBoxLayout(center); main.setContentsMargins(16,12,16,8); main.setSpacing(9)
        header=self.panel("header"); row=QHBoxLayout(header)
        brand=QLabel('◉  CARTUCHEIRA <span style="color:#ff8a00">EDER</span>'); brand.setObjectName("brand"); row.addWidget(brand); row.addStretch()
        logo=QLabel("◉\nEDER"); logo.setAlignment(Qt.AlignmentFlag.AlignCenter); logo.setObjectName("logo"); row.addWidget(logo); row.addStretch()
        for text,handler in [("IMPORTAR",self.import_backup),("EXPORTAR",self.export_backup)]:
            b=QPushButton(text); b.clicked.connect(handler); row.addWidget(b)
        main.addWidget(header)
        controls=QHBoxLayout(); controls.addWidget(QLabel("VOLUME GERAL")); self.volume=QSlider(Qt.Orientation.Horizontal); self.volume.setRange(0,100); self.volume.setValue(self.config.data.get("volume",80)); self.volume.setFixedWidth(180); self.volume.valueChanged.connect(self.set_volume); controls.addWidget(self.volume); self.volume_text=QLabel(); controls.addWidget(self.volume_text); controls.addStretch(); main.addLayout(controls)
        grid=QGridLayout(); grid.setSpacing(8); self.carts=[]
        for i in range(36):
            cart=Cart(i); cart.triggered.connect(self.play); cart.menu_requested.connect(self.cart_menu); grid.addWidget(cart,i//6,i%6); self.carts.append(cart)
        main.addLayout(grid,1)
        player=self.panel("player"); row=QHBoxLayout(player); self.playing_label=QLabel("Nenhum áudio em reprodução"); self.playing_label.setMinimumWidth(250); row.addWidget(self.playing_label)
        self.time_label=QLabel("00:00 / 00:00"); row.addWidget(self.time_label); self.progress=QProgressBar(); self.progress.setRange(0,1000); row.addWidget(self.progress,1)
        self.pause=QPushButton("PAUSAR"); self.pause.clicked.connect(self.pause_audio); row.addWidget(self.pause); stop=QPushButton("PARAR"); stop.setObjectName("stop"); stop.clicked.connect(self.stop); row.addWidget(stop); main.addWidget(player)
        footer=self.panel("footer"); row=QHBoxLayout(footer); row.setContentsMargins(10,4,10,4); row.addWidget(QLabel("Cartucheira EDER v0.1")); row.addStretch(); row.addWidget(QLabel("Todos os direitos reservados")); row.addStretch(); owner=QLabel("SO M.Soares"); owner.setStyleSheet("font-size:8pt;font-weight:700"); row.addWidget(owner); main.addWidget(footer)
        self.set_volume(self.volume.value())
    def refresh(self):
        for i,c in enumerate(self.carts): c.name(self.config.data["carts"][i].get("name",""))
    def play(self,index):
        item=self.config.data["carts"][index]; path=self.config.resolve(item.get("audio",""))
        if not path:return
        try:
            self.stop(); self.audio.play(path,self.volume.value()); self.current=index; self.elapsed=0; self.carts[index].playing(True); self.playing_label.setText(f'{index+1:02} - {item.get("name","")}')
        except Exception as exc: QMessageBox.warning(self,"Áudio",f"Não foi possível reproduzir este áudio.\n\n{exc}")
    def stop(self):
        self.audio.stop()
        if self.current is not None:self.carts[self.current].playing(False)
        self.current=None; self.elapsed=0; self.progress.setValue(0); self.playing_label.setText("Nenhum áudio em reprodução"); self.time_label.setText("00:00 / 00:00"); self.pause.setText("PAUSAR")
    def pause_audio(self): self.pause.setText("CONTINUAR" if self.audio.pause() else "PAUSAR")
    def set_volume(self,value): self.audio.volume(value); self.volume_text.setText(f"{value}%"); self.config.data["volume"]=value; self.config.write()
    @staticmethod
    def stamp(value):
        value=max(0,int(value)); return f"{value//60:02}:{value%60:02}"
    def tick(self):
        if self.current is None:return
        if not self.audio.paused:self.elapsed+=.1
        if not self.audio.busy():self.stop();return
        duration=max(.01,self.audio.duration); self.progress.setValue(min(1000,int(self.elapsed/duration*1000))); self.time_label.setText(f"{self.stamp(self.elapsed)} / {self.stamp(duration)}")
    def cart_menu(self,index):
        menu=QMenu(self); change=QAction("Trocar áudio…",self); rename=QAction("Renomear…",self); clear=QAction("Limpar",self)
        change.triggered.connect(lambda:self.change_audio(index)); rename.triggered.connect(lambda:self.rename(index)); clear.triggered.connect(lambda:self.clear(index)); menu.addActions([change,rename]); menu.addSeparator(); menu.addAction(clear); menu.exec(self.carts[index].mapToGlobal(self.carts[index].rect().topRight()))
    def change_audio(self,index):
        filename,_=QFileDialog.getOpenFileName(self,"Selecionar áudio","","Áudios (*.wav *.mp3 *.ogg);;Todos (*.*)")
        if filename:self.config.set_audio(index,Path(filename))
    def rename(self,index):
        value=self.config.data["carts"][index].get("name",""); name,ok=QInputDialog.getText(self,"Renomear cartucho","Nome personalizado:",text=value)
        if ok:self.config.data["carts"][index]["name"]=name.strip()[:40]; self.config.write(); self.carts[index].name(name.strip()[:40])
    def clear(self,index):
        if QMessageBox.question(self,"Limpar cartucho","Remover nome e áudio deste cartucho?")==QMessageBox.StandardButton.Yes:
            if self.current==index:self.stop()
            self.config.clear(index); self.carts[index].name("")
    def export_backup(self):
        filename,_=QFileDialog.getSaveFileName(self,"Exportar backup","Cartucheira-EDER-backup.eder","Backup EDER (*.eder)")
        if filename:
            try:self.config.export(Path(filename)); QMessageBox.information(self,"Backup","Backup exportado com sucesso.")
            except Exception as exc:QMessageBox.critical(self,"Backup",str(exc))
    def import_backup(self):
        filename,_=QFileDialog.getOpenFileName(self,"Importar backup","","Backup EDER (*.eder);;ZIP (*.zip)")
        if filename and QMessageBox.question(self,"Importar backup","Substituir a programação atual?")==QMessageBox.StandardButton.Yes:
            try:self.stop(); self.config.import_(Path(filename)); self.volume.setValue(self.config.data.get("volume",80)); self.refresh(); QMessageBox.information(self,"Backup","Programação importada com sucesso.")
            except Exception as exc:QMessageBox.critical(self,"Backup",str(exc))
    def closeEvent(self,event:QCloseEvent): self.config.write(); self.audio.close(); event.accept()
