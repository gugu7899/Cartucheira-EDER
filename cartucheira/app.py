from pathlib import Path
from PyQt6.QtCore import Qt,QTimer
from PyQt6.QtGui import QAction,QCloseEvent,QColor,QPixmap
from PyQt6.QtWidgets import (QColorDialog,QComboBox,QFileDialog,QFrame,QGridLayout,QHBoxLayout,QInputDialog,QLabel,QMainWindow,QMenu,QMessageBox,QProgressBar,QPushButton,QSlider,QVBoxLayout,QWidget)
from .audio import Audio
from .config import Config,resource
from .widgets import Cart

THEMES={
 "Escuro Padrão":("#0d0e10","#15171a","#17191b","#f3f3f3"),
 "Preto Estúdio":("#050505","#0a0a0a","#111111","#ffffff"),
 "Cinza Console":("#202226","#292c31","#32353a","#f5f5f5")}
BASE_STYLE='''
QWidget{background:@BG;color:@FG;font-family:"Segoe UI";font-size:10pt} QMainWindow{background:@BG}
#titleBar,#controlBar,#player,#footer{background:@PANEL;border:1px solid #303238;border-radius:7px}
#brand{font-size:17pt;font-weight:800} #logo{background:#080808;border-left:1px solid #262626;border-right:1px solid #262626}
QPushButton{background:#1d1f22;border:1px solid #484b50;border-radius:6px;padding:7px 12px;font-weight:700}
QPushButton:hover{border-color:#ff8a00;background:#25272b} QPushButton:pressed{background:#ff8a00;color:#111}
#stop{min-width:92px} #cart{background:@CART;border:1px solid #55585d;border-radius:8px} #cart:hover{background:#202225;border-color:#8b8b8b}
#cart[playing="true"]{border:2px solid #ff8a00;background:#292016} #number{color:#bfc0c2;font-size:10pt;font-weight:700}
#dots{background:transparent;border:0;padding:0;font-size:16pt} #led{color:#444;font-size:9pt}
#trigger{background:transparent;border:0;font-size:11pt;font-weight:700;padding:0} #trigger:hover,#trigger:pressed{background:transparent;color:#ff9d2e}
QProgressBar{background:#333;border:0;border-radius:3px;max-height:7px;color:transparent} QProgressBar::chunk{background:#ff8a00;border-radius:3px}
QSlider::groove:horizontal{height:5px;background:#444;border-radius:2px} QSlider::handle:horizontal{width:15px;margin:-5px 0;background:#ff8a00;border-radius:7px}
QComboBox{background:#1d1f22;border:1px solid #484b50;border-radius:6px;padding:7px 28px 7px 10px;min-width:140px}
QMenu{background:#202225;border:1px solid #555;padding:5px} QMenu::item{padding:7px 30px 7px 10px} QMenu::item:selected{background:#ff8a00;color:#111}
'''

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.config=Config(); self.audio=Audio(); self.current=None; self.elapsed=0
        self.setWindowTitle("Cartucheira EDER"); self.setMinimumSize(1100,740); self.resize(1300,900)
        self.build(); self.refresh(); self.set_theme(self.config.data.get("theme","Escuro Padrão"))
        self.timer=QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(100)
    def panel(self,name): f=QFrame(); f.setObjectName(name); return f
    def build(self):
        center=QWidget(); self.setCentralWidget(center); main=QVBoxLayout(center); main.setContentsMargins(12,8,12,6); main.setSpacing(8)
        title=self.panel("titleBar"); row=QHBoxLayout(title); row.setContentsMargins(18,5,18,5)
        brand=QLabel('◉  CARTUCHEIRA <span style="color:#ff8a00">EDER</span>'); brand.setObjectName("brand"); row.addWidget(brand); row.addStretch(); main.addWidget(title)
        controls=self.panel("controlBar"); row=QHBoxLayout(controls); row.setContentsMargins(14,7,14,7)
        theme_box=QVBoxLayout(); heading=QLabel("TEMA"); heading.setStyleSheet("color:#ff8a00;font-weight:800"); theme_box.addWidget(heading)
        self.theme=QComboBox(); self.theme.addItems(THEMES); self.theme.setCurrentText(self.config.data.get("theme","Escuro Padrão")); self.theme.currentTextChanged.connect(self.set_theme); theme_box.addWidget(self.theme); row.addLayout(theme_box)
        volume_box=QVBoxLayout(); volume_box.addWidget(QLabel("VOLUME GERAL")); line=QHBoxLayout(); line.addWidget(QLabel("🔊"))
        self.volume=QSlider(Qt.Orientation.Horizontal); self.volume.setRange(0,100); self.volume.setValue(self.config.data.get("volume",80)); self.volume.setFixedWidth(145); self.volume.valueChanged.connect(self.set_volume); line.addWidget(self.volume); self.volume_text=QLabel(); line.addWidget(self.volume_text); volume_box.addLayout(line); row.addLayout(volume_box)
        row.addStretch(); logo=QLabel(); logo.setObjectName("logo"); logo.setAlignment(Qt.AlignmentFlag.AlignCenter); logo.setFixedSize(245,112)
        pix=QPixmap(str(resource("assets/logo.png"))); logo.setPixmap(pix.scaled(225,105,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)); row.addWidget(logo); row.addStretch()
        for text,handler in [("↓  IMPORTAR",self.import_backup),("↑  EXPORTAR",self.export_backup)]:
            button=QPushButton(text); button.clicked.connect(handler); row.addWidget(button)
        self.pause=QPushButton("Ⅱ  PAUSAR"); self.pause.clicked.connect(self.pause_audio); row.addWidget(self.pause)
        stop=QPushButton("■  PARAR"); stop.setObjectName("stop"); stop.clicked.connect(self.stop); row.addWidget(stop); main.addWidget(controls)
        grid=QGridLayout(); grid.setSpacing(8); self.carts=[]
        for i in range(36):
            cart=Cart(i); cart.triggered.connect(self.play); cart.menu_requested.connect(self.cart_menu); grid.addWidget(cart,i//6,i%6); self.carts.append(cart)
        main.addLayout(grid,1)
        player=self.panel("player"); row=QHBoxLayout(player); row.setContentsMargins(16,7,16,7); row.addWidget(QLabel("▶"))
        self.time_label=QLabel("00:00 / 00:00"); row.addWidget(self.time_label); self.progress=QProgressBar(); self.progress.setRange(0,1000); row.addWidget(self.progress,1); main.addWidget(player)
        footer=self.panel("footer"); row=QHBoxLayout(footer); row.setContentsMargins(10,3,10,3); row.addWidget(QLabel("Cartucheira EDER v0.1")); row.addStretch(); row.addWidget(QLabel("Todos os direitos reservados")); row.addStretch(); owner=QLabel("SO M.Soares"); owner.setStyleSheet("font-size:8pt;font-weight:700"); row.addWidget(owner); main.addWidget(footer)
        self.set_volume(self.volume.value())
    def refresh(self):
        for i,cart in enumerate(self.carts):
            item=self.config.data["carts"][i]; cart.name(item.get("name","")); cart.set_color(item.get("color","#ff8a00"))
    def play(self,index):
        if self.current==index and self.audio.busy(): self.stop(); return
        item=self.config.data["carts"][index]; path=self.config.resolve(item.get("audio",""))
        if not path:return
        try:
            self.stop(); self.audio.play(path,self.volume.value()); self.current=index; self.elapsed=0; self.carts[index].playing(True)
        except Exception as exc: QMessageBox.warning(self,"Áudio",f"Não foi possível reproduzir este áudio.\n\n{exc}")
    def stop(self):
        self.audio.stop()
        if self.current is not None:self.carts[self.current].playing(False)
        self.current=None; self.elapsed=0; self.progress.setValue(0); self.time_label.setText("00:00 / 00:00"); self.pause.setText("Ⅱ  PAUSAR")
    def pause_audio(self): self.pause.setText("▶  CONTINUAR" if self.audio.pause() else "Ⅱ  PAUSAR")
    def set_volume(self,value): self.audio.volume(value); self.volume_text.setText(f"{value}%"); self.config.data["volume"]=value; self.config.write()
    def set_theme(self,name):
        bg,panel,cart,fg=THEMES.get(name,THEMES["Escuro Padrão"]); style=BASE_STYLE.replace("@BG",bg).replace("@FG",fg).replace("@PANEL",panel).replace("@CART",cart)
        self.setStyleSheet(style); self.config.data["theme"]=name; self.config.write()
    @staticmethod
    def stamp(value): value=max(0,int(value)); return f"{value//60:02}:{value%60:02}"
    def tick(self):
        if self.current is None:return
        if not self.audio.paused:self.elapsed+=.1
        if not self.audio.busy():self.stop();return
        duration=max(.01,self.audio.duration); self.progress.setValue(min(1000,int(self.elapsed/duration*1000))); self.time_label.setText(f"{self.stamp(self.elapsed)} / {self.stamp(duration)}")
    def cart_menu(self,index):
        menu=QMenu(self); change=QAction("Trocar áudio…",self); rename=QAction("Renomear…",self); color=QAction("Alterar cor…",self); clear=QAction("Limpar",self)
        change.triggered.connect(lambda:self.change_audio(index)); rename.triggered.connect(lambda:self.rename(index)); color.triggered.connect(lambda:self.change_color(index)); clear.triggered.connect(lambda:self.clear(index))
        menu.addActions([change,rename,color]); menu.addSeparator(); menu.addAction(clear); menu.exec(self.carts[index].mapToGlobal(self.carts[index].rect().topRight()))
    def change_audio(self,index):
        filename,_=QFileDialog.getOpenFileName(self,"Selecionar áudio","","Áudios (*.wav *.mp3 *.ogg);;Todos (*.*)")
        if filename:self.config.set_audio(index,Path(filename))
    def rename(self,index):
        value=self.config.data["carts"][index].get("name",""); name,ok=QInputDialog.getText(self,"Renomear cartucho","Nome personalizado:",text=value)
        if ok:self.config.data["carts"][index]["name"]=name.strip()[:40]; self.config.write(); self.carts[index].name(name.strip()[:40])
    def change_color(self,index):
        current=QColor(self.config.data["carts"][index].get("color","#ff8a00")); chosen=QColorDialog.getColor(current,self,"Cor do cartucho")
        if chosen.isValid(): self.config.data["carts"][index]["color"]=chosen.name(); self.config.write(); self.carts[index].set_color(chosen.name())
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
            try:self.stop(); self.config.import_(Path(filename)); self.volume.setValue(self.config.data.get("volume",80)); self.theme.setCurrentText(self.config.data.get("theme","Escuro Padrão")); self.refresh(); QMessageBox.information(self,"Backup","Programação importada com sucesso.")
            except Exception as exc:QMessageBox.critical(self,"Backup",str(exc))
    def closeEvent(self,event:QCloseEvent): self.config.write(); self.audio.close(); event.accept()
