import sys
import unittest
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
from time import sleep
from unittest.mock import patch
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from comparison import validate_report
import result_cache
import services
import app as api

def graph(reference, text):
    return {'query':reference,'center':'v','centerLabel':reference,'queryType':'verse','nodes':[{'data':{'id':'v','type':'verse','label':reference,'reference':reference,'text':text}}],'edges':[]}
def report():
    return {'overview':'Both discuss trust.','similarities':[{'title':'Trust','explanation':'Faith connects these passages.','left_refs':['John 3:16'],'right_refs':['Romans 8:28']}], 'differences':[], 'study_questions':['How is trust expressed?']}
class ComparisonTests(unittest.TestCase):
    def setUp(self): result_cache._results.clear()
    def test_grounded_report(self):
        self.assertEqual(validate_report(report(),graph('John 3:16','believe'),graph('Romans 8:28','love'))['method'],'ai')
    def test_wrong_side_citation_rejected(self):
        value=report();value['similarities'][0]['left_refs']=['Romans 8:28']
        with self.assertRaises(ValueError): validate_report(value,graph('John 3:16','believe'),graph('Romans 8:28','love'))
    def test_empty_evidence_and_missing_refs_rejected(self):
        value=report();value['similarities'][0]['left_refs']=[]
        with self.assertRaises(ValueError): validate_report(value,graph('John 3:16','believe'),graph('Romans 8:28','love'))
    def test_cache_coalesces_and_returns_independent_copies(self):
        calls=[]
        def build(): calls.append(1);sleep(.04);return {'items':[1]}
        with ThreadPoolExecutor(max_workers=4) as pool:
            values=list(pool.map(lambda _:result_cache.cached_result('same',build),range(4)))
        self.assertEqual(len(calls),1);values[0]['items'].append(2)
        self.assertEqual(result_cache.cached_result('same',build),{'items':[1]})
    def test_fast_verse_skips_ai(self):
        with patch.object(services,'get_verse_text',return_value='Verse'),patch.object(services,'get_cross_references',return_value=[]),patch.object(services,'get_chapter_entities',return_value={}),patch.object(services,'add_ai_explanations') as ai:
            services.build_verse_graph('John 3:16',{'book':'JHN','chapter':3,'verse':16},with_explanations=False)
        ai.assert_not_called()
    def test_common_topic_fast_path_skips_ai_and_entity_indexes(self):
        with patch.object(services,'build_topic_graph',return_value={'ok':True}) as build,patch.object(services,'analyze_query') as ai,patch.object(services,'find_person') as entity:
            self.assertEqual(services.explore_query('fear',with_explanations=False),{'ok':True})
        ai.assert_not_called();entity.assert_not_called()
        self.assertEqual(build.call_args.kwargs,{'with_explanations':False})
    def test_compare_route_validation_and_cached_call(self):
        client=api.app.test_client()
        self.assertEqual(client.post('/compare',json={'left':'','right':'hope'}).status_code,400)
        with patch.object(api,'graph_result',return_value={}),patch.object(api,'compare_graphs',return_value=report()) as compare:
            self.assertEqual(client.post('/compare',json={'left':'fear','right':'hope'}).status_code,200)
            self.assertEqual(client.post('/compare',json={'left':'fear','right':'hope'}).status_code,200)
            self.assertEqual(compare.call_count,1)
    def test_compare_failure_is_safe(self):
        with patch.object(api,'graph_result',side_effect=RuntimeError('secret diagnostic')):
            response=api.app.test_client().post('/compare',json={'left':'fear','right':'hope'})
        self.assertEqual(response.status_code,503);self.assertNotIn('secret',str(response.json))
if __name__=='__main__': unittest.main()
