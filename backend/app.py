
from pysondb import PysonDB
from flask import Flask, jsonify, request, make_response, Response , send_from_directory
from flask_cors import CORS
import asyncio
# import threading
import models
import scrape_etsy
from datetime import datetime
import logging
import os
# import utils

# log = utils.buildLogger('flas_cors.log')

app = Flask(__name__, static_folder='static/')
cors = CORS(app, resources={r"/*": {"origins": "*"}})


@app.errorhandler(500)
def server_error(e):
    logging.exception('An error occurred during a request. %s', e)
    return "An internal error occurred", 500




@app.get('/keywords')
def get_all() -> Response:
    ctx = models.get_db()
    res = models.RestApiResponse()
    records_db = ctx.get_all()
    res.data = records_db
    return jsonify(res.to_dict())

@app.get('/keywords/<keyword_id>')
def get_record_by_id(keyword_id) -> Response:
    ctx = models.get_db()
    res = models.RestApiResponse()
    record = ctx.get_by_id(keyword_id)
    record['id'] = keyword_id
    res.data = record
    return jsonify(res.to_dict())

# create http post method to insert a record
@app.post('/keywords')
def insert_record() -> Response:
    ctx = models.get_db()
    res = models.RestApiResponse()
    request_data = request.get_json()
    print('request_data ' + str(request_data))
    keyword_name = request_data.get('name')
    id = ctx.add({"name": keyword_name, "is_active": True})
    print('id created:: ' + str(id))
    res.data = id
    return jsonify(res.to_dict())


# create http put method to update a record
@app.put('/keywords')
def update_record() -> Response:
    ctx = models.get_db()
    res = models.RestApiResponse()
    request_data = request.get_json()
    print('request_data ' + str(request_data))
    keyword_id = request_data.get('id')
    keyword_name = request_data.get('name')
    is_active = request_data.get('is_active')
    if ctx.get_by_id(keyword_id) is None:
        return models.RestApiResponse.not_found("Keyword not found")
    ctx.update_by_id(keyword_id, {"name": keyword_name, "is_active": is_active})
    res.data = keyword_id
    return jsonify(res.to_dict())


@app.delete('/keywords/<keyword_id>')
def delete_record(keyword_id) -> Response:
    ctx = models.get_db()
    res = models.RestApiResponse()
    res.message = 'Keyword removed!'
    if ctx.get_by_id(keyword_id) is None:
        return models.RestApiResponse.not_found("Keyword not found")
    ctx.delete_by_id(keyword_id)
    return jsonify(res.to_dict())

@app.post('/keywords/export2')
def export_keywords2() -> Response:
    # get all records
    ctx = models.get_db()
    records =  [r for r in ctx.get_all() if r['is_active'] == True]

    # get data from the POST request.
    request_data = request.get_json()
    cookie_erank = request_data.get('cookie_erank')
    pages_per_keyword = int(request_data.get('pages'))
    listings_per_page = int(request_data.get('listings'))

    # call erank data or send 404
    if records is not  None and len(records) > 0:
        names = list(map(lambda x: x['name'], records))
        file_name = 'data_'+ datetime.now().strftime("%d%m%Y_%H_%M_%S") + '.xlsx'

        res = asyncio.run(scrape_etsy.run_etsay_erank_data(names, cookie_erank, pages_per_keyword, listings_per_page, file_name))
        if res:
            return send_from_directory(app.static_folder, file_name, as_attachment=True)
        else:
            return make_response(jsonify({'error': 'something wrong happen, nothing downloaded check the logs'}), 400)
    return make_response(jsonify({'error': 'no keyword listed'}), 400)


@app.get('/keywords/log_scrape_erank')
def get_log_scrape_erank() -> Response:
    f = open("static/log_scrape_erank.log", "r")
    log_content = f.read()
    return make_response(jsonify({'data': log_content}), 200)

@app.post('/keywords/clear_log_scrape_erank')
def clear_log_scrape_erank() -> Response:
    f = open("static/log_scrape_erank.log", "w")
    f.write('')
    return make_response(jsonify({'data': ''}), 200)

if __name__ == '__main__':
    asyncio.run(app.run(port=5000))

