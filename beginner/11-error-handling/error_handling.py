"""
SimuLearn Scripts — 初级 #11：异常处理基础
===========================================
知识点：error-handling

工程脚本在无人值守时运行，异常处理决定脚本是"崩溃"还是"记录错误并继续"。
对已知风险点用精确异常类型捕获；未知异常不应吞掉。

本节涵盖：
  1. try/except/finally 语法
  2. 常见异常类型
  3. 精确捕获 vs 宽泛捕获
  4. 工程鲁棒性脚本

运行方式：
  python error_handling.py
"""

import traceback
from pathlib import Path


# ═══════════════════════════════════════════════════════════════
# 1. 基本异常捕获
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 基本异常捕获")
print("=" * 60)

# 没有异常处理 — 一行出错，整个脚本崩溃
# result = 1 / 0  # ZeroDivisionError → 脚本终止

# try/except — 捕获并处理
print("安全除法:")
for divisor in [2, 1, 0, 3]:
    try:
        result = 10 / divisor
        print(f"  10 / {divisor} = {result:.1f}")
    except ZeroDivisionError:
        print(f"  10 / {divisor} → 除零错误，已跳过")

# try/except/else — 无异常时执行 else
print(f"\n文件读取:")
try:
    with open("不存在的文件.txt", "r") as f:
        content = f.read()
except FileNotFoundError as e:
    print(f"  ❌ 文件不存在: {e}")
else:
    print(f"  ✅ 文件读取成功")
    # else 中的代码只在 try 无异常时执行

# try/except/finally — finally 始终执行
print(f"\n资源清理 (finally):")
try:
    print(f"  打开文件...")
    # 模拟操作
    result = 100 / 5
    print(f"  计算结果: {result}")
except ZeroDivisionError:
    print(f"  除零错误")
finally:
    print(f"  🧹 清理操作（无论是否异常都执行）")


# ═══════════════════════════════════════════════════════════════
# 2. 常见异常类型
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. 常见异常类型")
print("=" * 60)

exceptions_to_demo = [
    ("ZeroDivisionError", lambda: 1/0),
    ("FileNotFoundError", lambda: open("missing.txt")),
    ("ValueError", lambda: int("abc")),
    ("TypeError", lambda: "stress" + 100),
    ("KeyError", lambda: {"E": 200e9}["nu"]),
    ("IndexError", lambda: [1, 2, 3][10]),
    ("AttributeError", lambda: "string".nonexistent()),
    ("ImportError", lambda: __import__("nonexistent_module")),
]

for name, func in exceptions_to_demo:
    try:
        func()
    except Exception as e:
        print(f"  {name:<20s}: {e}")


# ═══════════════════════════════════════════════════════════════
# 3. 精确捕获 vs 宽泛捕获
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 精确捕获 vs 宽泛捕获")
print("=" * 60)

def parse_stress(value_str: str) -> float:
    """解析应力值字符串，带完整错误处理。"""
    try:
        value = float(value_str)
    except ValueError:
        print(f"  ⚠️ 无法解析 '{value_str}' 为浮点数，使用 0.0")
        return 0.0
    except TypeError:
        print(f"  ⚠️ 参数类型错误: {type(value_str)}，使用 0.0")
        return 0.0
    else:
        # 值合法时检查物理范围
        if value < 0:
            print(f"  ⚠️ 负应力值 {value} MPa，可能数据有误")
        return value

print("应力解析测试:")
for val in ["235.5", "-10", "abc", None]:
    result = parse_stress(val)
    print(f"    输入 {repr(val):<8s} → {result}")

# ❌ 错误：捕获所有异常并静默
print(f"\n❌ 错误示范:")
try:
    critical_calc = 1 / 0
except Exception:
    pass  # 静默吞掉异常 — 这是工程灾难！

# ✅ 正确：至少记录日志
print(f"✅ 正确示范:")
try:
    critical_calc = 1 / 0
except Exception as e:
    print(f"  [ERROR] 计算失败: {e}")
    print(f"  堆栈: {traceback.format_exc()[-200:]}")


# ═══════════════════════════════════════════════════════════════
# 4. 自定义异常
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 自定义异常")
print("=" * 60)

class SimulationError(Exception):
    """仿真分析异常基类。"""
    pass

class ConvergenceError(SimulationError):
    """求解未收敛。"""
    def __init__(self, step, residual):
        self.step = step
        self.residual = residual
        super().__init__(f"载荷步 {step} 未收敛，残差 = {residual:.2e}")

class MaterialNotFoundError(SimulationError):
    """材料数据缺失。"""
    pass

# 使用自定义异常
def solve_step(step: int):
    if step == 3:
        raise ConvergenceError(step=3, residual=0.05)

for step in range(1, 5):
    try:
        solve_step(step)
        print(f"  Step {step}: ✅ 收敛")
    except ConvergenceError as e:
        print(f"  Step {step}: ❌ {e}")
    except SimulationError as e:
        print(f"  Step {step}: ❌ 仿真错误: {e}")


# ═══════════════════════════════════════════════════════════════
# 5. 工程鲁棒性脚本
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 工程鲁棒性脚本")
print("=" * 60)

def robust_read_csv(filepath: str) -> list[dict]:
    """鲁棒地读取 CSV 文件，处理各种边界情况。

    返回数据行列表，失败返回空列表。
    """
    path = Path(filepath)

    # 检查1：文件是否存在
    if not path.exists():
        print(f"  [WARN] 文件不存在: {filepath}")
        return []

    # 检查2：文件大小
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > 500:
        print(f"  [WARN] 文件过大 ({size_mb:.0f} MB)，建议分块读取")
        # 仍然尝试读取，但给出警告

    rows = []
    try:
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            headers = reader.fieldnames
            if headers is None:
                print(f"  [WARN] CSV 文件无表头")
                return []

            for line_no, row in enumerate(reader, start=2):
                try:
                    # 验证每行的关键字段
                    if "Node" not in row:
                        print(f"  [WARN] 第 {line_no} 行缺少 Node 字段，跳过")
                        continue
                    rows.append(row)
                except Exception as e:
                    print(f"  [WARN] 第 {line_no} 行解析失败: {e}")
                    continue

    except UnicodeDecodeError:
        # 尝试其他编码
        try:
            with open(path, "r", encoding="gbk") as f:
                reader = csv.DictReader(f)
                rows = list(reader)
        except Exception as e:
            print(f"  [ERROR] 编码错误: {e}")
            return []
    except PermissionError:
        print(f"  [ERROR] 权限不足，无法读取: {filepath}")
        return []
    except Exception as e:
        print(f"  [ERROR] 未知错误: {e}")
        return []

    print(f"  成功读取 {len(rows)} 行数据")
    return rows

import csv
result = robust_read_csv("nonexistent.csv")
print(f"  返回: {len(result)} 行")

# 演示 try-except 的工程用法：配置回退
def get_config(key: str, default=None):
    """多级配置回退。"""
    try:
        # 第1优先级：环境变量
        import os
        return os.environ[key]
    except KeyError:
        pass

    try:
        # 第2优先级：配置文件
        with open("config.json") as f:
            config = json.load(f)
            return config.get(key, default)
    except (FileNotFoundError, json.JSONDecodeError):
        pass

    # 第3优先级：默认值
    return default


# ═══════════════════════════════════════════════════════════════
# 6. 练习
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 编写一个 safe_divide(a, b, default=0.0) 函数，
     处理除零错误并返回 default。

  2. 编写一个函数 parse_ansys_line(line: str) -> dict，
     解析可能格式不标准的 ANSYS 输出行。
     处理：空行、标题行、数值行、分页符等多种情况。

  3. 以下代码的异常处理有什么问题？
     try:
         do_complex_simulation()
     except:
         print("出错")
     改正它。
""")

import json
if __name__ == "__main__":
    print("\n✅ 异常处理示例运行完成。")
