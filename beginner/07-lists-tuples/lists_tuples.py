"""
SimuLearn Scripts — 初级 #07：列表与元组
=========================================
知识点：lists-and-tuples

列表是仿真数据的主力容器：
  - 节点坐标序列
  - 载荷步列表
  - 结果集合
元组用于不可变记录：材料参数、固定配置。

本节涵盖：
  1. 列表创建与索引
  2. 列表切片
  3. 列表方法与操作
  4. 元组基础
  5. 列表推导式
  6. 工程应用案例

运行方式：
  python lists_tuples.py
"""

# ═══════════════════════════════════════════════════════════════
# 1. 列表创建与索引
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 列表创建与索引")
print("=" * 60)

# 创建列表 — 仿真中最常用的数据结构
node_ids = [1, 2, 3, 4, 5]
stresses = [100.5, -20.3, -5.1, 10.0, 5.2, 2.8]  # SX,SY,SZ,SXY,SYZ,SXZ
load_cases = ["自重", "风载", "地震"]
mixed = [1, "Q235", 200e9, True]  # 可以混合类型（但通常不建议）

print(f"节点编号: {node_ids}")
print(f"应力分量: {stresses}")

# 索引 — 从 0 开始
print(f"\n索引 (从0开始):")
print(f"  node_ids[0]  = {node_ids[0]}    (第一个)")
print(f"  node_ids[2]  = {node_ids[2]}    (第三个)")
print(f"  node_ids[-1] = {node_ids[-1]}   (倒数第一个)")
print(f"  node_ids[-2] = {node_ids[-2]}   (倒数第二个)")

# 应力分量的物理含义
labels = ["σx", "σy", "σz", "τxy", "τyz", "τzx"]
for i, label in enumerate(labels):
    print(f"  {label} = stresses[{i}] = {stresses[i]} MPa")


# ═══════════════════════════════════════════════════════════════
# 2. 列表切片 — 提取子集
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. 列表切片")
print("=" * 60)

numbers = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
print(f"原始: {numbers}")

# 切片语法: list[start:stop:step]
print(f"numbers[2:5]    = {numbers[2:5]}      (索引2到4)")
print(f"numbers[:4]     = {numbers[:4]}       (开头到索引3)")
print(f"numbers[5:]     = {numbers[5:]}       (索引5到结尾)")
print(f"numbers[::2]    = {numbers[::2]}      (每隔一个)")
print(f"numbers[::-1]   = {numbers[::-1]}     (倒序)")

# 仿真应用：提取时间序列的子集
time_steps = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
print(f"\n时间序列: {time_steps}")
print(f"前3步:    {time_steps[:3]}")
print(f"后3步:    {time_steps[-3:]}")
print(f"所有偶数步: {time_steps[::2]}")

# 提取应力分量中的正应力（前3个）和剪应力（后3个）
normal_stresses = stresses[:3]
shear_stresses = stresses[3:]
print(f"\n正应力: {normal_stresses}")
print(f"剪应力: {shear_stresses}")


# ═══════════════════════════════════════════════════════════════
# 3. 列表操作与方法
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 列表操作与方法")
print("=" * 60)

# 修改元素
nodes = [10, 20, 30, 40, 50]
print(f"原始: {nodes}")
nodes[2] = 35
print(f"修改[2]: {nodes}")

# 添加
nodes.append(60)           # 末尾添加
print(f"append(60): {nodes}")
nodes.insert(0, 5)         # 指定位置插入
print(f"insert(0, 5): {nodes}")
nodes.extend([70, 80])     # 扩展多个
print(f"extend([70,80]): {nodes}")

# 删除
removed = nodes.pop()      # 移除并返回末尾
print(f"pop(): {nodes} (返回 {removed})")
removed2 = nodes.pop(1)    # 移除索引1
print(f"pop(1): {nodes} (返回 {removed2})")
nodes.remove(35)           # 按值移除
print(f"remove(35): {nodes}")

# 查找
print(f"\n查找:")
print(f"  nodes.index(50) = {nodes.index(50)}")
print(f"  40 in nodes = {40 in nodes}")
print(f"  100 in nodes = {100 in nodes}")
print(f"  nodes.count(20) = {nodes.count(20)}")

# 排序
print(f"\n排序:")
unsorted = [50, 10, 40, 20, 30]
unsorted.sort()
print(f"  sort(): {unsorted}")
unsorted.sort(reverse=True)
print(f"  sort(reverse=True): {unsorted}")


# ═══════════════════════════════════════════════════════════════
# 4. 元组 — 不可变序列
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 元组 (tuple)")
print("=" * 60)

# 创建元组
coords = (100.0, 50.0, 0.0)  # 节点坐标 — 不变
material = ("Q235", 200e9, 0.3)  # (牌号, E, ν)

print(f"节点坐标: {coords}")
print(f"材料参数: {material}")

# 解包
x, y, z = coords
name, E, nu = material
print(f"\n解包: x={x}, y={y}, z={z}")
print(f"      材料={name}, E={E/1e9:.0f}GPa, ν={nu}")

# 元组不可修改
try:
    coords[0] = 200.0
except TypeError as e:
    print(f"\n尝试修改元组: TypeError: {e}")

# 为什么用元组？
print(f"\n元组 vs 列表:")
print(f"  ✅ 元组不可变 → 适合固定数据（材料参数、坐标）")
print(f"  ✅ 元组可哈希 → 可作为字典的键")
print(f"  ✅ 元组更快 → 比列表更轻量")
print(f"  ❌ 不能增删改元素 → 不适合动态数据")

# 单元素元组 — 注意逗号
single = (42,)  # 元组
not_tuple = (42)  # 只是整数！
print(f"\n单元素元组: {type(single)} ← 需要逗号")
print(f"不加逗号: {type(not_tuple)} ← 只是括号")


# ═══════════════════════════════════════════════════════════════
# 5. 列表推导式与工程过滤
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 列表推导式")
print("=" * 60)

# 基础：对所有应力分量取平方
squared = [s**2 for s in stresses]
print(f"应力平方: {[f'{s:.1f}' for s in squared]}")

# 过滤：只保留正应力
tensile = [s for s in stresses if s > 0]
print(f"拉应力 (>0): {tensile}")

# 变换+过滤：把位移从 m 转为 mm，只保留 > 1mm 的
disp_m = [0.0005, 0.0012, 0.0003, 0.0025, 0.0008]
disp_mm = [d * 1000 for d in disp_m if d * 1000 > 1.0]
print(f"位移 > 1mm: {disp_mm} mm")

# 嵌套推导式 — 多工况 × 多节点
print(f"\n多工况结果矩阵:")
n_cases, n_nodes = 3, 4
# 模拟各工况各节点的应力值
results = [[100 + c*10 + n*5 for n in range(n_nodes)] for c in range(n_cases)]
for c, case_data in enumerate(results):
    print(f"  工况{c+1}: {case_data}")

# 扁平化 — 展开为单一列表（所有工况所有节点）
all_stresses = [val for case in results for val in case]
print(f"\n所有应力值 (扁平化): {all_stresses}")


# ═══════════════════════════════════════════════════════════════
# 6. 工程应用
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 工程应用")
print("=" * 60)

# 用例1：将节点应力列表转化为节点ID->应力的映射
node_stresses = [
    (1, 100.5),
    (2, 98.7),
    (3, 102.1),
    (4, 95.3),
    (5, 105.8),
]

# 找出最大应力节点
max_node = max(node_stresses, key=lambda x: x[1])
print(f"最大应力: 节点 {max_node[0]}, σ = {max_node[1]} MPa")

# 按应力排序
sorted_nodes = sorted(node_stresses, key=lambda x: x[1], reverse=True)
print(f"应力排序 (高→低):")
for node, stress in sorted_nodes[:3]:
    print(f"  节点 {node}: {stress} MPa")

# 用例2：合并多载荷步的结果
step1 = [100, 98, 102]    # 载荷步1
step2 = [105, 102, 108]   # 载荷步2
step3 = [110, 107, 113]   # 载荷步3

# 计算每个节点的最大应力包络
envelope = [max(step[i] for step in [step1, step2, step3])
            for i in range(len(step1))]
print(f"\n应力包络 (3步):")
for i, s in enumerate(envelope, start=1):
    print(f"  节点 {i}: max = {s} MPa")

# 用例3：用列表实现简单的节点编号筛选
all_nodes = list(range(1, 101))  # 1~100
# 提取边界节点（假设 1-10 和 91-100）
boundary = all_nodes[:10] + all_nodes[-10:]
print(f"\n边界节点 (共{len(boundary)}个): {boundary}")

# 用 zip 同时遍历节点ID和结果
node_ids = [1, 2, 3, 4, 5]
displacements = [0.001, 0.002, 0.001, 0.003, 0.001]
print(f"\n节点位移报告:")
for nid, disp in zip(node_ids, displacements):
    flag = "⚠️" if disp > 0.002 else "✅"
    print(f"  {flag} 节点 {nid}: {disp*1000:.2f} mm")


# ═══════════════════════════════════════════════════════════════
# 7. 常见错误
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  7. 常见错误")
print("=" * 60)

print("""
  ❌ 错误1：索引越界
     nodes = [10, 20, 30]
     print(nodes[3])  ← IndexError! 最大索引是2

  ❌ 错误2：在遍历时修改列表
     for item in items:
         items.remove(item)  ← 跳过元素！

  ❌ 错误3：列表乘法创建嵌套列表
     matrix = [[0]*3]*3  ← 三个子列表是同一个对象！
     matrix[0][0] = 1  → [[1,0,0],[1,0,0],[1,0,0]]
  ✅ 正确：
     matrix = [[0]*3 for _ in range(3)]

  ❌ 错误4：把元组当成可修改的列表
     material = ("Q235", 200e9)
     material[0] = "Q345"  ← TypeError
""")


# ═══════════════════════════════════════════════════════════════
# 8. 练习
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 创建一个包含 10 个节点位移值（mm）的列表。
     用列表推导式计算所有位移的绝对值，并找出最大值。

  2. 有节点坐标列表 coords = [(0,0,0), (100,0,0), (100,50,0)]。
     写代码计算相邻节点之间的距离（两点间欧氏距离）。

  3. 为什么以下代码的行为与预期不同？
     grid = [[0]*3]*3
     grid[0][0] = 1
     print(grid)  # 输出什么？

  4. 用 zip 同时遍历三个列表（节点ID, X位移, Y位移），
     找出 X 和 Y 方向位移都超过 1mm 的节点。

  5. 列表 [1, 2, 3, 4, 5] 经过切片 [::-1] 后是什么？
     切片 [1:4:2] 的结果呢？
""")
