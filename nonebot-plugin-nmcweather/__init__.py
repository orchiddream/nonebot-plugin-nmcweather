from nonebot.plugin import PluginMetadata
from .weather import weather

__plugin_meta__ = PluginMetadata(
    name="天气查询",
    description="通过NMC API查询实时天气",
    usage="天气 省份-区县|天气 区县|支持区县 省份",
    type="application",
    homepage="{项目主页}",
    version="0.1.0",
    supported_adapters={"~onebot.v11"},
)