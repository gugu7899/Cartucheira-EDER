from pathlib import Path
from PyQt6.QtCore import Qt,QTimer
from PyQt6.QtGui import QAction,QCloseEvent,QColor,QImage,QKeySequence,QPixmap,QShortcut
from PyQt6.QtWidgets import (QColorDialog,QComboBox,QFileDialog,QFrame,QGridLayout,QHBoxLayout,QInputDialog,QLabel,QMainWindow,QMenu,QMessageBox,QPushButton,QSlider,QVBoxLayout,QWidget)
from .audio import Audio
from .config import Config,DEFAULT_KEYS,resource
from .widgets import Cart

THEMES={
 "Escuro Padrão":("#0d0e10","#15171a","#17191b","#1d2024","#f3f3f3","#ff8a00"),
 "Preto Estúdio":("#050505","#0a0a0a","#101010","#171717","#ffffff","#ff7900"),
 "Cinza Console":("#202226","#292c31","#303338","#383b40","#f5f5f5","#ff9b22"),
 "Azul Estúdio":("#071525","#0b2139","#102b49","#153657","#edf6ff","#268cff")}
BASE_STYLE='''
QWidget{background:@BG;color:@FG;font-family:"Segoe UI";font-size:10pt} QLabel{background:transparent} QMainWindow{background:@BG}
#titleBar,#footer{background:@PANEL;border:1px solid #303238;border-radius:7px} #controlBar{background:@BG;border:0}
#brand{font-size:17pt;font-weight:800} #logo{background:transparent;border:0}
QPushButton{background:#1d1f22;border:1px solid #484b50;border-radius:6px;padding:7px 12px;font-weight:700}
QPushButton:hover{border-color:@ACCENT;background:#25272b} QPushButton:pressed{background:@ACCENT;color:#111}
#stop{min-width:92px} #cart{background:@CART;border:1px solid #55585d;border-radius:8px} #cart[alternate="true"]{background:@CARTALT} #cart:hover{border-color:#8b8b8b}
#cart[playing="true"]{border:2px solid @ACCENT} #number{color:#bfc0c2;font-size:10pt;font-weight:700}
#dots{background:transparent;border:0;padding:0;font-size:16pt}
#shortcut{color:#8f959d;font-size:8pt;font-weight:700;margin-right:4px} #lockButton[locked="true"]{background:@ACCENT;color:#111}
#trigger{background:transparent;border:0;font-size:11pt;font-weight:700;padding:0} #trigger:hover,#trigger:pressed{background:transparent;color:#ff9d2e}
#cartTime{background:transparent;color:#c7c7c7;font-size:8pt;font-weight:600} #audioProgress{background:transparent;border:0} #audioProgress::chunk{background:#ff8a00;border-radius:1px}
QSlider{background:transparent} QSlider::groove:horizontal{height:4px;background:#30343a;border-radius:2px} QSlider::handle:horizontal{width:15px;margin:-5px 0;background:@ACCENT;border-radius:7px}
QComboBox{background:transparent;border:1px solid #484b50;border-radius:6px;padding:7px 28px 7px 10px;min-width:140px}
QMenu{background:#202225;border:1px solid #555;padding:5px} QMenu::item{padding:7px 30px 7px 10px} QMenu::item:selected{background:@ACCENT;color:#111}
'''

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__(); self.config=Config(); self.audio=Audio(self.config.data.get("output_device")); self.current=None; self.elapsed=0; self.fading=False; self.locked=False
        self.setWindowTitle("Cartucheira MBS"); self.setMinimumSize(1100,740); self.resize(1300,900)
        self.build(); self.refresh(); self.refresh_identity(); self.set_theme(self.config.data.get("theme","Escuro Padrão"))
        self.timer=QTimer(self); self.timer.timeout.connect(self.tick); self.timer.start(100)
    def panel(self,name): f=QFrame(); f.setObjectName(name); return f
    def build(self):
        center=QWidget(); self.setCentralWidget(center); main=QVBoxLayout(center); main.setContentsMargins(12,8,12,6); main.setSpacing(8)
        title=self.panel("titleBar"); row=QHBoxLayout(title); row.setContentsMargins(18,5,18,5)
        self.brand=QLabel(); self.brand.setObjectName("brand"); row.addWidget(self.brand); row.addStretch(); main.addWidget(title)
        controls=self.panel("controlBar"); row=QHBoxLayout(controls); row.setContentsMargins(14,7,14,7)
        theme_box=QVBoxLayout(); self.theme_heading=QLabel("TEMA"); self.theme_heading.setAlignment(Qt.AlignmentFlag.AlignCenter); self.theme_heading.setStyleSheet("font-weight:800"); theme_box.addWidget(self.theme_heading)
        self.theme=QComboBox(); self.theme.addItems(THEMES); self.theme.setCurrentText(self.config.data.get("theme","Escuro Padrão")); self.theme.currentTextChanged.connect(self.set_theme); theme_box.addWidget(self.theme); row.addLayout(theme_box)
        volume_box=QVBoxLayout(); volume_heading=QLabel("VOLUME GERAL"); volume_heading.setFixedWidth(145); volume_heading.setAlignment(Qt.AlignmentFlag.AlignCenter); volume_heading.setStyleSheet("font-weight:800"); heading_line=QHBoxLayout(); heading_line.addSpacing(28); heading_line.addWidget(volume_heading); heading_line.addSpacing(38); volume_box.addLayout(heading_line); line=QHBoxLayout(); line.addWidget(QLabel("🔊"))
        self.volume=QSlider(Qt.Orientation.Horizontal); self.volume.setRange(0,100); self.volume.setValue(self.config.data.get("volume",80)); self.volume.setFixedWidth(145); self.volume.valueChanged.connect(self.set_volume); line.addWidget(self.volume); self.volume_text=QLabel(); line.addWidget(self.volume_text); volume_box.addLayout(line); row.addLayout(volume_box)
        row.addStretch(); logo_panel=QFrame(); logo_panel.setObjectName("logo"); logo_panel.setFixedSize(245,112); logo_box=QVBoxLayout(logo_panel); logo_box.setContentsMargins(5,3,5,3); logo_box.setSpacing(0)
        self.logo_image=QLabel(); self.logo_image.setAlignment(Qt.AlignmentFlag.AlignCenter); self.logo_name=QLabel(); self.logo_name.setAlignment(Qt.AlignmentFlag.AlignCenter); self.logo_name.setStyleSheet("font-size:15pt;font-weight:900;letter-spacing:2px")
        logo_box.addWidget(self.logo_image,1); logo_box.addWidget(self.logo_name); row.addWidget(logo_panel); row.addStretch()
        self.program_controls=[self.theme]
        for text,handler in [("↓  IMPORTAR",self.import_backup),("↑  EXPORTAR",self.export_backup)]:
            button=QPushButton(text); button.clicked.connect(handler); row.addWidget(button); self.program_controls.append(button)
        self.lock_button=QPushButton("🔒  BLOQUEAR"); self.lock_button.setObjectName("lockButton"); self.lock_button.setProperty("locked",False); self.lock_button.clicked.connect(self.toggle_lock); row.addWidget(self.lock_button)
        settings=QPushButton("⚙"); settings.setFixedWidth(45); settings.clicked.connect(lambda:self.settings_menu(settings)); row.addWidget(settings); main.addWidget(controls)
        self.program_controls.append(settings)
        grid=QGridLayout(); grid.setSpacing(8); self.carts=[]
        for i in range(36):
            key=self.config.data.get("shortcuts",DEFAULT_KEYS)[i]; cart=Cart(i); cart.set_shortcut(key); cart.triggered.connect(self.play); cart.menu_requested.connect(self.cart_menu); grid.addWidget(cart,i//6,i%6); self.carts.append(cart)
        self.key_bindings=[]
        for i,key in enumerate(self.config.data.get("shortcuts",DEFAULT_KEYS)):
            shortcut=QShortcut(QKeySequence(key),self); shortcut.activated.connect(lambda index=i:self.play(index)); self.key_bindings.append(shortcut)
        main.addLayout(grid,1)
        owner=QLabel("Desenvolvedor Marcelo Soares"); owner.setStyleSheet("background:transparent;border:0;font-size:11pt;font-weight:400;color:#f2f2f2;padding-right:4px"); owner.setAlignment(Qt.AlignmentFlag.AlignRight); main.addWidget(owner)
        self.set_volume(self.volume.value())
    def refresh(self):
        for i,cart in enumerate(self.carts):
            item=self.config.data["carts"][i]; cart.name(item.get("name","")); cart.set_color(item.get("color",""))
    def refresh_shortcuts(self):
        keys=self.config.data.get("shortcuts",DEFAULT_KEYS)
        for i,key in enumerate(keys): self.key_bindings[i].setKey(QKeySequence(key)); self.carts[i].set_shortcut(key)
    def refresh_identity(self):
        name=self.config.data.get("app_name","MBS").strip() or "MBS"
        self.brand.setText(f'CARTUCHEIRA <span style="color:#ff8a00">{name}</span>'); self.logo_name.setText(name); self.setWindowTitle(f"Cartucheira {name}")
        image=QImage(str(self.config.resolve_symbol()))
        if self.config.data.get("symbol","").startswith("preset:") and image.height()>150:
            image=image.copy(55,45,max(1,image.width()-110),105)
        for y in range(image.height()):
            for x in range(image.width()):
                color=image.pixelColor(x,y)
                if max(color.red(),color.green(),color.blue())<58: color.setAlpha(0); image.setPixelColor(x,y,color)
        self.logo_image.setPixmap(QPixmap.fromImage(image).scaled(105,72,Qt.AspectRatioMode.KeepAspectRatio,Qt.TransformationMode.SmoothTransformation))
    def play(self,index):
        if self.current==index and self.audio.busy():
            if not self.fading:self.fading=True; self.audio.fadeout(650)
            return
        item=self.config.data["carts"][index]; path=self.config.resolve(item.get("audio",""))
        if not path:return
        try:
            if self.current is not None:self.carts[self.current].playing(False)
            self.audio.play(path,self.volume.value()); self.current=index; self.elapsed=0; self.fading=False; self.carts[index].playing(True)
        except Exception as exc: QMessageBox.warning(self,"Áudio",f"Não foi possível reproduzir este áudio.\n\n{exc}")
    def stop(self):
        self.audio.stop()
        if self.current is not None:self.carts[self.current].playing(False)
        self.current=None; self.elapsed=0; self.fading=False
    def toggle_lock(self):
        self.locked=not self.locked; self.lock_button.setText("🔓  DESBLOQUEAR" if self.locked else "🔒  BLOQUEAR"); self.lock_button.setProperty("locked",self.locked)
        self.lock_button.style().unpolish(self.lock_button); self.lock_button.style().polish(self.lock_button)
        for control in self.program_controls: control.setEnabled(not self.locked)
        for cart in self.carts: cart.set_locked(self.locked)
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
        duration=max(.01,self.audio.duration); cart=self.carts[self.current]; cart.set_time(self.stamp(self.elapsed),self.stamp(duration)); cart.set_progress(self.elapsed/duration*1000); cart.set_spectrum(self.audio.spectrum(self.elapsed,len(cart.bars)))
    def cart_menu(self,index):
        menu=QMenu(self); change=QAction("Trocar áudio…",self); rename=QAction("Renomear…",self); color=QAction("Alterar cor…",self); shortcut=QAction("Alterar atalho…",self); clear=QAction("Limpar",self)
        change.triggered.connect(lambda:self.change_audio(index)); rename.triggered.connect(lambda:self.rename(index)); color.triggered.connect(lambda:self.change_color(index)); shortcut.triggered.connect(lambda:self.change_shortcut(index)); clear.triggered.connect(lambda:self.clear(index))
        menu.addActions([change,rename,color,shortcut]); menu.addSeparator(); menu.addAction(clear); menu.exec(self.carts[index].mapToGlobal(self.carts[index].rect().topRight()))
    def change_audio(self,index):
        filename,_=QFileDialog.getOpenFileName(self,"Selecionar áudio","","Áudios (*.wav *.mp3 *.ogg);;Todos (*.*)")
        if filename:self.config.set_audio(index,Path(filename))
    def rename(self,index):
        value=self.config.data["carts"][index].get("name",""); name,ok=QInputDialog.getText(self,"Renomear cartucho","Nome personalizado:",text=value)
        if ok:self.config.data["carts"][index]["name"]=name.strip()[:40]; self.config.write(); self.carts[index].name(name.strip()[:40])
    def change_color(self,index):
        current=QColor(self.config.data["carts"][index].get("color") or "#303338"); chosen=QColorDialog.getColor(current,self,"Cor do cartucho")
        if chosen.isValid(): self.config.data["carts"][index]["color"]=chosen.name(); self.config.write(); self.carts[index].set_color(chosen.name())
    def change_shortcut(self,index):
        current=self.config.data["shortcuts"][index]; value,ok=QInputDialog.getText(self,"Alterar atalho",f"Novo atalho para o cartucho {index+1:02}:",text=current)
        if not ok:return
        sequence=QKeySequence(value.strip()); normalized=sequence.toString()
        if sequence.isEmpty(): QMessageBox.warning(self,"Atalho","Informe uma tecla ou combinação válida."); return
        if normalized in self.config.data["shortcuts"] and normalized!=current: QMessageBox.warning(self,"Atalho","Este atalho já pertence a outro cartucho."); return
        self.config.data["shortcuts"][index]=normalized; self.config.write(); self.key_bindings[index].setKey(sequence); self.carts[index].set_shortcut(normalized)
    def settings_menu(self,button):
        menu=QMenu(self); rename_app=QAction("Alterar nome da cartucheira…",self); symbol=QAction("Trocar símbolo…",self); device=QAction("Saída de som…",self); restore=QAction("Restaurar configurações originais",self); about=QAction("Sobre",self)
        rename_app.triggered.connect(self.change_app_name); symbol.triggered.connect(self.change_symbol); device.triggered.connect(self.choose_device); restore.triggered.connect(self.restore_defaults); about.triggered.connect(lambda:QMessageBox.about(self,"Cartucheira MBS","Cartucheira MBS v0.1\nSistema profissional de áudio para rádio e estúdio.\nNormalização automática ativada."))
        menu.addActions([rename_app,symbol,device]); menu.addSeparator(); menu.addAction(restore); menu.addSeparator(); menu.addAction(about); menu.exec(button.mapToGlobal(button.rect().bottomLeft()))
    def change_app_name(self):
        current=self.config.data.get("app_name","MBS"); name,ok=QInputDialog.getText(self,"Nome da cartucheira","Novo nome:",text=current)
        if ok and name.strip(): self.config.data["app_name"]=name.strip()[:24]; self.config.write(); self.refresh_identity()
    def change_symbol(self):
        filename,_=QFileDialog.getOpenFileName(self,"Selecionar símbolo","","Imagens (*.png *.jpg *.jpeg *.bmp *.webp)")
        if filename:self.config.set_symbol(Path(filename)); self.refresh_identity()
    def choose_device(self):
        devices=self.audio.devices(); current=self.config.data.get("output_device","Padrão do sistema"); selected,ok=QInputDialog.getItem(self,"Saída de som","Dispositivo:",devices,max(0,devices.index(current) if current in devices else 0),False)
        if ok:
            try:self.stop(); self.audio.set_device(selected); self.audio.volume(self.volume.value()); self.config.data["output_device"]=selected; self.config.write()
            except Exception as exc:QMessageBox.warning(self,"Saída de som",f"Não foi possível usar este dispositivo.\n\n{exc}")
    def restore_defaults(self):
        if QMessageBox.question(self,"Restaurar cartuchos","Restaurar nomes, cores e efeitos originais dos 36 cartuchos?")==QMessageBox.StandardButton.Yes:
            self.stop(); self.config.data=Config.defaults(); self.config.write(); self.volume.setValue(80); self.theme.setCurrentText("Escuro Padrão"); self.refresh(); self.refresh_identity(); self.refresh_shortcuts()
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
            try:self.stop(); self.config.import_(Path(filename)); self.volume.setValue(self.config.data.get("volume",80)); self.theme.setCurrentText(self.config.data.get("theme","Escuro Padrão")); self.refresh(); self.refresh_identity(); self.refresh_shortcuts(); QMessageBox.information(self,"Backup","Programação importada com sucesso.")
            except Exception as exc:QMessageBox.critical(self,"Backup",str(exc))
    def closeEvent(self,event:QCloseEvent): self.config.write(); self.audio.close(); event.accept()
