# zaobot

Thanks to the original [zaobot](https://github.com/huiyiqun/zaobot).

Thanks to [Coolq HTTP API](https://github.com/richardchien/coolq-http-api) and his [Python SDK](https://github.com/cqmoe/python-cqhttp).

## Get started
See the reference project above.
The entrance file is *bot/server.py*.

To install dependencies:
```
pip install -r requirements.txt
```

To run a server:
```shell
./run.sh
```

To run tests:
```shell
python -m pytest
```

## Technical structure
| Library | Description|
| ------- |  --------  |
|Coolq HTTP API| the upstream server|
|flask| this bot's web server|
|requests| interact with Coolq HTTP API|
|pytest| test framework|
|requests_mock| intercept HTTP requests|

## How to contribute
Post an issue or make a pull request!
