import tempfile,unittest
from pathlib import Path
from cartucheira.config import Config
class TestConfig(unittest.TestCase):
 def test_defaults(self):
  with tempfile.TemporaryDirectory() as d:self.assertEqual(len(Config(d).data['carts']),36)
 def test_clear_and_reload(self):
  with tempfile.TemporaryDirectory() as d:
   c=Config(d);c.clear(0);self.assertEqual(Config(d).data['carts'][0],{'name':'','audio':'','color':''})
 def test_backup(self):
  with tempfile.TemporaryDirectory() as d:
   p=Path(d);a=Config(p/'a');a.data['carts'][0]['name']='Teste';f=p/'a.eder';a.export(f);b=Config(p/'b');b.import_(f);self.assertEqual(b.data['carts'][0]['name'],'Teste')
if __name__=='__main__':unittest.main()
