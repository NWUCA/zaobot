import os
import time
from flask import Flask, request, abort, jsonify, current_app
from . import db
from . import directive, utils


def create_app(config=None):
    app = Flask(__name__)

    if config:
        # load the config if passed in
        app.config.from_mapping(config)
    else:
        app.config.from_mapping(
            DATABASE=os.path.join(app.instance_path, 'database.db')
        )
        app.config.from_pyfile(os.path.join(os.path.dirname(app.root_path), 'settings.cfg'))

    # print(os.getcwd())
    db.init_database(app)

    app.route('/', methods=['POST'])(handler)
    app.route('/webhook', methods=['POST'])(webhook_handler)

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

    if payload['message_type'] == 'group' and \
            payload['group_id'] not in current_app.config['ALLOWED_GROUP']:
        abort(400)

    pre_process(payload)

    raw_message = payload.get("message").strip()
    if raw_message[0] == '/':
        message = raw_message[1:].split()
        command = message[0]
        args = message[1:]
        try:
            # map command to directive.py and execute it.
            response = getattr(directive, command)(payload, args)
        except AttributeError as e:
            print(e)
            response = ''
    else:
        response = ''
    return jsonify(response) if isinstance(response, dict) else ''


# TODO 异步执行
def pre_process(payload):
    utils.log(payload)
    # utils.accumulate_exp(payload)

    if payload['message_type'] == 'group':
        utils.find_cai(payload)
        if payload['group_id'] == current_app.config['FORWARDED_QQ_GROUP_ID']:
            utils.send_to_tg(payload)


def webhook_handler():
    context = {"group_id": current_app.config['WEBHOOK_NOTIFICATION_GROUP'], "time": time.time()}

    # DOC: https://developer.github.com/webhooks/event-payloads/
    if request.headers.get("X-GitHub-Event") == 'check_run':
        payload = request.json
        if payload['action'] != "completed":
            return ""
        check_run = payload['check_run']
        message = f"CI job {check_run['name']} has completed: {check_run['conclusion']}."
        utils.send(context, message)
    elif request.headers.get("X-GitHub-Event") == 'push':
        payload = request.json
        commits = payload['commits']
        message = f"{payload['sender']['login']} has pushed {len(commits)} commit(s)" \
                  f" to my repository:"
        for commit in commits:
            message += f"\n{commit['id'][:6]} {commit['message']}"
        utils.send(context, message)
    return ""
