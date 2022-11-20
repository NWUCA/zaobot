# zaobot

## 1 命令列表

### 1.1 帮助

获取本仓库网址。

* 命令: `/help`
* 别名: `帮助` `?` `git` `github`

### 1.2 早安

记录群友起床时间。

* 命令: `/zao [自称]`
* 别名: `早` `早安`
* 例子:
  * `/zao`
  * `/早 靓仔`

### 1.3 晚安

记录群友睡觉时间，可以设置过多少分钟以后入睡。

* 命令: `/wan [分钟]`
* 别名: `晚` `晚安`
* 例子:
  * `/wan`
  * `/晚 60`

### 1.4 早起排行榜

查询今日早起排行榜，每日凌晨4点重新统计。

* 命令: `/zaoguys`
* 别名: `早起排行榜`

### 1.5 倒计时

获取包括考研倒计时在内的倒计时列表。

* 命令: `/cd`
* 别名: `countdown` `倒计时` `djs`

### 1.6 彩虹屁

让zaobot对你说一句彩虹屁。

* 命令: `/chp`
* 别名: `彩虹屁`

### 1.7 想要5000兆圆表情包生成器

默认上下部分使用`5000兆円`和`欲しい!`填充，群友可以自定义。

* 命令: `/choyen [上] [下]`
* 别名: `5000`
* 例子:
  * `/5000 月薪2000没有五险一金`
  * `/5000 国家励志奖学金 俺也想要！`

### 1.8 ph站logo生成器

必须指定左右文字，使用空格分隔。

* 命令: `/ph <左> <右>`
* 别名: `pornhub`
* 例子:
  * `/ph 西北 大学`

### 1.9 缩写查询

可以查询一段内容中的缩写含义。

* 命令: `/sxcx <内容|回复>`
* 别名: `缩写查询` `suoxie`
* 例子:
  * `/缩写查询 usa jfk`
  * `【回复某人消息】/suoxie`

### 1.10 yes or no

针对群友提出的二元问题随机回答yes或者no

* 命令: `/ask <问题>`
* 例子:
  * `/ask 今天吃东食堂嘛？`

## 2 被动列表

### 2.1 记录消息

记录群友所有聊天信息。

### 2.2 复读

随着群友复读次数增加，zaobot复读概率也会增加。

### 3 开发者文档

本项目使用 poetry 作为依赖包管理工具.

```bash
# 进入 poetry 环境
poetry shell
# 安装依赖
poetry install
```

目前数据库结构不稳定，需要在本地生成第一份表迁移文件并应用。

```bash
# 生成表迁移文件
alembic revision --autogenerate -m "first generation"
# 应用表迁移文件
alembic upgrade head
```

需要在根目录创建`.env`文件，作为必要的配置文件。

```conf
ENVIRONMENT=dev

HOST=127.0.0.1
PORT=8080

SYNC_DATABASE_URL=sqlite:///db.sqlite3
ASYNC_DATABASE_URL=sqlite+aiosqlite:///db.sqlite3

APSCHEDULER_AUTOSTART=true
APSCHEDULER_CONFIG={"apscheduler.timezone": "Asia/Shanghai"}

ADMIN_SECRET=<自定义随机字符串用于加密>
ADMIN_USERNAME=<后台管理员用户名>
ADMIN_PASSWORD=<后台管理员密码>

Q_WEATHER_KEY=<和风天气 api key>

YIKE_APPID=<已不再使用>
YIKE_APPSECRET=<已不再使用>
TIAN_APIKEY=<已不再使用>
```

本项目使用 onebot v11 协议，推荐使用 [go-cqhttp](https://github.com/Mrs4s/go-cqhttp) 的反响代理模式。go-cqhttp `config.yml` 必要配置如下。

```yml
account: # 账号相关
  uin: 123456789 # QQ账号
  password: '123456789' # 密码为空时使用扫码登录

message:
  # 上报数据类型
  # 可选: string,array
  post-format: string

# 连接服务列表
servers:
  - ws-reverse:
      universal: ws://127.0.0.1:8080/onebot/v11/
```

完事具备以后就可以运行了，后台管理界面在`http://127.0.0.1:8080/admin/`

```bash
nb run
```
