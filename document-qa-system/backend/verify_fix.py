"""
快速验证测试 - 检查修复是否成功
"""
from app.parsers import ParserRegistry
from app.core.config import get_settings

print("=" * 60)
print("修复验证测试")
print("=" * 60)

# 1. 检查解析器注册
print("\n1. 检查解析器注册状态:")
settings = get_settings()
print(f"   配置文件中允许的 MIME 类型：{settings.ALLOWED_MIME_TYPES}")

registered_parsers = ParserRegistry._parsers
print(f"   已注册的解析器：{list(registered_parsers.keys())}")

# 2. 验证每个配置的类型都有对应的解析器
print("\n2. 验证配置与解析器匹配:")
all_matched = True
for mime_type in settings.ALLOWED_MIME_TYPES:
    is_registered = ParserRegistry.is_supported(mime_type)
    status = "✅" if is_registered else "❌"
    print(f"   {status} {mime_type}: {'已注册' if is_registered else '未注册'}")
    if not is_registered:
        all_matched = False

# 3. 总结
print("\n" + "=" * 60)
if all_matched:
    print("✅ 所有配置的 MIME 类型都有对应的解析器！")
    print("✅ 修复成功！")
else:
    print("❌ 部分 MIME 类型缺少解析器，请检查注册逻辑。")
print("=" * 60)
