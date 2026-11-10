import tempfile
import unittest
from pathlib import Path
from creator_growth_analyst.__main__ import load_rows,analyze,rate

class TestGrowth(unittest.TestCase):
    def test_sample(self):
        p=Path(__file__).parents[1]/'examples'/'sample-posts.csv'
        rows,fields=load_rows(p)
        self.assertEqual(len(rows),10)
        self.assertAlmostEqual(rows[0]['save_per_view'],106/9031)
        md,insights=analyze(rows,fields)
        self.assertIn('X · 4条',md)
        self.assertIn('youtube',insights['platforms'])
        self.assertIn('下一轮实验',md)
    def test_missing_not_zero(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'posts.csv'
            p.write_text('platform,title,views,saves\nx,A,100,\nx,B,200,20\n',encoding='utf-8')
            rows,fields=load_rows(p)
            self.assertIsNone(rows[0]['save_per_view'])
            self.assertIsNone(rows[0]['engagement_per_view'])
            self.assertEqual(rows[1]['save_per_view'],0.1)
    def test_percent(self):
        self.assertEqual(rate('64%','completion_rate',2),0.64)
        self.assertEqual(rate('0.64','completion_rate',2),0.64)
        self.assertEqual(rate('64','completion_rate',2),0.64)
    def test_invalid(self):
        with tempfile.TemporaryDirectory() as t:
            p=Path(t)/'posts.csv'
            p.write_text('platform,title,views\nx,A,-1\n',encoding='utf-8')
            with self.assertRaises(ValueError):load_rows(p)

if __name__=='__main__':unittest.main()
