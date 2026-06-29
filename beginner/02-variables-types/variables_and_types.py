"""
SimuLearn Scripts — 初级 #02：变量与数据类型
=============================================
知识点：variables-and-types

Python 是动态类型语言，变量名只是指向对象的"标签"。
理解类型对处理仿真数据至关重要——错误的数据类型会导致静默计算错误。

本节涵盖：
  1. Python 基本数据类型 (int, float, str, bool)
  2. 类型检查与转换
  3. 仿真工程中的类型陷阱
  4. ANSYS 数据中的类型识别

运行方式：
  python variables_and_types.py
"""

# ═══════════════════════════════════════════════════════════════
# 1. 基本数据类型
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 基本数据类型")
print("=" * 60)

# int — 整数：节点编号、载荷步序号、单元数
node_count = 125000
load_step = 3
print(f"节点数 (int): {node_count:,}")

# float — 浮点数：应力、位移、温度、尺寸
max_stress_MPa = 235.5
displacement_mm = 0.127
print(f"最大应力 (float): {max_stress_MPa} MPa")
print(f"位移 (float):    {displacement_mm} mm")

# str — 字符串：材料牌号、文件名、路径
material = "Q345"
result_file = "C:/analysis/results.rst"
print(f"材料 (str):      {material}")
print(f"结果文件 (str):   {result_file}")

# bool — 布尔值：通过/不通过、收敛/发散
converged = True
passed = False
print(f"收敛 (bool):     {converged}")
print(f"通过 (bool):     {passed}")


# ═══════════════════════════════════════════════════════════════
# 2. 类型检查 — 用 type() 确认变量类型
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. 类型检查")
print("=" * 60)

print(f"type(125000)         → {type(125000)}")
print(f"type(235.5)          → {type(235.5)}")
print(f"type('Q345')         → {type('Q345')}")
print(f"type(True)           → {type(True)}")
print(f"type([1, 2, 3])      → {type([1, 2, 3])}")     # 列表
print(f"type({'E': 200e9})   → {type({'E': 200e9})}")  # 字典

# isinstance() — 更灵活的类型检查
print(f"\nisinstance(235.5, float)     → {isinstance(235.5, float)}")
print(f"isinstance(235.5, (int, float)) → {isinstance(235.5, (int, float))}")  # 数字
print(f"isinstance('Q345', str)      → {isinstance('Q345', str)}")


# ═══════════════════════════════════════════════════════════════
# 3. 类型转换 — 工程中常见的转换场景
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 类型转换")
print("=" * 60)

# 场景A：从文本文件读取的数值是字符串，需要转 float
raw_value = "235.5"
stress = float(raw_value)       # str → float
print(f"float('235.5') = {stress}")

# 场景B：ANSYS 输出的节点编号可能是 float，需要转 int
ansys_node = 123.0
node_id = int(ansys_node)        # float → int（注意截断！）
print(f"int(123.0) = {node_id}")

# 场景C：结果输出到报告时需要格式化为字符串
report_line = f"最大应力 = {max_stress_MPa:.1f} MPa"
print(f"格式化输出: {report_line}")

# 场景D：布尔值与数值的转换
print(f"int(True) = {int(True)}")    # 1
print(f"int(False) = {int(False)}")   # 0
print(f"bool(0) = {bool(0)}")         # False
print(f"bool(0.001) = {bool(0.001)}") # True（非零为真）


# ═══════════════════════════════════════════════════════════════
# 4. 工程陷阱 — 仿真数据中的类型问题
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 工程陷阱")
print("=" * 60)

# 陷阱1：整数除法
print("陷阱1 — 整数除法:")
a = 3
b = 2
print(f"  3 / 2   = {a / b}     ← 浮点除法（Python 3）")
print(f"  3 // 2  = {a // b}      ← 整数除法（向下取整）")
# 在仿真中，力/面积如果是两个整数，可能得到意外的 0 或 1
force = 10      # N
area = 3        # m²
pressure_wrong = force // area   # 3 Pa（错误！）
pressure_right = force / area    # 3.333... Pa
print(f"  10 N / 3 m² (//)  = {pressure_wrong} Pa  ← 错误")
print(f"  10 N / 3 m² (/)   = {pressure_right:.2f} Pa ← 正确")

# 陷阱2：字符串拼接 vs 数值运算
print("\n陷阱2 — 字符串与数字混用:")
s1 = "100"
s2 = "200"
print(f"  '100' + '200' = '{s1 + s2}'   ← 字符串拼接")
print(f"  100 + 200     = {100 + 200}       ← 数值加法")
# 如果从文件读取数据忘记转换类型，就会拼接而非相加

# 陷阱3：浮点数比较
print("\n陷阱3 — 浮点数比较:")
x = 0.1 + 0.2
print(f"  0.1 + 0.2 = {x}")
print(f"  0.1 + 0.2 == 0.3 → {x == 0.3}  ← 浮点精度问题！")
print(f"  abs((0.1+0.2) - 0.3) = {abs(x - 0.3):.2e}")
# 正确的比较方式
tolerance = 1e-9
print(f"  容差比较: abs((0.1+0.2)-0.3) < 1e-9 → {abs(x - 0.3) < tolerance}")

# 陷阱4：None 与 0 的区别
print("\n陷阱4 — None vs 0:")
temperature = None  # 未测量
stress = 0.0        # 测量值为零
print(f"  temperature is None → {temperature is None}")
print(f"  stress == 0        → {stress == 0}")
# None 表示"没有值"，0 表示"值为零"——物理含义完全不同


# ═══════════════════════════════════════════════════════════════
# 5. ANSYS 数据中的类型识别
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. ANSYS 数据中的类型识别")
print("=" * 60)

# 模拟从 ANSYS 输出中解析一行数据
line = "   1  100.5  -20.3   -5.1   10.0    5.2    2.8"

# 拆分并识别类型
parts = line.split()
print(f"原始行: '{line}'")
print(f"拆分后: {parts}")

# 第一列是节点编号（整数）
node_id = int(parts[0])
print(f"节点编号: {node_id} (type={type(node_id).__name__})")

# 其余是应力分量（浮点数）
stresses = [float(x) for x in parts[1:]]
print(f"应力分量: {stresses}")
print(f"各分量类型: {[type(s).__name__ for s in stresses]}")

# 验证：ANSYS 输出中的科学计数法
sci_line = "   5  1.2345E+02  -5.6789E-01"
sci_parts = sci_line.split()
try:
    node = int(sci_parts[0])
    sx = float(sci_parts[1])
    sy = float(sci_parts[2])
    print(f"\n科学计数法解析: 节点{node} SX={sx} SY={sy}")
except ValueError as e:
    print(f"解析失败: {e}")


# ═══════════════════════════════════════════════════════════════
# 6. 最佳实践
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 最佳实践")
print("=" * 60)

print("""
  ✅ 关键变量用 type() 或 isinstance() 验证类型
  ✅ 从文件/API 读取的数据显式转换类型
  ✅ 浮点数比较使用容差: abs(a - b) < 1e-9
  ✅ 使用 assert 验证取值范围
  ✅ 区分 None（无值）和 0（零值）
  ✅ 避免在类型不确定的变量上做数学运算
""")


# ═══════════════════════════════════════════════════════════════
# 7. 练习
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 以下表达式的结果是什么？先用脑算，再写代码验证：
     - 5 / 2
     - 5 // 2
     - int(5.9)
     - float('3.14')
     - bool('')
     - bool('False')

  2. 一个 ANSYS 输出行是 "10  2.5E+02  -1.0E-01  0.0"，
     写出解析每个值的代码，并说明每部分的类型。

  3. 为什么以下代码可能出错？
     stress = input("输入应力值 (MPa): ")
     safety_factor = 1.5
     allowable = stress / safety_factor

  4. 写一个函数 safe_float(value, default=0.0)：
     如果 value 可以转为 float 则返回转换结果，
     否则返回 default 并打印警告。
""")
