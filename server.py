from flask import Flask, request, abort, jsonify


def create_app(config=None):
    app = Flask(__name__)
    app.config.from_mapping(
        DATABASE='database.db'
    )
    if config:
        # load the config if passed in
        app.config.from_mapping(config)

    app.route('/', methods=['POST'])(handler)

    return app


def handler():
    payload = request.json
    post_type = payload.get("post_type")

    type_key = payload.get(
        {'message': 'message_type',
         'notice': 'notice_type',
         'event': 'event',  # compatible with v3.x
         'request': 'request_type',
         'meta_event': 'meta_event_type'}.get(post_type)
    )
    if not type_key:
        abort(400)

    if post_type != "message":
        return ''

    from . import coolq
    raw_message = payload.get("message").strip()
    if raw_message[0] == '/':
        message = raw_message[1:].split()
        command = message[0]
        args = message[1:]
        try:
            # public operation
            coolq.log(payload)
            coolq.remove_timeout_user(payload['user_id'], payload['time'], 48)

            response = getattr(coolq, command)(payload, args)
        except AttributeError:
            response = ''
    else:
        response = ''
    return jsonify(response) if isinstance(response, dict) else ''
