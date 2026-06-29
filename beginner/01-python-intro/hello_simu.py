"""
SimuLearn Scripts — 初级示例：你的第一个工程脚本
=================================================
知识点：Python 工程应用概览 (beginner/01-python-intro)

这个脚本展示 Python 在仿真工程中的典型工作流：
  1. 定义仿真输入参数
  2. 读取/生成结果数据
  3. 计算工程指标
  4. 输出报告

运行方式：
  python hello_simu.py
"""

import math
import sys
from datetime import datetime


# ─────────────────────────────────────────────────────────────
# 1. 配置区 — 将所有可调参数集中在这里
# ─────────────────────────────────────────────────────────────
CONFIG = {
    "beam_length_m": 1.0,          # 梁长度 [m]
    "beam_width_mm": 50.0,         # 梁截面宽度 [mm]
    "beam_height_mm": 100.0,       # 梁截面高度 [mm]
    "force_kN": 10.0,              # 施加力 [kN]
    "material": "Q235",            # 材料牌号
    "elastic_modulus_GPa": 200.0,  # 弹性模量 [GPa]
    "yield_strength_MPa": 235.0,   # 屈服强度 [MPa]
    "safety_factor": 1.5,          # 安全系数
}


# ─────────────────────────────────────────────────────────────
# 2. 函数区 — 每个函数只做一件事
# ─────────────────────────────────────────────────────────────

def calc_section_properties(width_mm: float, height_mm: float) -> dict:
    """计算矩形截面几何属性。

    Args:
        width_mm: 截面宽度 [mm]
        height_mm: 截面高度 [mm]

    Returns:
        包含面积、惯性矩和截面模量的字典
    """
    width_m = width_mm / 1000.0
    height_m = height_mm / 1000.0

    area_m2 = width_m * height_m
    I_m4 = width_m * height_m**3 / 12.0          # 惯性矩 [m⁴]
    W_m3 = I_m4 / (height_m / 2.0)                # 截面模量 [m³]

    return {
        "area_m2": area_m2,
        "I_m4": I_m4,
        "W_m3": W_m3,
        "width_m": width_m,
        "height_m": height_m,
    }


def calc_beam_stress(
    force_N: float,
    length_m: float,
    W_m3: float,
) -> dict:
    """计算简支梁跨中最大应力。

    Args:
        force_N: 跨中集中力 [N]
        length_m: 梁长 [m]
        W_m3: 截面模量 [m³]

    Returns:
        包含弯矩和应力的字典
    """
    M_max_Nm = force_N * length_m / 4.0           # 最大弯矩 [N·m]
    sigma_max_Pa = M_max_Nm / W_m3                 # 最大弯曲应力 [Pa]
    sigma_max_MPa = sigma_max_Pa / 1e6             # 转换为 [MPa]

    return {
        "M_max_Nm": M_max_Nm,
        "sigma_max_MPa": sigma_max_MPa,
    }


def check_design(
    sigma_MPa: float,
    yield_MPa: float,
    safety_factor: float,
) -> dict:
    """根据屈服准则判断设计是否通过。

    Args:
        sigma_MPa: 计算应力 [MPa]
        yield_MPa: 材料屈服强度 [MPa]
        safety_factor: 安全系数

    Returns:
        包含校核结果的字典
    """
    allowable_MPa = yield_MPa / safety_factor
    utilization = sigma_MPa / allowable_MPa
    passed = utilization <= 1.0

    return {
        "allowable_MPa": allowable_MPa,
        "utilization": utilization,
        "passed": passed,
        "status": "✅ 通过" if passed else "❌ 不通过",
    }


# ─────────────────────────────────────────────────────────────
# 3. 主流程区
# ─────────────────────────────────────────────────────────────

def main():
    print("=" * 60)
    print("  SimuLearn Scripts — 简支梁强度校核")
    print(f"  运行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # 提取配置参数
    L = CONFIG["beam_length_m"]
    b = CONFIG["beam_width_mm"]
    h = CONFIG["beam_height_mm"]
    F = CONFIG["force_kN"] * 1000.0           # kN → N
    E = CONFIG["elastic_modulus_GPa"] * 1e9    # GPa → Pa
    sigma_y = CONFIG["yield_strength_MPa"]
    sf = CONFIG["safety_factor"]

    # 步骤1：计算截面属性
    section = calc_section_properties(b, h)
    print(f"\n📐 截面属性:")
    print(f"   面积 A = {section['area_m2']:.6f} m²")
    print(f"   惯性矩 I = {section['I_m4']:.6e} m⁴")
    print(f"   截面模量 W = {section['W_m3']:.6e} m³")

    # 步骤2：计算应力
    result = calc_beam_stress(F, L, section["W_m3"])
    print(f"\n📊 受力分析:")
    print(f"   最大弯矩 M_max = {result['M_max_Nm']:.2f} N·m")
    print(f"   最大弯曲应力 σ_max = {result['sigma_max_MPa']:.2f} MPa")

    # 步骤3：校核
    check = check_design(result["sigma_max_MPa"], sigma_y, sf)
    print(f"\n🔍 强度校核:")
    print(f"   材料: {CONFIG['material']} (σ_y = {sigma_y} MPa)")
    print(f"   安全系数: {sf}")
    print(f"   许用应力 [σ] = {check['allowable_MPa']:.2f} MPa")
    print(f"   利用率 = {check['utilization']:.2%}")
    print(f"   结论: {check['status']}")

    # 步骤4：附加检查
    max_deflection_m = F * L**3 / (48 * E * section["I_m4"])
    deflection_ratio = max_deflection_m / L
    print(f"\n📏 刚度校核:")
    print(f"   最大挠度 = {max_deflection_m*1000:.3f} mm")
    print(f"   挠跨比 = 1/{1/deflection_ratio:.0f}")
    limit = 1/250
    if deflection_ratio <= limit:
        print(f"   结论: ✅ 满足 L/250 限值")
    else:
        print(f"   结论: ❌ 超过 L/250 限值 ({1/limit:.0f})")

    print("\n" + "=" * 60)
    print("  分析完成。")
    print("=" * 60)

    return 0 if check["passed"] else 1


if __name__ == "__main__":
    sys.exit(main())
