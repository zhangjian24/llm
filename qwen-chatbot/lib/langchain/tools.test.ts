/**
 * lib/langchain/tools 单元测试
 *
 * 覆盖 weatherTool：解析 JSON 输入 + 调用 getCoordinatesByCity + getWeatherData
 */
import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { weatherTool } from './tools';

describe('weatherTool', () => {
  beforeEach(() => {
    vi.stubGlobal('fetch', vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it('接受 city 字符串输入', async () => {
    // 模拟 geocoding 返回坐标
    vi.mocked(fetch)
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            results: [{ latitude: 39.9042, longitude: 116.4074, name: '北京' }],
          }),
        ),
      )
      // 模拟 weather API 返回
      .mockResolvedValueOnce(
        new Response(
          JSON.stringify({
            current: { temperature_2m: 20, weather_code: 0, wind_speed_10m: 5 },
            daily: {
              weather_code: [0],
              temperature_2m_max: [25],
              temperature_2m_min: [15],
            },
          }),
        ),
      );

    const result = await weatherTool.func('北京');
    expect(result).toContain('晴天');
    expect(result).toContain('20');
  });

  it('未找到城市时返回友好错误', async () => {
    vi.mocked(fetch).mockResolvedValueOnce(new Response(JSON.stringify({ results: [] })));

    const result = await weatherTool.func('不存在的城市xyz');
    expect(result).toContain('抱歉，无法找到城市');
  });

  it('geocoding API 失败时返回友好错误', async () => {
    // getCoordinatesByCity 内部 try-catch 把 fetch 错误吞掉返回 null
    vi.mocked(fetch).mockResolvedValueOnce(
      new Response('', { status: 500, statusText: 'Server Error' }),
    );
    const result = await weatherTool.func('北京');
    expect(result).toContain('抱歉，无法找到城市');
  });
});
