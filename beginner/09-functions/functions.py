"""
SimuLearn Scripts — 初级 #09：函数定义与调用
=============================================
知识点：functions-basics

函数把重复逻辑封装为可测试、可复用的单元。
好的函数 = 做一件事 + 做好 + 有清晰的输入输出。

仿真工程中，每个分析步骤都应该是一个函数：
  读文件 → 算指标 → 画图 → 写报告

本节涵盖：
  1. def 语法与参数
  2. 返回值
  3. 默认参数与关键字参数
  4. 作用域
  5. 文档字符串
  6. 工程函数实战

运行方式：
  python functions.py
"""

import math

# ═══════════════════════════════════════════════════════════════
# 1. 基本函数定义
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 基本函数定义")
print("=" * 60)

# 最简单的函数 — 无参数无返回值
def print_header():
    """打印分析标题。"""
    print("=" * 40)
    print("  结构分析结果")
    print("=" * 40)

print_header()

# 有参数有返回值
def calc_area(width_mm: float, height_mm: float) -> float:
    """计算矩形截面积。

    Args:
        width_mm: 宽度 [mm]
        height_mm: 高度 [mm]

    Returns:
        面积 [mm²]
    """
    return width_mm * height_mm

area = calc_area(50.0, 100.0)
print(f"截面积: {area} mm²")

# 类型注解 — 文档和 IDE 提示，但不强制类型
def calc_inertia(b: float, h: float) -> float:
    """计算矩形截面惯性矩 I = b·h³/12。"""
    return b * h**3 / 12

I = calc_inertia(50e-3, 100e-3)
print(f"惯性矩: {I:.6e} m⁴")


# ═══════════════════════════════════════════════════════════════
# 2. 参数类型
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. 参数类型")
print("=" * 60)

# 位置参数
def stress_to_utilization(stress: float, allowable: float) -> float:
    """计算应力利用率。"""
    return stress / allowable

print(f"利用率: {stress_to_utilization(180, 235):.2f}")

# 默认参数
def check_design(
    stress: float,
    yield_stress: float = 235.0,     # 默认 Q235
    safety_factor: float = 1.5,      # 默认安全系数
) -> bool:
    """检查设计是否通过。"""
    allowable = yield_stress / safety_factor
    return stress <= allowable

print(f"默认参数:  check_design(180) = {check_design(180)}")
print(f"指定全部:  check_design(180, 345, 2.0) = {check_design(180, 345, 2.0)}")

# ⚠️ 可变默认参数的陷阱！
print(f"\n⚠️ 可变默认参数陷阱:")
def bad_append(item, target_list=[]):  # ← 不要这样！
    target_list.append(item)
    return target_list

print(f"  第1次调用: {bad_append(1)}")
print(f"  第2次调用: {bad_append(2)}  ← 列表有之前的元素！")

# ✅ 正确方式
def good_append(item, target_list=None):
    if target_list is None:
        target_list = []
    target_list.append(item)
    return target_list

print(f"\n  正确方式:")
print(f"  第1次调用: {good_append(1)}")
print(f"  第2次调用: {good_append(2)}")

# 关键字参数 — 不依赖位置的参数传递
def create_beam(length, width, height, material="Q235"):
    return f"梁 {length}m × {width}mm × {height}mm, {material}"

# 可以按任意顺序传递
print(f"\n关键字参数:")
beam1 = create_beam(length=2.0, width=50, height=100)
beam2 = create_beam(width=60, height=120, length=3.0, material="Q345")
print(f"  {beam1}")
print(f"  {beam2}")

# *args — 接收任意数量的位置参数
def max_stress(*stresses):
    """返回最大应力值。"""
    if not stresses:
        return 0.0
    return max(stresses)

print(f"\n可变参数:")
print(f"  max_stress(150, 180, 220) = {max_stress(150, 180, 220)}")
print(f"  max_stress() = {max_stress()}")

# **kwargs — 接收任意数量的关键字参数
def material_report(**properties):
    """生成材料属性报告。"""
    for key, value in properties.items():
        print(f"  {key}: {value}")

print(f"关键字参数字典:")
material_report(name="Q345", E="206 GPa", yield_MPa=345)


# ═══════════════════════════════════════════════════════════════
# 3. 返回值
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 返回值")
print("=" * 60)

# 返回单个值
def von_mises(sx, sy, sz, txy, tyz, tzx):
    """计算 von Mises 等效应力 [Pa]."""
    d12 = sx - sy
    d23 = sy - sz
    d31 = sz - sx
    return math.sqrt(0.5 * (d12**2 + d23**2 + d31**2
                            + 6*(txy**2 + tyz**2 + tzx**2)))

vm = von_mises(100e6, -20e6, -5e6, 10e6, 5e6, 2e6)
print(f"von Mises: {vm/1e6:.1f} MPa")

# 返回多个值 — 实际上是返回元组
def section_properties(width_m, height_m):
    """计算截面属性，返回 (面积, 惯性矩, 截面模量)。"""
    area = width_m * height_m
    I = width_m * height_m**3 / 12
    W = I / (height_m / 2)
    return area, I, W

A, I, W = section_properties(0.05, 0.10)
print(f"\n截面属性:")
print(f"  A = {A:.4f} m²")
print(f"  I = {I:.6e} m⁴")
print(f"  W = {W:.6e} m³")

# 返回字典 — 更清晰（推荐！）
def beam_analysis(force, length, width_m, height_m, E):
    """简支梁分析，返回完整结果字典。"""
    A, I_m4, W_m3 = section_properties(width_m, height_m)

    # 弯矩和应力
    M = force * length / 4
    sigma = M / W_m3

    # 挠度
    deflection = force * length**3 / (48 * E * I_m4)

    # 弯曲剪应力
    tau = 3 * force / (2 * A)

    return {
        "max_moment_Nm": M,
        "max_bending_stress_Pa": sigma,
        "max_deflection_m": deflection,
        "max_shear_stress_Pa": tau,
        "deflection_ratio": deflection / length,
    }

result = beam_analysis(10000, 2.0, 0.05, 0.10, 200e9)
print(f"\n简支梁分析 (返回字典):")
for key, value in result.items():
    print(f"  {key}: {value:.4e}" if abs(value) < 1 else f"  {key}: {value:.2f}")


# ═══════════════════════════════════════════════════════════════
# 4. 作用域
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 作用域")
print("=" * 60)

# 全局变量
SAFETY_FACTOR = 1.5  # 约定：常量用全大写

def check_with_global(stress_MPa: float):
    """使用全局安全系数检查。"""
    # 可以读取全局变量，但修改需要 global 声明
    return stress_MPa < (235.0 / SAFETY_FACTOR)

print(f"全局 SAFETY_FACTOR = {SAFETY_FACTOR}")
print(f"check_with_global(180) = {check_with_global(180)}")

# 函数内部变量是局部的
def local_example():
    x = 100  # 局部变量
    print(f"  函数内部 x = {x}")

local_example()
# print(x)  # NameError! x 在函数外不可见

# 修改全局变量需要 global
counter = 0
def increment():
    global counter
    counter += 1

increment()
increment()
print(f"全局 counter = {counter}")

# ⚠️ 尽量避免使用 global，用参数传递替代
# ✅ 更好的方式
def increment_better(count):
    return count + 1

counter2 = 0
counter2 = increment_better(counter2)
counter2 = increment_better(counter2)
print(f"无 global 的 counter = {counter2}")


# ═══════════════════════════════════════════════════════════════
# 5. 文档字符串
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 文档字符串 (docstring)")
print("=" * 60)

def calc_fatigue_life(
    stress_amplitude_MPa: float,
    fatigue_limit_MPa: float = 200.0,
    cycles_to_fatigue_limit: int = 1_000_000,
    fatigue_exponent: float = -0.12,
) -> float:
    """估算疲劳寿命 (Basquin 方程)。

    使用简化的 S-N 曲线关系：
      N = N_f * (σ_a / σ_f)^(1/b)

    Args:
        stress_amplitude_MPa: 应力幅值 [MPa]
        fatigue_limit_MPa: 疲劳极限 [MPa]，默认 200
        cycles_to_fatigue_limit: 疲劳极限对应循环数，默认 1,000,000
        fatigue_exponent: 疲劳指数，默认 -0.12

    Returns:
        估算的疲劳寿命 (循环数)

    Raises:
        ValueError: 当应力幅小于等于 0 时

    Example:
        >>> calc_fatigue_life(250)
        1098765.2
    """
    if stress_amplitude_MPa <= 0:
        raise ValueError(f"应力幅必须 > 0，当前值: {stress_amplitude_MPa}")

    if stress_amplitude_MPa >= fatigue_limit_MPa:
        return cycles_to_fatigue_limit * (
            stress_amplitude_MPa / fatigue_limit_MPa
        ) ** (1.0 / fatigue_exponent)
    else:
        return float("inf")  # 无限寿命

# 查看文档
print("函数文档:")
print(calc_fatigue_life.__doc__)

# 使用
N1 = calc_fatigue_life(250)
N2 = calc_fatigue_life(150)
print(f"\n疲劳寿命估算:")
print(f"  σ_a = 250 MPa → N = {N1:,.0f} 循环")
print(f"  σ_a = 150 MPa → N = {N2} (无限寿命)")


# ═══════════════════════════════════════════════════════════════
# 6. 工程函数实战 — 构建仿真工具箱
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 工程函数实战")
print("=" * 60)

# 一组互相配合的仿真分析函数
def read_stress_file(filepath: str) -> list[dict]:
    """读取应力结果文件（模拟）。

    真实场景中这可能是 CSV 解析或 ANSYS 输出解析。
    """
    # 模拟数据
    return [
        {"node": 1, "sx": 100.5, "sy": -20.3, "sz": -5.1,
         "txy": 10.0, "tyz": 5.2, "tzx": 2.8},
        {"node": 2, "sx": 98.7, "sy": -18.9, "sz": -4.8,
         "txy": 9.5, "tyz": 4.9, "tzx": 2.5},
        {"node": 3, "sx": 180.0, "sy": -30.0, "sz": -8.0,
         "txy": 15.0, "tyz": 8.0, "tzx": 5.0},
    ]

def calc_all_von_mises(results: list[dict]) -> list[dict]:
    """为所有节点计算 von Mises 应力。"""
    for r in results:
        r["vm"] = von_mises(
            r["sx"], r["sy"], r["sz"],
            r["txy"], r["tyz"], r["tzx"]
        )
    return results

def find_critical_nodes(
    results: list[dict],
    threshold_MPa: float = 150.0,
) -> list[dict]:
    """找出超过阈值的节点。"""
    return [r for r in results if r.get("vm", 0) / 1e6 > threshold_MPa]

def generate_report(results: list[dict]) -> str:
    """生成分析报告字符串。"""
    critical = find_critical_nodes(results)

    lines = ["=" * 50]
    lines.append("  应力分析报告")
    lines.append("=" * 50)

    max_node = max(results, key=lambda r: r.get("vm", 0))
    lines.append(f"\n最大 von Mises 应力:")
    lines.append(f"  节点 {max_node['node']}: "
                 f"{max_node['vm']/1e6:.1f} MPa")

    if critical:
        lines.append(f"\n超限节点 ({len(critical)} 个):")
        for r in critical:
            lines.append(f"  节点 {r['node']}: {r['vm']/1e6:.1f} MPa ⚠️")
    else:
        lines.append(f"\n所有节点应力在限值内 ✅")

    lines.append("=" * 50)
    return "\n".join(lines)

# 流水线：读→算→筛选→报告
data = read_stress_file("results.csv")
data = calc_all_von_mises(data)
report = generate_report(data)
print(report)

# 函数式编程风格 — 数据流经一系列函数
# pipeline(data, [read_stress_file, calc_all_von_mises, generate_report])


# ═══════════════════════════════════════════════════════════════
# 7. 最佳实践
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  7. 函数最佳实践")
print("=" * 60)

print("""
  ✅ 每个函数只做一件事 (Single Responsibility)
  ✅ 函数名用动词: calc_*, get_*, read_*, write_*, check_*, find_*
  ✅ 有类型注解和 docstring
  ✅ 输入输出明确
  ✅ ≤ 50 行
  ✅ 纯函数优先 (不修改全局状态，不修改输入参数)
  ✅ 避免"上帝函数" (一个函数做所有事)

  ❌ 函数中有隐藏的副作用
  ❌ 用可变默认参数
  ❌ 参数过多 (>5个考虑用 dataclass 封装)
  ❌ 返回类型不一致 (有时 dict，有时 list)
""")


# ═══════════════════════════════════════════════════════════════
# 8. 练习
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 编写函数 calc_tresca(sx, sy, sz, txy, tyz, tzx)
     计算 Tresca (最大剪应力) 准则的等效应力。

  2. 编写函数 interpolate(x, xp, fp) — 线性插值。
     xp 和 fp 是已知数据点，x 是待插值点。

  3. 以下函数有什么问题？
     def process_data(data, result=[]):
         result.append(sum(data))
         return result

  4. 将以下代码重构为函数:
     # 读 CSV 文件
     data = []
     with open('results.csv') as f:
         for line in f:
             parts = line.strip().split(',')
             data.append(float(parts[1]))
     # 计算统计
     avg = sum(data) / len(data)
     print(f"平均值: {avg}")
     # 找最大值
     maximum = max(data)
     print(f"最大值: {maximum}")
""")

if __name__ == "__main__":
    print("\n✅ 函数示例运行完成。阅读上方输出并完成练习。")
