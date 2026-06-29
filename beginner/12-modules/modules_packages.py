"""
SimuLearn Scripts — 初级 #12：模块与包
=======================================
知识点：modules-and-packages

将通用工具函数提取为自建模块，多个脚本共享同一套工具函数。
理解 import 机制避免命名污染。

本节涵盖：
  1. import 语法
  2. 标准库常用模块
  3. 自建模块
  4. 包结构 (__init__.py)
  5. 避免循环导入

运行方式：
  python modules_packages.py
"""

# ═══════════════════════════════════════════════════════════════
# 1. import 语法对比
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. import 语法对比")
print("=" * 60)

# import module — 导入整个模块，使用 module.func()
import math
print(f"import math → math.sqrt(144) = {math.sqrt(144)}")

# from module import name — 导入特定函数，直接用 func()
from math import sqrt, pi
print(f"from math import sqrt, pi → sqrt(144) = {sqrt(144)}, pi = {pi}")

# from module import name as alias — 别名，避免命名冲突
from math import sin as math_sin
import numpy as np  # 社区约定别名
print(f"别名: np.array([1, 2, 3]) = {np.array([1, 2, 3])}")

# ⚠️ 不推荐：from module import *
# 污染命名空间，不知道哪些名字来自哪个模块
# from math import *  # 不要这样做


# ═══════════════════════════════════════════════════════════════
# 2. 仿真工程师常用标准库
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. 常用标准库速览")
print("=" * 60)

# os — 操作系统接口
import os
print(f"os.getcwd() = {os.getcwd()}")
print(f"os.name = {os.name}")

# sys — 系统参数
import sys
print(f"sys.version[:20] = {sys.version[:20]}")
print(f"sys.argv = {sys.argv}")

# pathlib — 现代路径处理
from pathlib import Path
home = Path.home()
print(f"Path.home() = {home}")

# datetime — 日期时间
from datetime import datetime
now = datetime.now()
print(f"datetime.now() = {now.strftime('%Y-%m-%d %H:%M:%S')}")

# re — 正则表达式
import re
match = re.search(r"\d+\.?\d*", "Stress = 235.5 MPa")
print(f"正则提取: {match.group() if match else None}")

# json — JSON 序列化
import json
config = {"material": "Q235", "yield_MPa": 235}
json_str = json.dumps(config)
print(f"JSON 序列化: {json_str}")

# collections — 高级容器
from collections import Counter, defaultdict
print(f"Counter('ABRACADABRA') = {Counter('ABRACADABRA')}")


# ═══════════════════════════════════════════════════════════════
# 3. 自建模块 — 通用工具函数
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 自建模块")
print("=" * 60)

# 仿真工程师应该把常用函数提取为 simu_utils.py
# 这里演示概念：

# 方式1：在当前目录创建模块
# ├── simu_utils.py    ← 工具函数
# └── main.py          ← 主脚本 (from simu_utils import calc_vm)

# 方式2：子目录组织
# ├── utils/
# │   ├── __init__.py
# │   ├── mechanics.py  ← 力学计算
# │   └── parser.py     ← 输出解析
# └── main.py           ← from utils.mechanics import calc_vm

# 方式3：pip 可安装包
# ├── simu_tools/
# │   ├── __init__.py
# │   ├── core.py
# │   └── ...
# ├── setup.py
# └── README.md

print("推荐的项目结构:")
print("""
  project/
  ├── simu_utils.py        # 通用工具
  ├── simu_constants.py    # 常数和默认值
  ├── config.yaml          # 配置
  ├── input/               # 输入文件
  ├── output/              # 结果输出
  ├── run_analysis.py      # 主分析脚本
  └── tests/               # 测试
""")


# ═══════════════════════════════════════════════════════════════
# 4. if __name__ == "__main__" 的奥秘
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  4. if __name__ == '__main__'")
print("=" * 60)

# 当一个 .py 文件被直接运行时，__name__ 等于 "__main__"
# 当它被 import 时，__name__ 等于文件名（模块名）

print(f"当前模块的 __name__ = {__name__}")

print("""
  作用：
  - 保护入口代码只在直接运行时执行
  - 使脚本既可独立运行，也可作为模块被导入

  示例：
  # simu_tools.py
  def calc_vm(sx, sy, ...):
      return ...

  if __name__ == "__main__":
      # 直接运行时执行的测试代码
      print(calc_vm(100, 0, 0, 0, 0, 0))  # → 100
      # 被 import 时不会执行这段代码
""")


# ═══════════════════════════════════════════════════════════════
# 5. 动态导入 -- 处理可选依赖
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  5. 动态导入")
print("=" * 60)

# 场景：某些功能依赖可选包（如 ansys-mapdl-core）
# 只在需要时才导入

def try_import_pymapdl():
    """尝试导入 PyMAPDL，如果未安装则返回 None。"""
    try:
        import ansys.mapdl.core as pymapdl
        return pymapdl
    except ImportError:
        print("  PyMAPDL 未安装，ANSYS 功能不可用")
        return None

mapdl_module = try_import_pymapdl()
print(f"  mapdl_module = {mapdl_module}")

# 另一种方式：延迟导入（在函数内部 import）
# 这样即使包未安装，只要不调用该函数就不报错


# ═══════════════════════════════════════════════════════════════
# 6. 常见导入错误
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 常见导入错误")
print("=" * 60)

print("""
  ❌ 错误1: from module import *
     from math import *  ← 污染命名空间

  ❌ 错误2: 循环导入
     # a.py: from b import func_b
     # b.py: from a import func_a
     → ImportError！

  ✅ 解决：把共同依赖提取到第三个模块 c.py

  ❌ 错误3: 模块名与标准库冲突
     # 文件名 math.py  → import math 会导入自己！

  ✅ 文件名不要与标准库/第三方库同名

  ❌ 错误4: 忘记 __init__.py
     # Python <3.3 空目录不能作为包导入
     # Python ≥3.3 可省略但建议保留（显式声明）

  ❌ 错误5: 相对导入在顶层脚本中使用
     # from .utils import func  ← 在直接运行的脚本中报错
     # 相对导入只在包内部使用
""")


# ═══════════════════════════════════════════════════════════════
# 7. 练习
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 将之前写的 von_mises 计算函数提取到一个独立文件
     simu_mechanics.py 中，然后在另一个脚本中 import 使用。

  2. 解释 import module 和 from module import name
     在命名空间上的区别。

  3. 编写一个 simu_constants.py 模块，包含：
     - G = 9.81 (重力加速度)
     - R = 8.314 (气体常数)
     - UNIT_CONVERSIONS = {"MPa_to_Pa": 1e6, ...}
     在主脚本中导入使用。

  4. 以下代码有什么问题？
     # my_script.py
     from math import *
     pi = 3.0  # ← 覆盖了 math.pi
     print(pi)
""")

if __name__ == "__main__":
    print("\n✅ 模块与包示例运行完成。")
