from nonebot.plugin import on_command
from nonebot.adapters.onebot.v11 import Message, MessageEvent
from nonebot.params import CommandArg
from nonebot.log import logger
from typing import Dict, Any
from .data_source import find_city_code, search_city_code, get_weather, get_all_districts

weather = on_command("天气", aliases={"查天气"}, priority=5)

@weather.handle()
async def handle_weather(event: MessageEvent, args: Message = CommandArg()):
    arg_text = args.extract_plain_text().strip()
    logger.debug(f"收到天气查询请求: {arg_text}")
    
    if not arg_text:
        await weather.finish("请输入查询指令，例如：\n天气 北京\n天气 河北-大城")

    # 解析输入
    logger.debug(f"参数：{arg_text}")
    parts = arg_text.split("-")
    
    # 统一使用 find_city_code 查询
    if len(parts) >= 2:
        province, city = parts[0], parts[1]
        logger.debug(f"尝试省份+城市查询: {province}, {city}")
        stationid = await find_city_code(province, city)
    else:
        # 如果没有分隔符，尝试将整个输入作为城市名
        logger.debug(f"尝试城市名查询: {arg_text}")
        stationid = await search_city_code(arg_text)

    if not stationid:
        await weather.finish(f"未找到城市 '{arg_text}'，请检查输入是否正确（格式：省份-城市）")
    
    logger.debug(f"获取到 stationid: {stationid}")
    
    # 获取天气数据
    weather_data = await get_weather(stationid)
    if not weather_data:
        await weather.finish("获取天气数据失败，请稍后再试")
    
    # 发送天气报告
    await send_weather_report(weather_data)

async def send_weather_report(data: Dict[str, Any]):
    """格式化天气信息（完整适配最新API数据结构）"""

    real_data = data["data"]["real"]
    station = real_data["station"]
    weather_info = real_data["weather"]
    wind_info = real_data["wind"]
    
    
    # 拼接天气信息（重点处理温度相关字段）
    msg = [
        f"【{station['province']}{station['city']}天气】",
        f"🕒 发布时间：{real_data['publish_time'] if str(real_data['publish_time']).strip() not in ['9999', '9999.0'] else '❓'}",
        "",
        f"🌤 当前天气：{weather_info['info'] if str(weather_info['info']).strip() not in ['9999', '9999.0'] else '❓'}",
        # 温度和体感温度使用优化后的函数处理（兼容9999.0）
        f"🌡 温度：{format_value(weather_info['temperature'], '{}℃')} (体感{format_value(weather_info['feelst'], '{}℃')})",
        f"📈 温差：{format_value(weather_info['temperatureDiff'], '{}℃')}",
        f"💧 湿度：{format_value(weather_info['humidity'], '{}%')}",
        f"🌬 风力：{wind_info['direct'] if str(wind_info['direct']).strip() not in ['9999', '9999.0'] else '❓'} "
        f"{wind_info['power'] if str(wind_info['power']).strip() not in ['9999', '9999.0'] else '❓'} "
        f"({format_value(wind_info['speed'], '{}m/s')})",
        f"☔ 降水量：{format_value(weather_info['rain'], '{}mm')}",
        f"📊 舒适度：{_get_comfort_desc(weather_info['icomfort']) if str(weather_info['icomfort']).strip() not in ['9999', '9999.0'] else '❓'}",
        f"🌅 日出：{real_data['sunriseSunset']['sunrise'] if str(real_data['sunriseSunset']['sunrise']).strip() not in ['9999', '9999.0'] else '❓'}",
        f"🌇 日落：{real_data['sunriseSunset']['sunset'] if str(real_data['sunriseSunset']['sunset']).strip() not in ['9999', '9999.0'] else '❓'}"
    ]

    await weather.finish("\n".join(msg))

# 优化未知值处理函数（兼容9999和9999.0）
def format_value(value, pattern):
    """
    格式化字段值：若为9999或9999.0则返回未知图案，否则返回带格式的值
    :param value: 原始值（可能是整数、浮点数或字符串）
    :param pattern: 正常显示的格式字符串（含占位符）
    """
    # 统一转换为字符串后判断（避免数值类型差异影响判断）
    str_value = str(value).strip()
    # 匹配"9999"或"9999.0"两种未知值格式
    if str_value in ["9999", "9999.0"]:
        return "❓"
    return pattern.format(value)

def _get_comfort_desc(level: int) -> str:
    """舒适度等级描述"""
    comfort_map = {
        -4: "很冷，极不适应",
        -3: "冷，很不舒适",
        -2: "凉，不舒适",
        -1: "凉爽，较舒适",
        0: "舒适，最可接受",
        1: "温暖，较舒适", 
        2: "暖，不舒适",
        3: "热，很不舒适",
        4: "很热，极不适应",
        9999: "❓"
    }
    return comfort_map.get(level, "未知")


districts = on_command("支持区县", aliases={"查询区县", "可查区县"}, priority=5)

@districts.handle()
async def handle_all_districts(event: MessageEvent, args: Message = CommandArg()):
    province = args.extract_plain_text().strip()
    if not province:
        await districts.finish("请输入省份名称，例如：支持区县 河北")
    
    result = await get_all_districts(province)
    if not result["districts"]:
        await districts.finish(f"未找到省份 '{province}' 或该省份下无可用区县数据")
    
    total = len(result["districts"])
    msg = [
        f"📌 {result['province']} 全部区县 ({total}个)：",
        "、".join(result["districts"])
    ]
    await districts.finish("\n".join(msg))