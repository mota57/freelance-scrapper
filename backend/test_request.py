import requests
import json
import unittest

class TestRequestMethods(unittest.TestCase):

    api_url = 'http://localhost:5000/keywords'

    def test_get(self):
        # test get all
        res_get = requests.get(self.api_url)
        print('request::url::'+str(res_get.url)+ ', request::get::status_code :: [' + str(res_get.status_code) +']')
        assert res_get.status_code == 200

    def test_crud(self):
        # test post
        res_post = requests.post(self.api_url, json=dict(id ='', name='keyword1'))
        print('request::post::'+str(res_post.url)+ ', request::post::status_code :: [' + str(res_post.status_code) +']')
        print(res_post.text)
        assert res_post.status_code == 200

        #test get after create
        keyword_id = json.loads(res_post.text)['data']
        res_get2 = requests.get(self.api_url+'/'+keyword_id)
        print('request::get_by_id::'+str(res_get2.url)+ ', request::get_by_id::status_code :: [' + str(res_get2.status_code) +']')
        assert res_get2.status_code == 200
        keyword = json.loads(res_get2.text)['data']
        assert keyword['name'] == 'keyword1'
        assert keyword['id'] == keyword_id

        keyword['name'] = 'keyword1.1'
        print('record before update ' + str(keyword))
        res = requests.put(self.api_url, json=keyword)
        print(res.text)
        print('request::put::'+str(res.url)+ ', request::put::status_code :: [' + str(res.status_code) +']')
        assert res.status_code == 200

        # test was changed after update
        res_get = requests.get(self.api_url+'/'+keyword['id'])
        print('request::get_by_id::'+str(res.url)+ ', request::get_by_id::status_code :: [' + str(res.status_code) +']')
        # print(res_get.text)
        assert keyword['name'] == 'keyword1.1'
        assert keyword['id'] == keyword_id
        assert res_get.status_code == 200

