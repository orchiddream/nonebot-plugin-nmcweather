from nonebot.plugin import PluginMetadata
from .weather import weather

__plugin_meta__ = PluginMetadata(
    name="天气查询",
    description="通过NMC API查询实时天气",
    usage="天气 省份-区县|天气 区县|支持区县 省份",
    type="application",
    homepage="https://github.com/orchiddream/nonebot-plugin-nmcweather",
    version="0.1.0",
    supported_adapters={"~onebot.v11"},
)