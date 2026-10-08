import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import app as api
import services
class APITests(unittest.TestCase):
    def setUp(self):
        import result_cache
        result_cache._results.clear()
        self.client = api.app.test_client()
    def test_health(self): self.assertEqual(self.client.get('/health').json, {'status':'ok'})
    def test_blank_and_long_queries(self):
        for query in ['', ' '*5, 'x'*301]: self.assertEqual(self.client.get('/explore',query_string={'q':query}).status_code,400)
    def test_errors_hide_provider_details(self):
        with patch.object(api,'explore_query',side_effect=RuntimeError('private provider diagnostic')):
            response = self.client.get('/explore?q=fear')
        self.assertEqual(response.status_code,500)
        self.assertNotIn('detail',response.json)
        self.assertNotIn('private',str(response.json))
    def test_bad_input_message(self):
        with patch.object(api,'explore_query',side_effect=ValueError('Could not find this verse.')):
            self.assertEqual(self.client.get('/explore?q=John+3:999').status_code,400)
    def test_empty_topic_subthemes_are_not_success(self):
        analysis = SimpleNamespace(center_label='Nothing',normalized_query='nothing',short_description='',search_terms=['nothing'],preferred_books=[],candidate_references=[],subthemes=[SimpleNamespace(name='Theme',description='',search_terms=['nothing'])])
        with patch.object(services,'search_bible_text',return_value=[]):
            with self.assertRaises(ValueError): services.build_topic_graph('nothing',analysis)
    def test_optional_entity_outage_does_not_block_topic(self):
        analysis = SimpleNamespace(query_type='topic')
        with patch.object(services,'find_person',side_effect=RuntimeError('offline')), patch.object(services,'find_place',side_effect=RuntimeError('offline')), patch.object(services,'find_event',side_effect=RuntimeError('offline')), patch.object(services,'analyze_query',return_value=analysis), patch.object(services,'build_topic_graph',return_value={'ok':True}):
            self.assertEqual(services.explore_query('fear'),{'ok':True})
if __name__ == '__main__': unittest.main()
