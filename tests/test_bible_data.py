import importlib.util
import unittest
from pathlib import Path
path = Path(__file__).resolve().parents[1] / 'bible_data.py'
spec = importlib.util.spec_from_file_location('bible_data', path)
b = importlib.util.module_from_spec(spec)
spec.loader.exec_module(b)
class PassageTests(unittest.TestCase):
    def setUp(self):
        b.get_chapter = lambda *args: {'chapter': {'content': [{'type':'verse','number':i,'text':f'Text {i}'} for i in range(1,5)]}}
    def test_complete_range(self):
        self.assertEqual(b.get_passage_text('ROM',5,2,4),'[2] Text 2 [3] Text 3 [4] Text 4')
    def test_single(self):
        self.assertEqual(b.get_passage_text('ROM',5,2),'Text 2')
    def test_missing_and_reversed(self):
        with self.assertRaises(ValueError): b.get_passage_text('ROM',5,3,6)
        with self.assertRaises(ValueError): b.get_passage_text('ROM',5,4,2)
    def test_nested_complete_translation(self):
        from unittest.mock import patch
        fixture={'books':[{'id':'JHN','chapters':[{'chapter':{'number':3,'content':[{'type':'verse','number':16,'text':'God so loved the world.'}]}}]}]}
        b.verse_corpus.cache_clear()
        with patch.object(b,'get_complete_translation',return_value=fixture):
            self.assertEqual(b.verse_corpus()[0]['label'],'John 3:16')
        b.verse_corpus.cache_clear()
    def test_word_boundaries_and_prefixes(self):
        b.verse_corpus = lambda: [{'normalized':text,'book':'JHN','chapter':1,'verse':i,'text':text} for i,text in enumerate(['glove','love','lovely','fearful','unfearful'],1)]
        self.assertEqual([r['text'] for r in b.search_bible_text(['love'])],['love','lovely'])
        self.assertEqual([r['text'] for r in b.search_bible_text(['fear'])],['fearful'])
if __name__ == '__main__': unittest.main()
