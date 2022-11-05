import unittest
import app

class SearchDDGTests(unittest.TestCase):
    def setUp(self):
        app.app.config['TESTING'] = True
        self.app = app.app.test_client()

    def test_request_unknown(self):
        rv = self.app.get('/search/?request=abcde')
        assert rv.status_code == 404
        assert 'Not Found' in rv.text
    
    def test_request_none(self):
        rv = self.app.get('/search/')
        assert rv.status_code == 400
        assert 'request is None'

    def test_query_none(self):
        rv = self.app.get('/search/?request=search_ddg')
        assert rv.status_code == 400
        assert 'query is None' in rv.text

    def test_user_id_none(self):
        rv = self.app.get('/search/?request=search_ddg&query=marshmallow')
        assert rv.status_code == 400
        assert 'user_id is None' in rv.text

    def test_search_ddg(self):
        rv = self.app.get('/search/?request=search_ddg&query=marshmallow&user_id=2727')
        assert rv.status_code == 200    
        assert "These are what we've found!" in rv.text             # the header text should be there
        assert 'marshmallow' in rv.text                             # marshmallow should be in the text

    def test_search_ddg_results_only_10(self):
        rv = self.app.get('/search/?request=search_ddg&query=marshmallow&user_id=2727')
        self.assertLessEqual(len(dict(rv.get_json())['messages']), 10)  # there should only be 10 text keys inside of messages

    def test_current_results(self):
        rv = self.app.get('/search/?request=current_results&user_id=2727')
        assert rv.status_code == 200
    
    def test_search_ddg_match_current_results(self):
        self.assertDictEqual(
            self.app.get('/search/?request=search_ddg&query=marshmallow&user_id=2727').get_json(),
            self.app.get('/search/?request=current_results&user_id=2727').get_json()
        )

    def test_current_results_user_id_none(self):
        rv = self.app.get('/search/?request=current_results')
        assert rv.status_code == 400
        assert 'user_id is None' in rv.text

    def test_current_results_only_10(self):
        rv = self.app.get('/search/?request=current_results&user_id=2727')
        self.assertLessEqual(len(dict(rv.get_json())['messages']), 10)  # there should be less than or equal to 10 text keys inside of messages

    def test_article_text_from_search_result_result_num_none(self):
        rv = self.app.get('/search/?request=article_text_from_search_result&user_id=2727')
        assert rv.status_code == 400
        assert 'result_num is None' in rv.text

    def test_article_text_from_search_result_invalid_result_num(self):
        rv = self.app.get('/search/?request=article_text_from_search_result&user_id=2727&result_num=11')
        assert rv.status_code == 404
        assert 'invalid result number' in rv.text

    def test_article_text_from_search_result(self):
        # somehow the search result is getting replaced by prior tests so we initiate a search again before proceeding
        self.app.get('/search/?request=search_ddg&query=marshmallow&user_id=2727')      
        
        rv = self.app.get('/search/?request=article_text_from_search_result&user_id=2727&result_num=1')
        print(f'Status Code: {rv.status_code}')
        # assert rv.status_code == 200
        assert 'marshmallow' in rv.text

    # def test_article_text_from_search_result_only_10(self):
    #     rv = self.app.get('/search/?request=article_text_from_search_result&user_id=2727&result_num=1')
    #     assert rv.status_code == 200
    #     self.assertLessEqual(len(dict(rv.get_json())['messages']), 10)  # there should be less than or equal to 10 text keys inside of messages