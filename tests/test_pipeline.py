import importlib.util, unittest
from pathlib import Path
import numpy as np
spec=importlib.util.spec_from_file_location('pipeline',Path(__file__).resolve().parents[1]/'src/pipeline.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class ContractTests(unittest.TestCase):
    def test_dirty_input_reconciles(self):
        raw=m.generate_raw(); clean,rejects,dupes=m.clean(raw)
        self.assertEqual(len(raw),len(clean)+len(rejects)+dupes)
        self.assertEqual(len(rejects),1); self.assertEqual(dupes,1)
        self.assertTrue(clean.observation_id.is_unique)
    def test_conflicting_ids_fail(self):
        raw=m.generate_raw().iloc[:20].copy(); raw.loc[1,'observation_id']=raw.loc[0,'observation_id']
        with self.assertRaises(ValueError): m.clean(raw)
    def test_interval_handles_no_effect(self):
        ci=m.bootstrap_difference(np.ones(20),np.ones(20),np.random.default_rng(1))
        self.assertEqual(ci,[0.,0.])
if __name__=='__main__': unittest.main()
