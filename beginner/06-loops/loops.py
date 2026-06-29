"""
SimuLearn Scripts — 初级 #06：循环结构
=======================================
知识点：loops-for-while

循环用于批量处理——仿真中最常见的需求：
  - 遍历所有工况
  - 遍历所有节点/单元
  - 遍历所有时间步
  - 参数扫描

本节涵盖：
  1. for 循环基础
  2. range() 和 enumerate()
  3. while 循环与收敛判定
  4. break / continue
  5. 嵌套循环
  6. 列表推导式预览
  7. 工程循环实战

运行方式：
  python loops.py
"""

# ═══════════════════════════════════════════════════════════════
# 1. for 循环 — 遍历已知集合
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. for 循环基础")
print("=" * 60)

# 遍历列表 — 所有载荷工况
load_cases = ["自重", "风载", "地震", "温度"]
print("工况列表:")
for case in load_cases:
    print(f"  分析工况: {case}")

# 遍历节点坐标
nodes = [(0.0, 0.0, 0.0), (100.0, 0.0, 0.0), (100.0, 50.0, 0.0)]
print(f"\n节点坐标:")
for x, y, z in nodes:  # 元组解包
    print(f"  ({x:6.1f}, {y:6.1f}, {z:6.1f})")

# 遍历字典 — 材料参数
materials = {
    "Q235": {"E": 200e9, "nu": 0.3, "density": 7850},
    "6061-T6": {"E": 69e9, "nu": 0.33, "density": 2700},
}
print(f"\n材料库:")
for name, props in materials.items():
    print(f"  {name}: E={props['E']/1e9:.0f} GPa, ν={props['nu']}")


# ═══════════════════════════════════════════════════════════════
# 2. range() 和 enumerate()
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. range() 和 enumerate()")
print("=" * 60)

# range(start, stop, step) — 生成整数序列
print("range(1, 11, 2):", list(range(1, 11, 2)))
print("range(5):       ", list(range(5)))       # 0 到 4
print("range(10, 0, -1):", list(range(10, 0, -1)))  # 递减

# 遍历载荷步
print(f"\n载荷步结果:")
for step in range(1, 6):
    load = step * 2000  # 每步增加 2000 N
    print(f"  Step {step}: F = {load} N")

# enumerate() — 同时获取索引和值
print(f"\n带索引遍历:")
loads = [2000, 4000, 6000, 8000, 10000]
for i, load in enumerate(loads, start=1):
    print(f"  工况 {i}: 载荷 = {load} N")

# 循环体中使用索引 — 追踪进度
print(f"\n进度追踪:")
for i, case in enumerate(load_cases, start=1):
    progress = i / len(load_cases) * 100
    print(f"  [{progress:3.0f}%] {case}")


# ═══════════════════════════════════════════════════════════════
# 3. while 循环 — 未知终止条件
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. while 循环")
print("=" * 60)

# 典型应用：收敛判定
print("非线性求解模拟:")
residual = 1.0
tolerance = 1e-3
iteration = 0
max_iter = 100

while residual > tolerance and iteration < max_iter:
    iteration += 1
    residual *= 0.5  # 模拟收敛：每次减半
    if iteration <= 3 or iteration >= 12:
        print(f"  Iter {iteration:2d}: residual = {residual:.2e}")

if iteration >= max_iter:
    print(f"  ⚠️ 达到最大迭代次数，未收敛")
else:
    print(f"  ✅ 收敛于第 {iteration} 次迭代，残差 = {residual:.2e}")

# 工程边界检查
print(f"\n载荷增量法:")
target_load = 10000  # N
applied_load = 0
load_increment = 2500  # N
step = 0

while applied_load < target_load:
    step += 1
    applied_load += load_increment
    # 防止超过目标
    if applied_load > target_load:
        applied_load = target_load
    print(f"  Step {step}: 施加 {applied_load} N / {target_load} N")


# ═══════════════════════════════════════════════════════════════
# 4. break 和 continue
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. break 和 continue")
print("=" * 60)

# break — 提前退出循环
print("寻找第一个超过限值的节点:")
stresses = [150.0, 180.0, 220.0, 240.0, 160.0]  # MPa
limit = 200.0

for i, stress in enumerate(stresses):
    if stress > limit:
        print(f"  ⚠️ 节点 {i+1} 应力 {stress} MPa 超过 {limit} MPa")
        print(f"  → 停止检查（找到第一个超限节点）")
        break
    print(f"  节点 {i+1}: {stress} MPa ✅")
else:
    # for-else: 当循环没有被 break 中断时执行
    print(f"  所有节点应力均在限值内 ✅")

# continue — 跳过当前迭代
print(f"\n只输出非零位移分量:")
displacements = [0.0, 0.001, 0.0, -0.002, 0.0, 0.003]
for i, d in enumerate(displacements):
    if abs(d) < 1e-10:  # 近似为零
        continue
    print(f"  U{i+1} = {d:.4f} mm")

# 典型错误：while True 没有退出条件
# while True:
#     pass  # ← 死循环！必须有 break


# ═══════════════════════════════════════════════════════════════
# 5. 嵌套循环
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 嵌套循环")
print("=" * 60)

# 多工况 × 多节点 — 仿真最常见模式
print("多工况 × 多节点遍历:")
cases = ["自重", "风载"]
node_ids = [1, 2, 3]

for case in cases:
    print(f"  工况: {case}")
    for node in node_ids:
        print(f"    节点 {node}: 计算中...")
    print()

# 嵌套循环的复杂度 = O(n_cases × n_nodes)
# 对于大规模数据，应考虑向量化（NumPy）替代嵌套循环

# 用 for-else 检查所有工况是否都收敛
print("检查所有工况收敛性:")
all_converged = True
for case_idx in range(1, 4):
    residual = 0.1 / (case_idx ** 2)  # 模拟
    converged = residual < 1e-2
    print(f"  工况 {case_idx}: 残差={residual:.4f} {'✅' if converged else '❌'}")
    if not converged:
        all_converged = False
        print(f"  → 工况 {case_idx} 未收敛，终止后续工况")
        break

if all_converged:
    print("所有工况收敛 ✅")


# ═══════════════════════════════════════════════════════════════
# 6. 列表推导式 — 一行替代 for-append
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 列表推导式")
print("=" * 60)

# 传统方式
traditional = []
for i in range(1, 6):
    traditional.append(i ** 2)
print(f"传统 for: {traditional}")

# 列表推导式
comprehension = [i ** 2 for i in range(1, 6)]
print(f"推导式:   {comprehension}")

# 带条件的推导式
stresses = [150, 180, 220, 240, 160, 205, 175]  # MPa
# 筛选超过 200 MPa 的节点
over_limit = [(i, s) for i, s in enumerate(stresses, 1) if s > 200]
print(f"\n超过限值的节点: {over_limit}")

# 单位换算：全部 MPa → Pa
stresses_pa = [s * 1e6 for s in stresses]
print(f"MPa → Pa: {[f'{s/1e6:.0f}MPa' for s in stresses_pa]}")


# ═══════════════════════════════════════════════════════════════
# 7. 工程循环实战
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  7. 工程循环实战")
print("=" * 60)

# 实战1：参数扫描 — 遍历不同板厚
print("板厚参数扫描:")
thicknesses = [2.0, 3.0, 4.0, 5.0]  # mm
force = 1000.0  # N
width = 50.0  # mm
length = 200.0  # mm
E = 200e9  # Pa

print(f"{'厚度(mm)':<10} {'应力(MPa)':<12} {'挠度(mm)':<12} {'质量(kg)':<10}")
print("-" * 44)
for t in thicknesses:
    t_m = t / 1000.0
    I = (width / 1000) * t_m**3 / 12
    W = I / (t_m / 2)
    M = force * (length / 1000) / 4
    sigma = M / W / 1e6
    deflection = force * (length/1000)**3 / (48 * E * I) * 1000
    mass = width/1000 * t_m * length/1000 * 7850
    print(f"{t:<10.1f} {sigma:<12.2f} {deflection:<12.3f} {mass:<10.3f}")

# 实战2：用循环生成 APDL 命令
print(f"\n生成 APDL 接触对命令:")
contact_pairs = [
    ("BOLT_HEAD", "FLANGE_TOP"),
    ("BOLT_SHANK", "HOLE_WALL"),
    ("NUT_FACE", "FLANGE_BOTTOM"),
]
for i, (target, contact) in enumerate(contact_pairs, start=1):
    print(f"  ! 接触对 {i}: {contact} → {target}")
    print(f"  MAT,{i}")
    print(f"  REAL,{i}")
    print(f"  ! ...")

# 实战3：读取结果文件并使用循环统计
print(f"\n批量统计多工况结果:")
import random
random.seed(42)

for case_id in range(1, 4):
    # 模拟从文件读取的结果
    sx = [random.gauss(100, 20) for _ in range(10)]
    sy = [random.gauss(-20, 10) for _ in range(10)]

    print(f"  工况 {case_id}:")
    print(f"    SX max={max(sx):.1f}  min={min(sx):.1f}  avg={sum(sx)/len(sx):.1f}")
    print(f"    SY max={max(sy):.1f}  min={min(sy):.1f}  avg={sum(sy)/len(sy):.1f}")


# ═══════════════════════════════════════════════════════════════
# 8. 常见错误
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  8. 常见错误")
print("=" * 60)

print("""
  ❌ 错误1：在遍历列表时修改列表
     for item in my_list:
         if item < 0:
             my_list.remove(item)  ← 导致跳过元素！
  ✅ 正确：遍历副本或使用列表推导式
     my_list = [item for item in my_list if item >= 0]

  ❌ 错误2：while True 没有退出条件
     while True:
         residual = compute()
         # ← 缺少 break 条件！
  ✅ 正确：
     while residual > tol and iter < max_iter:
         residual = compute()
         iter += 1

  ❌ 错误3：用 for 遍历大数组
     for i in range(1000000):
         result[i] = array[i] * 2  ← 极慢！
  ✅ 正确：使用 NumPy
     result = array * 2  # 向量化运算
""")


# ═══════════════════════════════════════════════════════════════
# 9. 练习
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 用 for 循环计算 1+2+3+...+100，再用 sum(range(101)) 验证。

  2. 编写一个 while 循环模拟载荷步加载：
     从 0 开始，每次加 500N，直到达到 5000N。
     如果某步应力超过 200MPa，停止加载并报告"塑形屈服"。

  3. 用列表推导式生成前 20 个自然数的平方，再筛选出能被 3 整除的。

  4. 两个列表：材料名 ['Q235', '45#', '40Cr'] 和
     屈服强度 [235, 355, 785] (MPa)。
     用 for 循环与 zip() 遍历并打印"材料 XX 屈服强度 XX MPa"。

  5. 以下代码输出什么？
     for i in range(3):
         for j in range(3):
             if i == j:
                 continue
             print(f"({i},{j})", end=" ")
""")
