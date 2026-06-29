"""
SimuLearn Scripts — 初级 #14：ANSYS 中的数据类型
=================================================
知识点：ansys-data-types

理解 ANSYS 输出的标量、向量、张量和表格数据，
将其转化为 Python 数据结构。

本节涵盖：
  1. ANSYS 输出数据类型概览
  2. 标量 (温度、时间、最大值)
  3. 向量 (节点位移)
  4. 张量 (应力/应变)
  5. 表格数据 (载荷步历史)

运行方式：
  python ansys_data_types.py
"""

import numpy as np

# ═══════════════════════════════════════════════════════════════
# 1. ANSYS 输出数据类型概览
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. ANSYS 输出数据类型概览")
print("=" * 60)

print("""
  ANSYS 输出的数据类型:

  标量  → float    温度最大值、总质量、收敛残差
  向量  → list[3]  节点位移 UX,UY,UZ
  张量  → list[6]  应力 SX,SY,SZ,SXY,SYZ,SXZ
  表格  → list[dict]  多载荷步结果历史

  Python 对应:
  标量  → float / int
  向量  → [x, y, z] 或 dict 或 np.array(3)
  张量  → [sx,sy,sz,sxy,syz,szx] 或 np.array(6)
  表格  → [{step, max_stress, ...}, ...] 或 DataFrame
""")


# ═══════════════════════════════════════════════════════════════
# 2. 标量数据
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  2. 标量数据")
print("=" * 60)

# 典型 ANSYS 输出标量
scalars = {
    "total_mass_kg": 12.567,
    "max_temperature_C": 85.3,
    "min_temperature_C": 32.1,
    "convergence_residual": 1.5e-6,
    "num_elements": 125000,
    "analysis_time_s": 45.2,
}

print("标量示例:")
for name, value in scalars.items():
    print(f"  {name:<25s} = {value} ({type(value).__name__})")

# 标量的单位标注 — 用复合类型
from typing import NamedTuple

class ScalarWithUnit(NamedTuple):
    value: float
    unit: str
    description: str

max_stress = ScalarWithUnit(180.5, "MPa", "最大 von Mises 应力")
print(f"\n带单位的标量: {max_stress.value} {max_stress.unit} ({max_stress.description})")


# ═══════════════════════════════════════════════════════════════
# 3. 向量数据 — 节点位移
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 向量数据 — 节点位移")
print("=" * 60)

# 表示方式1: 简单列表
displacement_list = [0.001234, -0.000056, 0.0]
print(f"列表: {displacement_list}")

# 表示方式2: 字典（推荐）
displacement_dict = {
    "ux": 0.001234,
    "uy": -0.000056,
    "uz": 0.0,
    "usum": 0.001235,  # sqrt(ux²+uy²+uz²)
}
print(f"字典: {displacement_dict}")
print(f"  合位移: {displacement_dict['usum']:.4e} mm")

# 表示方式3: NumPy 数组（适合批量运算）
U = np.array([0.001234, -0.000056, 0.0])
magnitude = np.linalg.norm(U)
print(f"NumPy 数组: {U}")
print(f"  模长: {magnitude:.4e} mm")

# 表示方式4: NamedTuple
class Displacement(NamedTuple):
    ux: float
    uy: float
    uz: float

    @property
    def magnitude(self):
        return (self.ux**2 + self.uy**2 + self.uz**2) ** 0.5

disp = Displacement(0.001234, -0.000056, 0.0)
print(f"NamedTuple: UX={disp.ux} UY={disp.uy} UZ={disp.uz}")
print(f"  合位移: {disp.magnitude:.4e} mm")

# 批量节点的向量 — 矩阵形式
node_displacements = np.array([
    [0.001, -5e-5, 0.0],     # 节点1
    [0.002, -8e-5, 1e-6],    # 节点2
    [0.003, -1e-4, 2e-6],    # 节点3
])
print(f"\n多节点位移矩阵:")
print(f"  形状: {node_displacements.shape}")
print(f"  节点2 UX: {node_displacements[1, 0]:.4e}")


# ═══════════════════════════════════════════════════════════════
# 4. 张量数据 — 应力/应变张量
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 张量数据 — 应力/应变")
print("=" * 60)

# ANSYS 输出的顺序：SX, SY, SZ, SXY, SYZ, SXZ
stress_tensor = np.array([100.5, -20.3, -5.1, 10.0, 5.2, 2.8])

# 分量提取
sx, sy, sz, sxy, syz, sxz = stress_tensor

print(f"应力张量 (ANSYS 顺序):")
print(f"  正应力: σx={sx}  σy={sy}  σz={sz}")
print(f"  剪应力: τxy={sxy}  τyz={syz}  τzx={sxz}")

# 计算 von Mises 等效应力
def calc_vm_vectorized(stress):
    """批量计算 von Mises 应力。"""
    s = stress  # shape: (..., 6)
    d12 = s[..., 0] - s[..., 1]
    d23 = s[..., 1] - s[..., 2]
    d31 = s[..., 2] - s[..., 0]
    return np.sqrt(0.5 * (d12**2 + d23**2 + d31**2
                          + 6.0 * (s[..., 3]**2 + s[..., 4]**2 + s[..., 5]**2)))

vm = calc_vm_vectorized(stress_tensor)
print(f"\nvon Mises 等效应力: {vm:.1f} MPa")

# 批量节点应力
node_stresses = np.array([
    [100.5, -20.3, -5.1, 10.0, 5.2, 2.8],
    [98.7, -18.9, -4.8, 9.5, 4.9, 2.5],
    [102.1, -21.0, -5.3, 10.8, 5.5, 3.0],
])
vms = calc_vm_vectorized(node_stresses)
print(f"\n批量 von Mises:")
for i, vm_val in enumerate(vms, 1):
    print(f"  节点 {i}: {vm_val:.1f} MPa")

# 应力张量的 Python 字典表示
stress_dict = {
    "normal": {"x": 100.5, "y": -20.3, "z": -5.1},
    "shear": {"xy": 10.0, "yz": 5.2, "zx": 2.8},
}
print(f"\n字典表示: {stress_dict}")


# ═══════════════════════════════════════════════════════════════
# 5. 表格数据 — 载荷步历史
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 表格数据 — 载荷步历史")
print("=" * 60)

# 表示方式1: 列表嵌套字典
history_dicts = [
    {"step": 1, "time_s": 0.0, "max_stress_MPa": 0.0, "max_disp_mm": 0.0},
    {"step": 2, "time_s": 0.5, "max_stress_MPa": 120.0, "max_disp_mm": 0.5},
    {"step": 3, "time_s": 1.0, "max_stress_MPa": 180.5, "max_disp_mm": 0.8},
    {"step": 4, "time_s": 1.5, "max_stress_MPa": 175.2, "max_disp_mm": 1.1},
    {"step": 5, "time_s": 2.0, "max_stress_MPa": 185.0, "max_disp_mm": 1.3},
]

print("载荷步历史 (dict):")
for row in history_dicts:
    print(f"  Step {row['step']:2d} @ t={row['time_s']:.1f}s: "
          f"σmax={row['max_stress_MPa']:.1f} MPa, "
          f"dmax={row['max_disp_mm']:.2f} mm")

# 提取列
times = [r["time_s"] for r in history_dicts]
stresses = [r["max_stress_MPa"] for r in history_dicts]
print(f"\n时间序列: {times}")
print(f"应力序列: {stresses}")

# 表示方式2: NumPy 结构化数组
# （适合大规模数据的高效存储）

# 表示方式3: Pandas DataFrame（下个知识点）


# ═══════════════════════════════════════════════════════════════
# 6. 张量不变量计算
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 应力张量不变量")
print("=" * 60)

def stress_invariants(sx, sy, sz, sxy, syz, sxz):
    """计算应力张量的三个不变量。"""
    # I1 = σx + σy + σz (第一不变量 = 3×平均应力)
    I1 = sx + sy + sz

    # I2 (第二不变量)
    I2 = (sx*sy + sy*sz + sz*sx
          - sxy**2 - syz**2 - sxz**2)

    # I3 (第三不变量 = 行列式)
    I3 = (sx*sy*sz + 2*sxy*syz*sxz
          - sx*syz**2 - sy*sxz**2 - sz*sxy**2)

    # 偏应力第二不变量 J2
    p = I1 / 3
    J2 = (I1**2 - 3*I2) / 3

    # von Mises = sqrt(3 * J2)
    vm = np.sqrt(3 * J2)

    return {
        "I1": I1,
        "I2": I2,
        "I3": I3,
        "J2": J2,
        "hydrostatic": p,
        "von_mises": vm,
    }

inv = stress_invariants(100.5, -20.3, -5.1, 10.0, 5.2, 2.8)
print("应力张量不变量:")
for name, value in inv.items():
    if abs(value) > 1:
        print(f"  {name:<15s} = {value:.1f}")
    else:
        print(f"  {name:<15s} = {value:.4e}")


# ═══════════════════════════════════════════════════════════════
# 7. 工程实践
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  7. 工程实践建议")
print("=" * 60)

print("""
  数据表示选型:

  单个标量      → float
  单个向量      → dict 或 NamedTuple
  多个向量      → np.array((n, 3))
  单个张量      → np.array(6) 或 dict
  多个张量      → np.array((n, 6))
  表格数据      → list[dict] 或 pandas DataFrame
  超大数据(>1GB) → NumPy memmap 或 HDF5 (h5py)

  关键原则:
  ✅ 保持数据原始顺序 (尤其是 ANSYS 的 [SX,SY,SZ,SXY,SYZ,SXZ])
  ✅ 始终记录单位和坐标系
  ✅ 用 docstring 说明数组各维度的含义
  ✅ 验证形状 (check .shape) 避免维度错误
""")


# ═══════════════════════════════════════════════════════════════
# 8. 练习
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. ANSYS 输出的节点应力是 [SX, SY, SZ, SXY, SYZ, SXZ]。
     写代码从这个列表提取：
     - 三个主应力分量
     - 三个剪应力分量
     - 应力球量 p = (σx + σy + σz) / 3

  2. 有一个多节点位移数组 (n×3)，计算所有节点的合位移，
     找出位移最大的节点索引。

  3. 将载荷步历史数据 (step, time, max_stress) 转换为
     NumPy 数组，分别提取 time 和 stress 做趋势分析。
""")
