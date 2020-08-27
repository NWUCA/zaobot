# zaobot

Thanks to the original [zaobot](https://github.com/huiyiqun/zaobot).

Thanks to [Coolq HTTP API](https://github.com/richardchien/coolq-http-api) 
and its [Python SDK](https://github.com/cqmoe/python-cqhttp).

The original bot framework is Coolq. However, Coolq has shutdown their service, 
for now the bot framework has been migrated to [go-cqhttp](https://github.com/Mrs4s/go-cqhttp).

## Prerequisites
Zaobot is a flask app, so you should first learn 
   [how flask works](https://flask.palletsprojects.com/en/1.1.x/).
   
We use pytest as the test framework. You may want to read their 
   [doc](https://docs.pytest.org/en/stable/).

## Get started
See the reference project above.
The entrance file is *bot/server.py*.

1. Clone this repository and install dependencies.
    ```shell script
    git clone https://github.com/NWUCA/zaobot.git
    cd zaobot
    pip install -r requirements.txt
    ```
   
2. Write code.

    Mostly you just need to modify `bot/directive.py` (to add directives) and `tests/test_coolq.py` (to add tests).
    
    Basically, each function needs a test.
    
    To start a server, first you need to write a config file like `tests/test_settings.py`, put it in the root 
    directory of this project, then run:
    ```shell script
    ./run.sh
    ```
   But your config file may cause a problem because you do not have appropriate API keys (indeed you can apply
   for your own API keys, but apparently this can cost a lot of time). So maybe you could just rely on pytest
   to debug and test everything.
   
3. Run tests.
    ```shell script
    python -m pytest
    ```
    Also you need to run flake8 checks. Note we don't meet PEP 8's line length limits.
    ```shell script
    flake8 --max-line-length 127
    ```

## Technical structure
The bot is built on Coolq and Coolq HTTP API.

### Repository anatomy
```
├── bot  # bot source code
│   ├── context.py  # message context abstraction
│   ├── db.py  # handles db operations
│   ├── directive.py  # contains all the directives
│   ├── __init__.py
│   ├── schema.sql  # database table structure
│   ├── server.py  # handles flask
│   └── utils.py  # functions used in other files
├── instance
│   └── database.db  # database file lives here
├── LICENSE
├── README.md
├── requirements.txt
├── run.sh
├── settings.cfg  # global config file
└── tests  # all the tests
    ├── conftest.py  # contains pytest config and custom fixtures
    ├── test_coolq.py  # for now, all the tests are in this file
    ├── test_data.json  # unused, may be removed in the future
    ├── test.json  # what request data looks like, this is what COOLQ HTTP API offers
    └── test_settings.cfg  # config file for tests
```

### Dependencies
| Library | Description|
| ------- |  --------  |
|flask| this bot's web server|
|requests| interact with Coolq HTTP API|
|tenacity | retry library|
|APScheduler| scheduled tasks|

### Development dependencies
| Library | Description|
| ------- |  --------  |
|pytest| test framework|
|requests_mock| intercept HTTP requests|
|flake8| code style check tools|

## Deploy
```bash
gunicorn -b [domain:port] "bot.server:create_app()"
```

## How to contribute
Feel free to open an issue or a pull request.