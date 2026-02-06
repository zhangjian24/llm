// lib/langchain/tools.ts
// 定义外部工具，如天气查询功能

import { z } from "zod";
import { DynamicTool } from "@langchain/core/tools";

/**
 * 使用Open-Meteo API查询天气的函数
 * @param latitude 纬度
 * @param longitude 经度
 * @returns 天气信息
 */
const getWeatherData = async (latitude: number, longitude: number): Promise<string> => {
  try {
    // Open-Meteo API的URL
    const url = `https://api.open-meteo.com/v1/forecast?latitude=${latitude}&longitude=${longitude}&current=temperature_2m,weather_code,wind_speed_10m&hourly=temperature_2m,weather_code&daily=weather_code,temperature_2m_max,temperature_2m_min&timezone=auto`;
    
    const response = await fetch(url);
    
    if (!response.ok) {
      throw new Error(`天气API请求失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    // 解析天气数据
    const current = data.current;
    const daily = data.daily;

    // 天气代码映射
    const weatherCodeMap: Record<number, string> = {
      0: "晴天",
      1: "主要晴天",
      2: "部分多云",
      3: "多云",
      45: "雾",
      48: "霜雾",
      51: "轻毛毛雨",
      53: "毛毛雨",
      55: "浓毛毛雨",
      56: "轻微冻毛毛雨",
      57: "严重冻毛毛雨",
      61: "轻微降雨",
      63: "降雨",
      65: "强降雨",
      66: "轻微冻雨",
      67: "严重冻雨",
      71: "轻微降雪",
      73: "降雪",
      75: "强降雪",
      77: "雪粒",
      80: "轻微阵雨",
      81: "阵雨",
      82: "强阵雨",
      85: "轻微阵雪",
      86: "阵雪",
      95: "雷暴",
      96: "轻微冰雹雷暴",
      99: "严重冰雹雷暴"
    };

    const weatherDescription = weatherCodeMap[current.weather_code] || "未知天气";
    
    return `当前位置天气信息：
- 温度: ${current.temperature_2m}°C
- 天气: ${weatherDescription}
- 风速: ${current.wind_speed_10m} km/h
- 最高温度: ${daily.temperature_2m_max[0]}°C
- 最低温度: ${daily.temperature_2m_min[0]}°C`;
  } catch (error) {
    console.error("获取天气数据时出错:", error);
    return `获取天气信息失败: ${(error as Error).message}`;
  }
};

/**
 * 根据城市名称获取坐标的辅助函数
 * @param city 城市名称
 * @returns 坐标对象
 */
const getCoordinatesByCity = async (city: string): Promise<{ latitude: number, longitude: number } | null> => {
  try {
    // 使用Open-Meteo的地理编码API获取坐标
    const encodedCity = encodeURIComponent(city);
    const geocodingUrl = `https://geocoding-api.open-meteo.com/v1/search?name=${encodedCity}&count=1&language=zh&format=json`;
    
    const response = await fetch(geocodingUrl);
    
    if (!response.ok) {
      throw new Error(`地理编码API请求失败: ${response.status} ${response.statusText}`);
    }
    
    const data = await response.json();
    
    if (data.results && data.results.length > 0) {
      const location = data.results[0];
      return {
        latitude: location.latitude,
        longitude: location.longitude
      };
    }
    
    return null;
  } catch (error) {
    console.error("获取城市坐标时出错:", error);
    return null;
  }
};

/**
 * 天气查询工具
 * 允许AI助手查询任意城市的天气信息
 */
export const weatherTool = new DynamicTool({
  name: "get_weather",
  description: "获取指定城市的天气信息。输入参数为城市名称，输出该城市的当前天气状况，包括温度、天气描述、风速等信息。",
  func: async (city: string): Promise<string> => {
    try {
      // 首先根据城市名称获取坐标
      const coordinates = await getCoordinatesByCity(city);
      
      if (!coordinates) {
        return `抱歉，无法找到城市 "${city}" 的位置信息。`;
      }
      
      // 使用坐标查询天气
      return await getWeatherData(coordinates.latitude, coordinates.longitude);
    } catch (error) {
      console.error("天气查询工具执行出错:", error);
      return `天气查询失败: ${(error as Error).message}`;
    }
  },
});

// 导出所有可用的工具
export const tools = [weatherTool];