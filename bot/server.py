from flask import Flask, request, abort, jsonify
from . import db
import os


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE=os.path.join(app.instance_path, 'database.db')
        # DATABASE='database.db'
    )
    if config:
        # load the config if passed in
        app.config.from_mapping(config)
    print(os.getcwd())
    db.init_database(app)

    app.route('/', methods=['POST'])(handler)

    app.teardown_appcontext(db.close_db)

    return app


def handler():
    payload = request.json
    post_type = payload.get("post_type")

    # type_key = payload.get(
    #     {'message': 'message_type',
    #      'notice': 'notice_type',
    #      'event': 'event',  # compatible with v3.x
    #      'request': 'request_type',
    #      'meta_event': 'meta_event_type'}.get(post_type)
    # )
    # if not type_key:
    #     abort(400)

    if post_type != "message":
        abort(400)

    from . import directive
    raw_message = payload.get("message").strip()
    if raw_message[0] == '/':
        message = raw_message[1:].split()
        command = message[0]
        args = message[1:]
        try:
            # public operation
            directive.log(payload)
            # coolq.accumulate_exp(payload)

            response = getattr(directive, command)(payload, args)
        except AttributeError as e:
            print(e)
            response = ''
    else:
        response = ''
    return jsonify(response) if isinstance(response, dict) else ''
