import app
import unittest

class CharlieWadeTests(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def test_unknown_path(self):
        rv = self.app.get('/charlie_wading/')
        assert rv.status_code == 404
        assert 'Not Found' in rv.text

    def test_no_args(self):
        rv = self.app.get('/charlie_wade/')
        assert rv.status_code == 400
        assert 'request is None' in rv.text

    def test_request_unknown(self):
        rv = self.app.get('/charlie_wade/?request=abcde')
        assert rv.status_code == 404
        assert 'Not Found' in rv.text

    def test_chapter_none(self):
        rv = self.app.get('/charlie_wade/?request=chapter')
        assert rv.status_code == 400
        assert 'chapter is None' in rv.text

    def test_chapter_that_do_not_exist(self):
        rv = self.app.get('/charlie_wade/?request=chapter&chapter=acbde')
        assert rv.status_code == 404
        assert 'not found' in rv.text

    def test_chapter(self):
        rv = self.app.get('/charlie_wade/?request=chapter&chapter=2891')
        assert rv.status_code == 200    
        self.assertLessEqual(len(dict(rv.get_json())['messages']), 10)  # there should be less than or equal to 10 text keys inside of messages
        assert '2891' in rv.text                                    # 2891 should be in the text

    def test_latest_chapter(self):
        rv = self.app.get('/charlie_wade/?request=latest_chapter')
        assert rv.status_code == 200
        self.assertLessEqual(len(dict(rv.get_json())['messages']), 10)  # there should be less than or equal to 10 text keys inside of messages

    def test_chapters(self):
        rv = self.app.get('/charlie_wade/?request=chapters')
        assert rv.status_code == 200
        self.assertLessEqual(len(dict(rv.get_json())['messages']), 10)  # there should be less than or equal to 10 text keys inside of messages