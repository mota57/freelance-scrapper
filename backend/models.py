from pysondb import PysonDB
from pysondb.errors import IdDoesNotExistError
from json import JSONEncoder
from flask import Flask, jsonify,  make_response, Response


class RestApiResponse:
    def __init__(self):
        self.status = 200
        self.message = 'success'
        self.data = None

    def to_dict(self):
        return {'status': self.status, 'message': self.message, 'data': self.data}

    def ok(self):
        self.to_dict()
        return jsonify()

    def not_found(error: str = None) -> Response:
        if error is None:
            error = "Resource not found"
        return RestApiResponse.custom_error(error, 404)

    def custom_error(message, status_code) -> Response:
        return make_response(jsonify(message), status_code)


class ContextAdapter:
    def __init__(self, db: PysonDB):
        self.db = db

    def get_all(self) -> dict:
        records = self.db.get_all()
        entries = []
        for key in records.keys():
            records[key]['id'] = key
            entries.append(records[key])
        print(entries)
        return entries


    def get_by_id(self,  id) -> dict:
        try:
            record = self.db.get_by_id(id)
            record['id'] = id
            return record
        except IdDoesNotExistError:
            return None

    def add(self, record: dict) -> str:
        return self.db.add(record)

    def update_by_id(self, id: str, record: dict) -> str:
        self.db.update_by_id(id, record)
        return id

    def delete_by_id(self, id: str):
        self.db.delete_by_id(id)



def get_db() -> ContextAdapter:
    return ContextAdapter(PysonDB('keyword.json'))