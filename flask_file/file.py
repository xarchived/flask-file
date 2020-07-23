import json
from os import urandom
from typing import Union

from flask import Flask, Blueprint, request, send_file, current_app

from flask_file.exceptions import *


class File(object):
    _app: Union[Flask, Blueprint]

    def __init__(self, app: Union[Flask, Blueprint] = None):
        if app is not None:
            self.init_app(app)

    def init_app(self, app: Union[Flask, Blueprint]) -> None:
        self._app = app
        self.enhance(app)

    @staticmethod
    def enhance(app: Union[Flask, Blueprint]) -> None:
        @app.route('/file/upload', methods=['POST'])
        def upload():
            if 'file' not in request.files:
                raise FileNotProvided(f'File not provided (files={list(request.files)})')

            file = request.files['file']
            file_id = int.from_bytes(urandom(13), byteorder='little')
            file_path = f'{current_app.config["FILES_DIRECTORY"]}/{file_id}'

            if file:
                info = {
                    'filename': file.filename or file_id,
                    'content_type': file.content_type,
                    'mime_type': file.mimetype
                }

                with open(file_path + '.json', 'w') as f:
                    json.dump(info, f, ensure_ascii=True)

                file.save(file_path + '.data')

            return str(file_id)

        @app.route('/file/<int:file_id>')
        def download(file_id: int):
            file_path = f'{current_app.config["FILES_DIRECTORY"]}/{file_id}'
            try:
                with open(file_path + '.json') as f:
                    info = json.load(f)
            except FileNotFoundError:
                raise FileNotFound(f'File not found (id={file_id})')

            return send_file(file_path + '.data', as_attachment=True, attachment_filename=info['filename'])
