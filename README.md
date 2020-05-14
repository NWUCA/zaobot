# zaobot

Thanks to the original [zaobot](https://github.com/huiyiqun/zaobot).

Thanks to [Coolq HTTP API](https://github.com/richardchien/coolq-http-api) 
and its [Python SDK](https://github.com/cqmoe/python-cqhttp).

## Get started
See the reference project above.
The entrance file is *bot/server.py*.

## Technical structure
The bot is built on Coolq and Coolq HTTP API.

### Dependencies
| Library | Description|
| ------- |  --------  |
|flask| this bot's web server|
|requests| interact with Coolq HTTP API|
|pytest| test framework|
|requests_mock| intercept HTTP requests|

### Development dependencies
| Library | Description|
| ------- |  --------  |
|pytest| test framework|
|requests_mock| intercept HTTP requests|
|flake8| code style check tools|

## How to contribute
1. Clone this repository and install dependencies.
    ```shell script
    git clone https://github.com/NWUCA/zaobot.git
    cd zaobot
    pip install -r requirements.txt
    ```
   
2. Write code.

    Mostly you just need to modify `bot/directive.py` (to add directives) and `tests/test_coolq.py` (to add tests).
    
    Basically each function needs a test.
    
    To start a server:
    ```shell script
    ./run.sh
    ```
   
3. Run tests.
    ```shell script
    python -m pytest
    ```
    Also you need to run flake8 checks. Note we don't meet PEP 8's line length limits.
    ```shell script
    flake8 --max-line-length 127
    ```
   
4. Make a pull request.