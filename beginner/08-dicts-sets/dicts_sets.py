"""
SimuLearn Scripts — 初级 #08：字典与集合
=========================================
知识点：dicts-and-sets

字典是仿真中最强大的数据结构之一：
  - 材料参数库 (材料名 → 属性)
  - 工况索引 (工况名 → 结果)
  - 节点结果缓存 (节点ID → 应力)
集合用于去重操作和维护标签。

本节涵盖：
  1. 字典创建与访问
  2. 字典方法
  3. 嵌套字典
  4. 集合基础
  5. 工程案例

运行方式：
  python dicts_sets.py
"""

# ═══════════════════════════════════════════════════════════════
# 1. 字典创建与访问
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 字典创建与访问")
print("=" * 60)

# 创建字典 — 键值对
material = {
    "name": "Q235",
    "E": 200e9,       # 弹性模量 [Pa]
    "nu": 0.3,        # 泊松比
    "density": 7850,  # 密度 [kg/m³]
    "yield": 235e6,   # 屈服强度 [Pa]
}
print(f"材料字典: {material}")

# 访问
print(f"\n访问:")
print(f"  material['name'] = {material['name']}")
print(f"  material['E'] = {material['E']/1e9:.0f} GPa")

# 安全访问 — get() 避免 KeyError
print(f"\n安全访问 (get):")
print(f"  material.get('E') = {material.get('E')}")
print(f"  material.get('ultimate') = {material.get('ultimate')}")  # None
print(f"  material.get('ultimate', '未知') = {material.get('ultimate', '未知')}")

# 不存在的键 — 直接访问会崩溃
try:
    _ = material["ultimate"]
except KeyError as e:
    print(f"  material['ultimate'] → KeyError: {e}")

# 添加/修改
material["thermal_expansion"] = 1.2e-5  # 热膨胀系数
material["yield"] = 250e6  # 更新屈服强度 (Q235→Q250)
print(f"\n添加/修改后: {material}")


# ═══════════════════════════════════════════════════════════════
# 2. 字典方法
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. 字典方法")
print("=" * 60)

# keys(), values(), items()
print(f"键 (keys):   {list(material.keys())}")
print(f"值 (values): {[f'{v:.1e}' if isinstance(v, float) else v for v in material.values()]}")

# 遍历 — items() 是最常见的
print(f"\n遍历所有属性:")
for key, value in material.items():
    if isinstance(value, float) and value > 1000:
        print(f"  {key:<20s} = {value:.2e}")
    else:
        print(f"  {key:<20s} = {value}")

# 检查键是否存在
print(f"\n键存在性:")
print(f"  'E' in material → {'E' in material}")
print(f"  'Poisson' in material → {'Poisson' in material}")

# 删除
removed = material.pop("thermal_expansion")
print(f"\npop('thermal_expansion') = {removed}")
print(f"删除后: {list(material.keys())}")

# 合并
defaults = {"source": "GB/T 1591", "temperature_range": (-20, 400)}
material.update(defaults)
print(f"合并默认值后: {material}")


# ═══════════════════════════════════════════════════════════════
# 3. 嵌套字典 — 材料数据库
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 嵌套字典 — 材料数据库")
print("=" * 60)

materials_db = {
    "Q235": {
        "E": 200e9,
        "nu": 0.3,
        "density": 7850,
        "yield": 235e6,
        "type": "碳素结构钢",
        "temperature_max_C": 350,
    },
    "Q345": {
        "E": 206e9,
        "nu": 0.3,
        "density": 7850,
        "yield": 345e6,
        "type": "低合金高强度钢",
        "temperature_max_C": 400,
    },
    "6061-T6": {
        "E": 69e9,
        "nu": 0.33,
        "density": 2700,
        "yield": 276e6,
        "type": "铝合金",
        "temperature_max_C": 150,
    },
}

# 查询
for name, props in materials_db.items():
    print(f"\n{name} ({props['type']}):")
    print(f"  E = {props['E']/1e9:.0f} GPa")
    print(f"  σy = {props['yield']/1e6:.0f} MPa")
    print(f"  ρ = {props['density']} kg/m³")
    print(f"  Tmax = {props['temperature_max_C']}°C")

# 按条件筛选 — 找所有屈服 > 250 MPa 的材料
print(f"\n筛选 σy > 250 MPa:")
high_strength = {
    name: props for name, props in materials_db.items()
    if props["yield"] > 250e6
}
for name in high_strength:
    print(f"  {name}: σy = {high_strength[name]['yield']/1e6:.0f} MPa")


# ═══════════════════════════════════════════════════════════════
# 4. 集合 — 去重与集合运算
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 集合 (set)")
print("=" * 60)

# 创建集合 — 自动去重
node_ids = [1, 2, 2, 3, 3, 3, 4, 5, 5]
unique_nodes = set(node_ids)
print(f"原始: {node_ids}")
print(f"去重: {unique_nodes}")

# 集合运算
contact_nodes = {1, 2, 3, 10, 11}     # 接触区域的节点
load_nodes = {3, 4, 5, 11, 12}         # 施加载荷的节点

print(f"\n接触区域节点: {contact_nodes}")
print(f"施加载荷节点: {load_nodes}")

print(f"\n集合运算:")
print(f"  交集 (&):  {contact_nodes & load_nodes}     ← 同时是接触和加载点")
print(f"  并集 (|):  {contact_nodes | load_nodes}    ← 所有需要关注的节点")
print(f"  差集 (-):  {contact_nodes - load_nodes}    ← 仅接触，不加载")
print(f"  对称差 (^): {contact_nodes ^ load_nodes}    ← 仅在一个集合中")

# 添加/删除
color_set = {"red", "green", "blue"}
color_set.add("yellow")
color_set.discard("red")  # 不存在也不报错
print(f"\n颜色集合: {color_set}")

# 成员检查 — 极快 (O(1))
print(f"  'blue' in color_set → {'blue' in color_set}")
print(f"  'red' in color_set → {'red' in color_set}")


# ═══════════════════════════════════════════════════════════════
# 5. 工程案例
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 工程案例")
print("=" * 60)

# 案例1：用字典替代多重 if-elif
# ❌ 不好的方式
def get_material_factor_bad(name):
    if name == "Q235":
        return 1.0
    elif name == "Q345":
        return 1.1
    elif name == "Q420":
        return 1.2
    else:
        return 1.0

# ✅ 用字典
MATERIAL_FACTORS = {
    "Q235": 1.0,
    "Q345": 1.1,
    "Q420": 1.2,
}
def get_material_factor(name):
    return MATERIAL_FACTORS.get(name, 1.0)

print(f"材料系数 (字典查找):")
for m in ["Q235", "Q345", "Q420", "Unknown"]:
    print(f"  {m}: {get_material_factor(m)}")

# 案例2：工况结果缓存
print(f"\n工况结果缓存:")
case_results = {}

# 模拟批量分析结果存储
for case_id in range(1, 4):
    case_results[case_id] = {
        "max_stress_MPa": 150 + case_id * 20,
        "max_disp_mm": 0.5 + case_id * 0.1,
        "converged": True,
    }

# 查询
for cid, result in case_results.items():
    print(f"  工况 {cid}: σmax={result['max_stress_MPa']} MPa, "
          f"dmax={result['max_disp_mm']:.1f} mm, "
          f"{'✅' if result['converged'] else '❌'}")

# 案例3：用集合追踪失败节点
print(f"\n失效模式追踪:")
failed_tensile = {5, 12, 23, 45, 67}     # 拉伸失效节点
failed_compressive = {3, 12, 34, 45, 78}  # 压缩失效节点
failed_shear = {12, 23, 56, 67, 89}       # 剪切失效节点

# 所有失效节点（任一模式）
all_failed = failed_tensile | failed_compressive | failed_shear
print(f"总失效节点数: {len(all_failed)}")

# 多模式失效节点
multi_fail = (failed_tensile & failed_compressive) | \
             (failed_tensile & failed_shear) | \
             (failed_compressive & failed_shear)
print(f"多模式失效节点: {sorted(multi_fail)}")

# 仅拉伸失效（不含其他模式）
only_tensile = failed_tensile - failed_compressive - failed_shear
print(f"仅拉伸失效: {only_tensile}")


# ═══════════════════════════════════════════════════════════════
# 6. 字典推导式
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 字典推导式")
print("=" * 60)

# 创建节点ID→位移的映射
node_disps = {i: round(0.001 * i**0.5, 6) for i in range(1, 6)}
print(f"节点位移映射: {node_disps}")

# 反转映射 (注意：值可能重复)
# {位移: 节点ID列表}
disp_to_nodes = {}
for node, disp in node_disps.items():
    disp_to_nodes.setdefault(disp, []).append(node)
print(f"位移→节点: {disp_to_nodes}")

# 过滤字典
filtered = {k: v for k, v in node_disps.items() if v > 0.0015}
print(f"位移 > 0.0015: {filtered}")


# ═══════════════════════════════════════════════════════════════
# 7. 默认字典与计数器
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  7. defaultdict 和 Counter")
print("=" * 60)

# defaultdict — 自动为缺失键创建默认值
from collections import defaultdict

# 按单元类型统计节点数
element_nodes = defaultdict(list)
elements = [
    ("SOLID185", 1), ("SOLID185", 2), ("SHELL181", 3),
    ("SOLID185", 4), ("SHELL181", 5), ("BEAM188", 6),
]

for etype, node in elements:
    element_nodes[etype].append(node)

for etype, nodes in element_nodes.items():
    print(f"  {etype}: {len(nodes)} 个节点 → {nodes}")

# Counter — 快速计数
from collections import Counter

# 统计各应力区间节点数
stresses = [150, 180, 220, 240, 160, 205, 175, 230, 190, 210]
intervals = []
for s in stresses:
    if s < 180:
        intervals.append("低 (<180)")
    elif s < 210:
        intervals.append("中 (180-210)")
    else:
        intervals.append("高 (>210)")

stress_dist = Counter(intervals)
print(f"\n应力分布:")
for level, count in stress_dist.most_common():
    print(f"  {level}: {count} 个节点")


# ═══════════════════════════════════════════════════════════════
# 8. 练习
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 创建一个字典存储你常用的3种材料参数，写一个函数
     get_material(name, property) 来安全访问。

  2. 有节点集合 A = {1,2,3,4,5}（固定端）和 B = {3,4,5,6,7}（载荷端），
     找出仅属于固定端的节点和仅属于载荷端的节点。

  3. 用字典推导式将以下列表转为字典：
     materials = ['Q235', 'Q345', '45#']
     yields = [235, 345, 355]
     → {'Q235': 235, 'Q345': 345, '45#': 355}

  4. 用 Counter 统计一段 ANSYS 日志中 ERROR 和 WARNING 的
     出现次数。
""")
