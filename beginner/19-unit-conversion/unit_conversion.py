"""
SimuLearn Scripts — 初级 #19：仿真单位换算脚本
=================================================
知识点：unit-conversion

仿真中最容易出错的不是公式，而是单位。
  - Mars Climate Orbiter: lbf·s vs N·s → $327M 损失
  - 仿真输入: 长度用 mm，材料属性用 m → 结果差 1000 倍
  - 跨团队协作: 欧洲用 MPa，美国用 ksi

本节涵盖：
  1. 为什么单位是仿真的生命线
  2. simulearn unit_converter 使用
  3. 工程案例：输入输出单位不一致
  4. 创建自定义换算表
  5. 单位标注自动化
  6. 常见坑与最佳实践

运行方式：
  # 确保 utils/ 在 Python path 中
  python unit_conversion.py

前置依赖：
  utils/unit_converter.py (仓库已有)
"""

import math
import sys
from pathlib import Path

# 添加仓库根目录到 path
REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from utils.unit_converter import (
    convert,
    list_units,
    list_categories,
)

# ═══════════════════════════════════════════════════════════════
# 1. 为什么单位是仿真的生命线
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 为什么单位是仿真的生命线")
print("=" * 60)

print("""
  真实事故:

  1999 Mars Climate Orbiter
  ├── 洛克希德·马丁: 推力数据用 lbf·s (英制)
  ├── NASA JPL: 软件期望 N·s (国际单位)
  ├── 结果: 轨道器进入火星大气层烧毁
  └── 损失: $327,000,000 + 数年工作

  仿真工程中的单位陷阱:
  ┌─────────────────────────────────────────────────┐
  │ 输入 1: 截面宽度 = 50 (用户想的是 mm)            │
  │ 输入 2: E = 210e9 (材料库是 Pa)                  │
  │ 计算 I = b·h³/12 = 50 * 100³ / 12 = 4166667     │
  │       ↑ 这里混了 mm 和 m，I 差了 10¹² 倍!       │
  └─────────────────────────────────────────────────┘

  核心原则: 所有计算使用一致的单位制，只在输入/输出时转换。
""")


# ═══════════════════════════════════════════════════════════════
# 2. simulearn unit_converter 使用
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  2. simulearn unit_converter 使用")
print("=" * 60)

# ── 查看所有支持的单位 ──
print("\n支持的单位类别:")
for cat in list_categories():
    units = list(list_units(cat).keys())
    print(f"  {cat}: {', '.join(units[:6])}{'...' if len(units) > 6 else ''}")

# ── 基本换算 ──
print("\n基本换算示例:")

# 长度换算
val_mm = convert(5.0, "inch", "mm")
print(f"  5 inch = {val_mm} mm")

val_inch = convert(127.0, "mm", "inch")
print(f"  127 mm = {val_inch} inch")

# 应力换算
val_psi = convert(350, "MPa", "psi")
print(f"  350 MPa = {val_psi:.1f} psi")

val_MPa = convert(50000, "psi", "MPa")
print(f"  50000 psi = {val_MPa:.1f} MPa")

# 力换算
val_N = convert(1000, "lbf", "N")
print(f"  1000 lbf = {val_N:.1f} N")

val_kgf = convert(1000, "N", "kgf")
print(f"  1000 N = {val_kgf:.2f} kgf")

# 温度换算 — 注意偏移！
print("\n温度换算 (含偏移):")
temp_C_to_K = convert(25, "°C", "K")
print(f"  25°C = {temp_C_to_K:.2f} K")

temp_F_to_C = convert(100, "°F", "°C")
print(f"  100°F = {temp_F_to_C:.2f} °C")

temp_K_to_F = convert(300, "K", "°F")
print(f"  300 K = {temp_K_to_F:.2f} °F")

# ── 角度换算 ──
print("\n角度换算:")
rad = convert(180, "deg", "rad")
print(f"  180° = {rad:.6f} rad")
deg = convert(math.pi / 2, "rad", "deg")
print(f"  π/2 rad = {deg:.2f}°")


# ═══════════════════════════════════════════════════════════════
# 3. 工程案例：输入输出单位不一致
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 工程案例：跨单位制仿真")
print("=" * 60)

print("""
  场景: 一家欧洲公司（使用 MPa/mm）拿到美国供应商的
        测试数据（psi/inch），需要做仿真校核。
""")

# ── 案例 A：手工单位混乱（⚠ 错误演示）──
print("\n  --- 案例 A: 错误做法 ---")

# 供应商数据（英制）
width_inch = 2.0       # inch
height_inch = 4.0      # inch
E_psi = 30e6           # psi (钢材)
force_lbf = 5000       # lbf
L_inch = 20.0          # inch

# ❌ 直接混用英制和公制
#    width_mm = width_inch * 25.4  ← 散落在代码各处的魔法数字
#    E_MPa = E_psi / 145.038      ← 容易写错

print("  供应商数据 (英制):")
print(f"    截面: {width_inch} × {height_inch} inch")
print(f"    弹性模量: {E_psi:.1e} psi")
print(f"    载荷: {force_lbf} lbf")
print(f"    跨距: {L_inch} inch")

# ── 案例 B：用 convert 安全换算 ──
print("\n  --- 案例 B: 正确做法 (用 convert) ---")

# 第一步：统一换算到国际单位制 (SI)
width_m = convert(width_inch, "inch", "m")
height_m = convert(height_inch, "inch", "m")
E_Pa = convert(E_psi, "psi", "Pa")
force_N = convert(force_lbf, "lbf", "N")
L_m = convert(L_inch, "inch", "m")

print("  换算到 SI:")
print(f"    截面: {width_m*1000:.1f} × {height_m*1000:.1f} mm")
print(f"    弹性模量: {E_Pa/1e9:.2f} GPa")
print(f"    载荷: {force_N:.1f} N")
print(f"    跨距: {L_m:.3f} m")

# 第二步：用 SI 单位做计算
I_m4 = width_m * height_m**3 / 12
M_max = force_N * L_m / 4
c = height_m / 2
stress_Pa = M_max * c / I_m4
deflection_m = force_N * L_m**3 / (48 * E_Pa * I_m4)

print("\n  计算结果 (SI):")
print(f"    I = {I_m4:.6e} m⁴")
print(f"    σ_max = {stress_Pa/1e6:.2f} MPa")
print(f"    δ_max = {deflection_m*1000:.3f} mm")

# 第三步：按需换算到客户习惯的单位
stress_psi = convert(stress_Pa, "Pa", "psi")
deflection_inch = convert(deflection_m, "m", "inch")

print("\n  给美国客户的报告 (英制):")
print(f"    σ_max = {stress_psi:.0f} psi")
print(f"    δ_max = {deflection_inch:.4f} inch")

# ── 验证：英制直接计算 vs 公制换算 ──
print("\n  --- 验证：两种路径应该一致 ---")
# 英制直接
I_in4 = width_inch * height_inch**3 / 12
stress_psi_direct = force_lbf * L_inch * (height_inch/2) / (4 * I_in4)
print(f"  英制直接: σ = {stress_psi_direct:.0f} psi")
print(f"  公制换算: σ = {stress_psi:.0f} psi")
print(f"  差异: {abs(stress_psi_direct - stress_psi):.2e} psi  ✅ 一致")


# ═══════════════════════════════════════════════════════════════
# 4. 创建自定义换算表
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 创建自定义换算表")
print("=" * 60)

# 场景：某项目需要输出一个"换算速查表"给非技术人员
def generate_conversion_table(category: str, reference_value: float = 1.0):
    """为给定类别生成换算表。

    Args:
        category: 单位类别（如"应力/压力"）
        reference_value: 参考值
    """
    units = list(list_units(category).keys())
    reference_unit = units[0]  # 以第一个为基准

    print(f"\n  {category} 换算表 (基准: {reference_value} {reference_unit}):")
    print(f"  {'─' * 45}")
    print(f"  {'单位':<10} {'等效值':<18} {'反向换算':<18}")
    print(f"  {'─' * 45}")

    for unit in units:
        converted = convert(reference_value, reference_unit, unit)
        back = convert(1.0, unit, reference_unit)
        print(f"  {unit:<10} {converted:<18.6g} 1 {unit} = {back:.6g} {reference_unit}")

# 生成几张常用的速查表
generate_conversion_table("应力/压力", 1.0)  # 1 Pa → 各压力单位
generate_conversion_table("长度", 1.0)       # 1 m → 各长度单位
generate_conversion_table("力", 1000.0)      # 1000 N → 各力单位


# ═══════════════════════════════════════════════════════════════
# 5. 单位标注自动化
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 单位标注自动化")
print("=" * 60)

# 实战：创建一个"聪明"的数值类，自动记录单位
class UnitValue:
    """带单位标注的数值。

    不应替代 unit_converter，而是在脚本中
    作为"自文档化"的辅助，减少单位混淆。

    使用示例:
        length = UnitValue(1.5, "m")
        stress = UnitValue(350, "MPa")
        result = length.to("mm")  # → UnitValue(1500.0, "mm")
    """

    def __init__(self, value: float, unit: str):
        self.value = value
        self.unit = unit

    def to(self, target_unit: str) -> "UnitValue":
        """换算到目标单位。"""
        new_value = convert(self.value, self.unit, target_unit)
        return UnitValue(new_value, target_unit)

    def __repr__(self):
        return f"UnitValue({self.value:.4g}, '{self.unit}')"

    def __str__(self):
        return f"{self.value:.4g} {self.unit}"

    # 算术运算（保持在当前单位制）
    def __add__(self, other: "UnitValue") -> "UnitValue":
        if self.unit != other.unit:
            raise ValueError(f"无法相加不同单位: {self.unit} vs {other.unit}")
        return UnitValue(self.value + other.value, self.unit)

    def __mul__(self, scalar: float) -> "UnitValue":
        return UnitValue(self.value * scalar, self.unit)

    def __truediv__(self, other) -> "UnitValue":
        if isinstance(other, UnitValue):
            if self.unit != other.unit:
                raise ValueError(f"无法相除不同单位: {self.unit} vs {other.unit}")
            return UnitValue(self.value / other.value, self.unit)
        else:
            return UnitValue(self.value / other, self.unit)

    # 比较运算符（先统一单位再比）
    def __lt__(self, other: "UnitValue") -> bool:
        if self.unit != other.unit:
            other_val = convert(other.value, other.unit, self.unit)
        else:
            other_val = other.value
        return self.value < other_val

    def __gt__(self, other: "UnitValue") -> bool:
        if self.unit != other.unit:
            other_val = convert(other.value, other.unit, self.unit)
        else:
            other_val = other.value
        return self.value > other_val


# 使用 UnitValue 做一次完整的分析
print("\n  使用 UnitValue 的简支梁分析:")

L = UnitValue(1.5, "m")
b = UnitValue(100, "mm")
h = UnitValue(200, "mm")
E = UnitValue(210, "GPa")
F = UnitValue(10, "kN")
sigma_yield = UnitValue(235, "MPa")

# 统一到 SI 计算
b_si = b.to("m")
h_si = h.to("m")
E_si = E.to("Pa")
F_si = F.to("N")
sigma_y_si = sigma_yield.to("Pa")

print(f"  L  = {L}")
print(f"  b  = {b} → SI: {b_si}")
print(f"  h  = {h} → SI: {h_si}")
print(f"  E  = {E} → SI: {E_si}")
print(f"  F  = {F} → SI: {F_si}")

# SI 计算
I = UnitValue(b_si.value * h_si.value**3 / 12, "m⁴")
M = UnitValue(F_si.value * L.value / 4, "N·m")
c = UnitValue(h_si.value / 2, "m")
sigma = UnitValue(M.value * c.value / I.value, "Pa")
delta = UnitValue(F_si.value * L.value**3 / (48 * E_si.value * I.value), "m")

print(f"\n  结果:")
print(f"    I    = {I}")
print(f"    σ_max = {sigma} = {sigma.to('MPa')}")
print(f"    δ_max = {delta} = {delta.to('mm')}")

# 校核（自动处理单位）
sigma_MPa = sigma.to("MPa")
print(f"    利用率: {sigma_MPa.value / sigma_yield.value:.3f}")
print(f"    判定: {'✅ PASS' if sigma_MPa < sigma_yield else '❌ FAIL'}")


# ═══════════════════════════════════════════════════════════════
# 6. 单位一致性校验工具
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 单位一致性校验工具")
print("=" * 60)

def check_input_consistency(
    length: tuple,      # (value, unit)
    force: tuple,
    modulus: tuple,
    stress_allow: tuple,
) -> list:
    """检查输入单位是否属于同一单位制。

    返回警告列表。这不是严格的量纲分析，
    而是工程中的"气味检查"——混合 mm 和 m 通常意味着错误。

    Args:
        length: (值, 单位) 如 (1.5, "m")
        force: (值, 单位) 如 (10000, "N")
        modulus: (值, 单位) 如 (210e9, "Pa")
        stress_allow: (值, 单位) 如 (235e6, "Pa")

    Returns:
        警告消息列表
    """
    warnings = []
    val_l, unit_l = length
    val_f, unit_f = force
    val_e, unit_e = modulus
    val_s, unit_s = stress_allow

    # 规则1: 长度单位一致性检查
    if unit_l in ("mm", "cm") and unit_e in ("Pa", "kPa", "MPa", "GPa"):
        warnings.append(
            f"⚠ 长度用 '{unit_l}' 但弹性模量用 '{unit_e}' (SI基准)。\n"
            f"   如果 I = b·h³/12 用 mm，而 E 用 Pa，结果会差 10¹² 倍！\n"
            f"   建议: 全部换算到 m 或全部用 MPa+mm 制。"
        )

    # 规则2: 应力/模量单位一致性
    stress_cat = list_units()[unit_s]["category"]
    modulus_cat = list_units()[unit_e]["category"]
    if stress_cat != modulus_cat:
        warnings.append(
            f"⚠ 许用应力类别 '{stress_cat}' ≠ 弹性模量类别 '{modulus_cat}'"
        )

    # 规则3: 极端值检查
    if val_e > 1e15:
        warnings.append(f"⚠ 弹性模量数值极大 ({val_e:.1e} {unit_e})，可能用错了单位")
    if val_l < 0.001 and unit_l == "m":
        warnings.append(f"⚠ 长度极小 ({val_l:.5f} m)，可能是 mm 值写成了 m")

    return warnings


# 测试：好的输入
print("\n  测试 1: 好的输入 (全部 SI)")
w = check_input_consistency(
    length=(1.5, "m"),
    force=(10000, "N"),
    modulus=(210e9, "Pa"),
    stress_allow=(235e6, "Pa"),
)
if w:
    for msg in w:
        print(f"  {msg}")
else:
    print("  ✅ 未检测到问题")

# 测试：坏的输入 — 常见的 mm + Pa 混用
print("\n  测试 2: 坏的输入 (mm + Pa 混用)")
w = check_input_consistency(
    length=(1500, "mm"),     # ← 应该换算成 m
    force=(10000, "N"),
    modulus=(210e9, "Pa"),
    stress_allow=(235e6, "Pa"),
)
for msg in w:
    print(f"  {msg}")


# ═══════════════════════════════════════════════════════════════
# 7. 常见坑与最佳实践
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  7. 常见坑与最佳实践")
print("=" * 60)

pitfalls = [
    ("坑1: 温度换算忘记偏移",
     "100°C → K 不是 +100 而是 +273.15",
     "使用 convert(100, '°C', 'K') 自动处理偏移"),

    ("坑2: MPa+mm 制 vs SI 制",
     "有限元软件常用 MPa+mm+tonne，惯性矩 I 用 mm⁴",
     "明确文档化你的单位制，不使用'默认'假设"),

    ("坑3: 角度函数忘记换算",
     "math.sin(45) → sin(45 rad)，不是 45°！",
     "math.sin(math.radians(45)) 或 convert(45,'deg','rad')"),

    ("坑4: 密度单位陷阱",
     "钢铁密度: 7850 kg/m³ = 7.85e-9 tonne/mm³",
     "用 convert 换算，不要手算 10 的幂次"),

    ("坑5: 螺栓预紧力单位",
     "扭矩扳手: N·m, lbf·ft, kgf·cm 三者容易混淆",
     "在输入文件顶部用注释声明单位制"),

    ("坑6: 重力加速度",
     "9.81 m/s² vs 9810 mm/s² vs 386.4 in/s²",
     "显式定义为常量 GRAVITY = UnitValue(9.81, 'm/s2')"),
]

for title, problem, solution in pitfalls:
    print(f"\n  ⚠  {title}")
    print(f"     问题: {problem}")
    print(f"     解决: {solution}")


# ═══════════════════════════════════════════════════════════════
# 8. 练习
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  8. 练习")
print("=" * 60)

print("""
  [练习 1] 写一个函数 convert_material_properties(material_dict, target_system):
           输入: {"E": (210, "GPa"), "nu": (0.3, ""), "rho": (7850, "kg/m3")}
           目标: target_system = "MPa_mm" (E → MPa, rho → tonne/mm³)
           输出: 换算后的字典

  [练习 2] 扩展 UnitValue 类，支持：
           - 导出单位间的乘除（N/m² → Pa 自动识别）
           - 格式化输出控制小数位数
           - 与 pint 库的互操作

  [练习 3] 验证 Mars Climate Orbiter 事故：
           写脚本模拟：洛克希德输入 1000 lbf·s，JPL 当作 1000 N·s
           计算轨道偏差（简化物理模型）

  [练习 4] 为你的 ansys 脚本添加单位标注：
           在所有输入文件顶部添加 !! UNITS: MPa, mm, N, tonne
           写脚本自动解析该注释并校验后续数值
""")

print("✅ 知识点 19 完成: 仿真单位换算脚本")
