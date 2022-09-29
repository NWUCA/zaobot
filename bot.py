import nonebot
from nonebot.adapters.onebot.v11 import Adapter
import database

nonebot.init()
app = nonebot.get_asgi()

driver = nonebot.get_driver()
driver.register_adapter(Adapter)
driver.on_startup(lambda: database.connect(driver.config.database_url, app))
driver.on_shutdown(database.disconnect)

plugins = [
    'nonebot_plugin_apscheduler',
    'plugins.help',
    'plugins.record',
    'plugins.zao',
    'plugins.fudu',
    'plugins.caihongpi',
]

for plugin in plugins:
    nonebot.load_plugin(plugin)

if __name__ == "__main__":
    nonebot.logger.warning("Always use `nb run` to start the bot instead of manually running!")    
    nonebot.run(app="__mp_main__:app")
