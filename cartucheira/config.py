import json, os, shutil, sys, uuid, zipfile
from pathlib import Path

NAMES = [
 "Bip de chamada","Vinheta curta","Abertura de transmissão","Encerramento","Alerta curto","Sinal de atenção",
 "Transição de bloco","Chamada de operador","Ruído de sintonia","Identificação de estação","Efeito de passagem","Sinal eletrônico",
 "Aviso curto","Campainha rádio","Pulso de comunicação","Confirmação","Entrada de boletim","Saída de boletim",
 "Efeito digital","Efeito analógico","Rádio antigo","Interferência curta","Frequência abrindo","Frequência fechando",
 "Alerta técnico","Chamada urgente","Sinal de conexão","Efeito de transmissão","Efeito de encerramento","Transição musical",
 "Impacto sonoro","Sinal especial","Efeito ambiente","Chamada extra","Reserva","Reserva"
]

def resource(relative):
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent)) / relative

def app_data():
    base = Path(os.getenv("LOCALAPPDATA", Path.home() / ".cartucheira_eder")) / "Cartucheira EDER"
    (base / "audio").mkdir(parents=True, exist_ok=True)
    return base

class Config:
    def __init__(self, root=None):
        self.root = Path(root) if root else app_data()
        self.audio_dir = self.root / "audio"
        self.audio_dir.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "config.json"
        self.data = self.load()
    @staticmethod
    def defaults():
        return {"version":1,"volume":80,"theme":"Escuro Padrão","carts":[{"name":n,"audio":f"preset:{i+1:02}.wav","color":"#ff8a00"} for i,n in enumerate(NAMES)]}
    def load(self):
        if self.path.exists():
            try:
                data=json.loads(self.path.read_text(encoding="utf-8"))
                if len(data.get("carts",[]))==36:
                    data.setdefault("theme","Escuro Padrão")
                    for cart in data["carts"]: cart.setdefault("color","#ff8a00")
                    return data
            except Exception: pass
            shutil.copy2(self.path,self.path.with_suffix(".json.corrompido"))
        data=self.defaults(); self.write(data); return data
    def write(self,data=None):
        data=data or self.data
        tmp=self.path.with_suffix(".tmp")
        tmp.write_text(json.dumps(data,ensure_ascii=False,indent=2),encoding="utf-8")
        tmp.replace(self.path)
    def resolve(self,value):
        if not value: return None
        path=resource("assets/audio/"+value[7:]) if value.startswith("preset:") else self.audio_dir/Path(value).name
        return path if path.exists() else None
    def set_audio(self,index,source):
        old=self.data["carts"][index].get("audio","")
        target=self.audio_dir/f"cart_{index+1:02}_{uuid.uuid4().hex[:8]}{source.suffix.lower()}"
        shutil.copy2(source,target); self.data["carts"][index]["audio"]=target.name
        self._unused(old); self.write()
    def clear(self,index):
        old=self.data["carts"][index].get("audio","")
        color=self.data["carts"][index].get("color","#ff8a00")
        self.data["carts"][index]={"name":"","audio":"","color":color}; self._unused(old); self.write()
    def _unused(self,value):
        if value and not value.startswith("preset:") and not any(c.get("audio")==value for c in self.data["carts"]):
            (self.audio_dir/Path(value).name).unlink(missing_ok=True)
    def export(self,destination):
        self.write()
        with zipfile.ZipFile(destination,"w",zipfile.ZIP_DEFLATED) as z:
            z.write(self.path,"config.json")
            for f in self.audio_dir.iterdir():
                if f.is_file(): z.write(f,"audio/"+f.name)
    def import_(self,source):
        with zipfile.ZipFile(source) as z:
            if "config.json" not in z.namelist(): raise ValueError("Este não é um backup da Cartucheira EDER.")
            data=json.loads(z.read("config.json").decode("utf-8"))
            if len(data.get("carts",[]))!=36: raise ValueError("Backup incompatível.")
            for name in z.namelist():
                p=Path(name)
                if len(p.parts)==2 and p.parts[0]=="audio": (self.audio_dir/p.name).write_bytes(z.read(name))
        self.data=data; self.write()
