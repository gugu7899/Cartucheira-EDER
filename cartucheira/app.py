test_backup (test_config.TestConfig.test_backup) ... ok
test_clear_and_reload (test_config.TestConfig.test_clear_and_reload) ... ok
test_defaults (test_config.TestConfig.test_defaults) ... ok

----------------------------------------------------------------------
Ran 3 tests in 0.004s

OK
from pathlib import Path
from PyQt6.QtCore import Qt,QTimer
from PyQt6.QtGui import QAction,QCloseEvent,QColor,QImage,QPixmap
from PyQt6.QtWidgets import (QColorDialog,QComboBox,QFileDialog,QFrame,QGridLayout,QHBoxLayout,QInputDialog,QLabel,QMainWindow,QMenu,QMessageBox,QPushButton,QSlider,QVBoxLayout,QWidget)
from .audio import Audio
from .config import Config,resource
from .widgets import Cart

THEMES={
 "Escuro Padrão":("#0d0e10","#15171a","#17191b","#1d2024","#f3f3f3","#ff8a00"),
 "Preto Estúdio":("#050505","#0a0a0a","#101010","#171717","#ffffff","#ff7900"),
 "Cinza Console":("#202226","#292c31","#303338","#383b40","#f5f5f5","#ff9b22"),
 "Azul Estúdio":("#071525","#0b2139","#102b49","#153657","#edf6ff","#268cff")}
BASE_STYLE='''
QWidget{background:@BG;color:@FG;font-family:"Segoe UI";font-size:10pt} QLabel{background:transparent} QMainWindow{background:@BG}
#titleBar,#footer{background:@PANEL;border:1px solid #303238;border-radius:7px} #controlBar{background:@BG;border:0}
#brand{font-size:17pt;font-weight:800} #logo{background:transparent;border-left:1px solid #303238;border-right:1px solid #303238}
QPushButton{background:#1d1f22;border:1px solid #484b50;border-radius:6px;padding:7px 12px;font-weight:700}
QPushButton:hover{border-color:@ACCENT;background:#25272b} QPushButton:pressed{background:@ACCENT;color:#111}
#stop{min-width:92px} #cart{background:@CART;border:1px solid #55585d;border-radius:8px} #cart[alternate="true"]{background:@CARTALT} #cart:hover{border-color:#8b8b8b}
#cart[playing="true"]{border:2px solid @ACCENT;background:@PANEL} #number{color:#bfc0c2;font-size:10pt;font-weight:700}
#dots{background:transparent;border:0;padding:0;font-size:16pt}
#trigger{background:transparent;border:0;font-size:11pt;font-weight:700;padding:0} #trigger:hover,#trigger:pressed{background:transparent;color:#ff9d2e}
#cartTime{background:transparent;color:#c7c7c7;font-size:8pt;font-weight:600} #audioProgress{background:transparent;border:0} #audioProgress::chunk{background:#ff8a00;border-radius:1px}
QSlider{background:transparent} QSlider::groove:horizontal{height:4px;background:#30343a;border-radius:2px} QSlider::handle:horizontal{width:15px;margin:-5px 0;background:@ACCENT;border-radius:7px}
QComboBox{background:transparent;border:1px solid #484b50;border-radius:6px;padding:7px 28px 7px 10px;min-width:140px}
QMenu{background:#202225;border:1px solid #555;padding:5px} QMenu::item{padding:7px 30px 7px 10px} QMenu::item:selected{background:@ACCENT;color:#111}
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
        theme_box=QVBoxLayout(); self.theme_heading=QLabel("TEMA"); self.theme_heading.setAlignment(Qt.AlignmentFlag.AlignCenter); self.theme_heading.setStyleSheet("font-weight:800"); theme_box.addWidget(self.theme_heading)
        self.theme=QComboBox(); self.theme.addItems(THEMES); self.theme.setCurrentText(self.config.data.get("theme","Escuro Padrão")); self.theme.currentTextChanged.connect(self.set_theme); theme_box.addWidget(self.theme); row.addLayout(theme_box)
        volume_box=QVBoxLayout(); volume_heading=QLabel("VOLUME GERAL"); volume_heading.setAlignment(Qt.AlignmentFlag.AlignCenter); volume_heading.setStyleSheet("font-weight:800"); volume_box.addWidget(volume_heading); line=QHBoxLayout(); line.addWidget(QLabel("🔊"))
        self.volume=QSlider(Qt.Orientation.Horizontal); self.volume.setRange(0,100); self.volume.setValue(self.config.data.get("volume",80)); self.volume.setFixedWidth(145); self.volume.valueChanged.connect(self.set_volume); line.addWidget(self.volume); self.volume_text=QLabel(); line.addWidget(self.volume_text); volume_box.addLayout(line); row.addLayout(volume_box)
        row.addStretch(); logo=QLabel(); logo.setObjectName("logo"); logo.setAlignment(Qt.AlignmentFlag.AlignCenter); logo.setFixedSize(245,112)
        image=QImage(str(resource("assets/logo.png")))
        for y in range(image.height()):
            for x in range(image.width()):
                color=image.pixelColor(x,y)
                if max(color.red(),color.green(),color.blue())<58: color.setAlpha(0); image.setPixelColor(x,y,color)
        pix=QPixmap.fromImage(image); logo.setPixmap(pix.scaled(225,105,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation)); row.addWidget(logo); row.addStretch()
        for text,handler in [("↓  IMPORTAR",self.import_backup),("↑  EXPORTAR",self.export_backup)]:
            button=QPushButton(text); button.clicked.connect(handler); row.addWidget(button)
        settings=QPushButton("⚙"); settings.setFixedWidth(45); settings.clicked.connect(lambda:self.settings_menu(settings)); row.addWidget(settings); main.addWidget(controls)
        grid=QGridLayout(); grid.setSpacing(8); self.carts=[]
        for i in range(36):
            cart=Cart(i); cart.triggered.connect(self.play); cart.menu_requested.connect(self.cart_menu); grid.addWidget(cart,i//6,i%6); self.carts.append(cart)
        main.addLayout(grid,1)
        owner=QLabel("Desenvolvedor: Marcelo Soares"); owner.setStyleSheet("background:transparent;border:0;font-size:11pt;font-weight:400;color:#f2f2f2;padding-left:4px"); owner.setAlignment(Qt.AlignmentFlag.AlignLeft); main.addWidget(owner)
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
        self.current=None; self.elapsed=0
    def set_volume(self,value): self.audio.volume(value); self.volume_text.setText(f"{value}%"); self.config.data["volume"]=value; self.config.write()
    def set_theme(self,name):
        bg,panel,cart,cart_alt,fg,accent=THEMES.get(name,THEMES["Escuro Padrão"]); style=BASE_STYLE.replace("@BG",bg).replace("@FG",fg).replace("@PANEL",panel).replace("@CARTALT",cart_alt).replace("@CART",cart).replace("@ACCENT",accent)
        self.setStyleSheet(style); self.theme_heading.setStyleSheet("font-weight:800"); self.config.data["theme"]=name; self.config.write()
    @staticmethod
    def stamp(value): value=max(0,int(value)); return f"{value//60:02}:{value%60:02}"
    def tick(self):
        if self.current is None:return
        if not self.audio.paused:self.elapsed+=.1
        if not self.audio.busy():self.stop();return
        duration=max(.01,self.audio.duration); cart=self.carts[self.current]; cart.set_time(self.stamp(self.elapsed),self.stamp(duration)); cart.set_progress(self.elapsed/duration*1000)
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
    def settings_menu(self,button):
        menu=QMenu(self); restore=QAction("Restaurar cartuchos originais",self); about=QAction("Sobre a Cartucheira EDER",self)
        restore.triggered.connect(self.restore_defaults); about.triggered.connect(lambda:QMessageBox.about(self,"Cartucheira EDER","Cartucheira EDER v0.1\nSistema profissional de áudio para rádio e estúdio."))
        menu.addAction(restore); menu.addSeparator(); menu.addAction(about); menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
    def restore_defaults(self):
        if QMessageBox.question(self,"Restaurar cartuchos","Restaurar nomes, cores e efeitos originais dos 36 cartuchos?")==QMessageBox.StandardButton.Yes:
            self.stop(); self.config.data=Config.defaults(); self.config.write(); self.volume.setValue(80); self.theme.setCurrentText("Escuro Padrão"); self.refresh()
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
