import os
from flask import Flask, request, abort, jsonify, current_app
from bot import db
from bot import utils
from bot.directive import Directive
from bot.context import Context, PrivateContext, GroupContext
from apscheduler.schedulers.background import BackgroundScheduler
from .utils import send


def create_app(config=None):
    app = Flask(__name__)

    if config:
        # load the config if passed in
        app.config.from_mapping(config)
    else:
        app.config.from_mapping(
            DATABASE=os.path.join(app.instance_path, 'database.db')
        )
        if not os.path.exists(app.instance_path):
            os.mkdir(app.instance_path)
        app.config.from_pyfile(os.path.join(os.path.dirname(app.root_path), 'settings.cfg'))

    # print(os.getcwd())
    db.init_database(app)

    app.route('/', methods=['POST'])(handler)
    app.route('/webhook', methods=['POST'])(webhook_handler)

    app.teardown_appcontext(db.close_db)

    init_background_tasks(app.config)

    return app


def init_background_tasks(config):
    apsched = BackgroundScheduler()
    apsched.add_job(init_ky_reminder, args=[config], trigger='cron', hour=7, minute=0)
    apsched.start()


def init_ky_reminder(config):
    from datetime import date
    try:
        ky_date_str = os.environ["KY_DATE"]
        ky_date = date(int(ky_date_str[:4]), int(ky_date_str[4:6]), int(ky_date_str[6:]))
        days_to_ky = (ky_date - date.today()).days
        for group, name in config["ALLOWED_GROUP"].items():
            if '考研' in name:
                send(GroupContext.build(group_id=group), message=f"距离{ky_date_str[:4]}年度考研还有{days_to_ky}天")
    except KeyError:
        for group, name in config["ALLOWED_GROUP"].items():
            if '考研' in name:
                send(GroupContext.build(group_id=group), message="管理员还未设定考研时间，使用 /setky 设定考研时间")


def handler():
    payload = request.json
    post_type = payload.get("post_type")

    if post_type != "message":
        abort(400)

    if payload['message_type'] != 'group' and payload['message_type'] != 'private':
        abort(400)

    if payload['message_type'] == 'group' and \
            payload['group_id'] not in current_app.config['ALLOWED_GROUP']:
        abort(400)

    if payload['message_type'] == 'group':
        context = GroupContext(payload)
    elif payload['message_type'] == 'private':
        context = PrivateContext(payload)

    pre_process(context)

    # map command to Directive class and execute it.
    try:
        if hasattr(Directive, context.directive):
            obj = Directive(context)
            response = getattr(obj, context.directive)()
        else:
            response = ''
    except AttributeError:  # if a message is not a directive
        response = ''

    return jsonify(response) if isinstance(response, dict) else ''


# TODO 异步执行
def pre_process(context: Context):
    utils.log(context)
    utils.accumulate_exp(context)
    utils.randomly_save_message_to_treehole(context)

    if context.message_type == 'group':
        utils.find_cai(context)
        if context.group_id == current_app.config['FORWARDED_QQ_GROUP_ID']:
            utils.send_to_tg(context)


def webhook_handler():
    context = GroupContext.build('', group_id=current_app.config['WEBHOOK_NOTIFICATION_GROUP'])

    # DOC: https://developer.github.com/webhooks/event-payloads/
    payload = request.json
    if request.headers.get("X-GitHub-Event") == 'check_run':
        if payload['action'] != "completed":
            return ""
        check_run = payload['check_run']
        message = f"CI job {check_run['name']} has completed: {check_run['conclusion']}."
        utils.send(context, message)
    elif request.headers.get("X-GitHub-Event") == 'push':
        commits = payload['commits']
        message = f"{payload['sender']['login']} has pushed {len(commits)} commit(s)" \
                  f" to my repository:"
        for commit in commits:
            message += f"\n{commit['id'][:6]} {commit['message']}"
        utils.send(context, message)
    elif request.headers.get("X-GitHub-Event") == 'pull_request':
        message = f"{payload['sender']['login']} has {payload['action']} a pull request " \
                  f"{payload['pull_request']['title']}. " \
                  f"For details see: {payload['pull_request']['url']}"
        utils.send(context, message)
    return ""
