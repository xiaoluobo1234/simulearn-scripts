"""
SimuLearn Scripts — 单位换算工具
=================================
知识点：仿真单位换算脚本 (beginner/19-unit-conversion)

提供常用工程单位制之间的换算功能。
所有换算因子有单一事实来源，避免散落在各脚本中。

支持的换算类别：
  - 长度 (mm, cm, m, inch, ft)
  - 力 (N, kN, MN, lbf, kgf)
  - 应力/压力 (Pa, kPa, MPa, GPa, psi, ksi, bar, atm)
  - 质量 (kg, g, ton, lbm, slug)
  - 密度 (kg/m³, g/cm³, lbm/in³)
  - 温度 (K, °C, °F 偏移)
  - 能量 (J, kJ, cal, BTU)
  - 功率 (W, kW, MW, hp)
  - 角度 (rad, deg)

使用方式：
  from utils.unit_converter import convert, list_units

  stress_pa = convert(350, "MPa", "Pa")    # → 350_000_000
  length_mm = convert(5.0, "inch", "mm")   # → 127.0
"""

from typing import Union

# ─────────────────────────────────────────────────────────────
# 换算因子 — 全部以 SI 单位为基准
# ─────────────────────────────────────────────────────────────

# 类别: {单位: {因子: float, 偏移: float (仅温度), 类别: str}}
# 因子含义: value_in_si = value_in_unit * factor + offset

_UNITS = {
    # ── 长度 [基准: m] ──
    "nm":  {"factor": 1e-9,        "offset": 0.0, "category": "长度"},
    "µm":  {"factor": 1e-6,        "offset": 0.0, "category": "长度"},
    "mm":  {"factor": 1e-3,        "offset": 0.0, "category": "长度"},
    "cm":  {"factor": 1e-2,        "offset": 0.0, "category": "长度"},
    "m":   {"factor": 1.0,         "offset": 0.0, "category": "长度"},
    "km":  {"factor": 1e3,         "offset": 0.0, "category": "长度"},
    "inch":{"factor": 0.0254,      "offset": 0.0, "category": "长度"},
    "ft":  {"factor": 0.3048,      "offset": 0.0, "category": "长度"},
    "mil": {"factor": 2.54e-5,     "offset": 0.0, "category": "长度"},

    # ── 力 [基准: N] ──
    "N":   {"factor": 1.0,         "offset": 0.0, "category": "力"},
    "kN":  {"factor": 1e3,         "offset": 0.0, "category": "力"},
    "MN":  {"factor": 1e6,         "offset": 0.0, "category": "力"},
    "lbf": {"factor": 4.4482216,   "offset": 0.0, "category": "力"},
    "kgf": {"factor": 9.80665,     "offset": 0.0, "category": "力"},
    "dyne":{"factor": 1e-5,        "offset": 0.0, "category": "力"},

    # ── 应力/压力 [基准: Pa] ──
    "Pa":  {"factor": 1.0,         "offset": 0.0, "category": "应力/压力"},
    "kPa": {"factor": 1e3,         "offset": 0.0, "category": "应力/压力"},
    "MPa": {"factor": 1e6,         "offset": 0.0, "category": "应力/压力"},
    "GPa": {"factor": 1e9,         "offset": 0.0, "category": "应力/压力"},
    "psi": {"factor": 6894.757,    "offset": 0.0, "category": "应力/压力"},
    "ksi": {"factor": 6.894757e6,  "offset": 0.0, "category": "应力/压力"},
    "bar": {"factor": 1e5,         "offset": 0.0, "category": "应力/压力"},
    "atm": {"factor": 101325.0,    "offset": 0.0, "category": "应力/压力"},
    "torr":{"factor": 133.322,     "offset": 0.0, "category": "应力/压力"},

    # ── 质量 [基准: kg] ──
    "g":   {"factor": 1e-3,        "offset": 0.0, "category": "质量"},
    "kg":  {"factor": 1.0,         "offset": 0.0, "category": "质量"},
    "ton": {"factor": 1e3,         "offset": 0.0, "category": "质量"},  # metric ton
    "lbm": {"factor": 0.45359237,  "offset": 0.0, "category": "质量"},
    "slug":{"factor": 14.5939,     "offset": 0.0, "category": "质量"},
    "oz":  {"factor": 0.0283495,   "offset": 0.0, "category": "质量"},

    # ── 密度 [基准: kg/m³] ──
    "kg/m3":   {"factor": 1.0,       "offset": 0.0, "category": "密度"},
    "g/cm3":   {"factor": 1000.0,    "offset": 0.0, "category": "密度"},
    "lbm/in3": {"factor": 27679.9,   "offset": 0.0, "category": "密度"},
    "lbm/ft3": {"factor": 16.0185,   "offset": 0.0, "category": "密度"},

    # ── 温度 [基准: K] ── (使用偏移)
    "K":  {"factor": 1.0,          "offset": 0.0,    "category": "温度"},
    "°C": {"factor": 1.0,          "offset": 273.15, "category": "温度"},
    "°F": {"factor": 5.0/9.0,      "offset": 255.372222, "category": "温度"},
    # Note: °F→K: (F + 459.67) × 5/9 → offset = 459.67*5/9 = 255.3722...

    # ── 能量 [基准: J] ──
    "J":   {"factor": 1.0,         "offset": 0.0, "category": "能量"},
    "kJ":  {"factor": 1e3,         "offset": 0.0, "category": "能量"},
    "MJ":  {"factor": 1e6,         "offset": 0.0, "category": "能量"},
    "cal": {"factor": 4.184,       "offset": 0.0, "category": "能量"},
    "kcal":{"factor": 4184.0,      "offset": 0.0, "category": "能量"},
    "BTU": {"factor": 1055.06,     "offset": 0.0, "category": "能量"},
    "eV":  {"factor": 1.602176634e-19, "offset": 0.0, "category": "能量"},

    # ── 功率 [基准: W] ──
    "W":  {"factor": 1.0,          "offset": 0.0, "category": "功率"},
    "kW": {"factor": 1e3,          "offset": 0.0, "category": "功率"},
    "MW": {"factor": 1e6,          "offset": 0.0, "category": "功率"},
    "hp": {"factor": 745.6999,     "offset": 0.0, "category": "功率"},  # mechanical hp

    # ── 角度 [基准: rad] ──
    "rad": {"factor": 1.0,         "offset": 0.0, "category": "角度"},
    "deg": {"factor": 3.141592653589793/180.0, "offset": 0.0, "category": "角度"},
}


def _check_unit(unit: str) -> None:
    """检查单位是否已注册。"""
    if unit not in _UNITS:
        available = ", ".join(sorted(_UNITS.keys()))
        raise ValueError(f"未知单位 '{unit}'。可用单位: {available}")


def convert(value: Union[float, int], from_unit: str, to_unit: str) -> float:
    """在两个注册单位之间换算。

    Args:
        value: 数值
        from_unit: 源单位
        to_unit: 目标单位

    Returns:
        换算后的数值

    Raises:
        ValueError: 单位未注册或跨类别换算

    Example:
        >>> convert(350, "MPa", "Pa")
        350000000.0
        >>> convert(100, "°C", "K")
        373.15
        >>> convert(5.0, "inch", "mm")
        127.0
    """
    _check_unit(from_unit)
    _check_unit(to_unit)

    src = _UNITS[from_unit]
    dst = _UNITS[to_unit]

    if src["category"] != dst["category"]:
        raise ValueError(
            f"无法跨类别换算: '{from_unit}' ({src['category']}) → "
            f"'{to_unit}' ({dst['category']})"
        )

    # 先转到 SI，再转到目标单位
    si_value = value * src["factor"] + src["offset"]
    return (si_value - dst["offset"]) / dst["factor"]


def list_units(category: str = None) -> dict:
    """列出所有注册单位，可选按类别筛选。

    Args:
        category: 类别名称，为 None 时返回全部

    Returns:
        {单位: 元信息} 字典
    """
    if category:
        return {u: info for u, info in _UNITS.items()
                if info["category"] == category}
    return dict(_UNITS)


def list_categories() -> list:
    """列出所有单位类别。"""
    return sorted(set(info["category"] for info in _UNITS.values()))


# ─────────────────────────────────────────────────────────────
# 便捷函数 — 常用换算的简短别名
# ─────────────────────────────────────────────────────────────

def MPa_to_Pa(value: float) -> float:
    """MPa → Pa"""
    return value * 1e6


def Pa_to_MPa(value: float) -> float:
    """Pa → MPa"""
    return value / 1e6


def mm_to_m(value: float) -> float:
    """mm → m"""
    return value / 1000.0


def m_to_mm(value: float) -> float:
    """m → mm"""
    return value * 1000.0


def celsius_to_kelvin(value: float) -> float:
    """°C → K"""
    return value + 273.15


def kelvin_to_celsius(value: float) -> float:
    """K → °C"""
    return value - 273.15


def kN_to_N(value: float) -> float:
    """kN → N"""
    return value * 1000.0


def N_to_kN(value: float) -> float:
    """N → kN"""
    return value / 1000.0


# ─────────────────────────────────────────────────────────────
# 自测
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 基本换算测试
    assert abs(convert(350, "MPa", "Pa") - 350_000_000) < 0.01
    assert abs(convert(5.0, "inch", "mm") - 127.0) < 0.01
    assert abs(convert(100, "°C", "K") - 373.15) < 0.01
    assert abs(convert(32, "°F", "°C") - 0.0) < 0.01
    assert abs(convert(0, "°C", "°F") - 32.0) < 0.1
    assert abs(convert(90, "deg", "rad") - 1.5707963) < 1e-6
    assert abs(convert(1, "hp", "W") - 745.6999) < 0.01
    assert abs(convert(1, "g/cm3", "kg/m3") - 1000.0) < 0.01

    # 便捷函数测试
    assert MPa_to_Pa(1) == 1_000_000
    assert Pa_to_MPa(1_000_000) == 1
    assert mm_to_m(1000) == 1.0
    assert celsius_to_kelvin(0) == 273.15

    # 错误情况
    try:
        convert(1, "MPa", "mm")  # 跨类别
        assert False, "应该抛出异常"
    except ValueError:
        pass

    try:
        convert(1, "furlong", "m")  # 未知单位
        assert False, "应该抛出异常"
    except ValueError:
        pass

    print("✅ 所有单位换算测试通过")
    print()
    print("可用类别:")
    for cat in list_categories():
        units = list_units(cat)
        print(f"  {cat}: {', '.join(units.keys())}")
