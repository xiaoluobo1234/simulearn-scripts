"""
SimuLearn Scripts — 初级 #03：运算符与表达式
=============================================
知识点：basic-operators

运算符定义数据的运算规则。仿真工程中：
  - 安全系数 = 屈服强度 / 最大应力
  - 通过判断 = (等效应力 < 许用应力) and (位移 < 限值)
  - 载荷组合 = 1.2×恒载 + 1.4×活载

本节涵盖：
  1. 算术运算符 (+, -, *, /, //, %, **)
  2. 比较运算符 (==, !=, <, >, <=, >=)
  3. 逻辑运算符 (and, or, not)
  4. 赋值运算符 (=, +=, -=, *=, /=)
  5. 运算符优先级与括号
  6. 工程表达式实战

运行方式：
  python operators_expressions.py
"""

# ═══════════════════════════════════════════════════════════════
# 1. 算术运算符 — 仿真计算的基石
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 算术运算符")
print("=" * 60)

# 简支梁跨中弯矩：M = F × L / 4
F = 10000.0   # 集中力 [N]
L = 2.0       # 梁长 [m]
M = F * L / 4
print(f"弯矩 M = F×L/4 = {F}×{L}/4 = {M:.0f} N·m")

# 矩形截面惯性矩：I = b × h³ / 12
b = 0.05      # 宽 [m]
h = 0.10      # 高 [m]
I = b * h**3 / 12   # ** 是幂运算
print(f"惯性矩 I = b×h³/12 = {b}×{h}³/12 = {I:.6e} m⁴")

# 弯曲应力：σ = M × y / I，其中 y = h/2
y = h / 2
sigma = M * y / I
print(f"弯曲应力 σ = M×y/I = {sigma/1e6:.1f} MPa")

# 取模运算 % — 用于循环索引
print(f"\n取模运算: 10 % 3 = {10 % 3}     (10÷3=3 余 1)")
print(f"          15 % 5 = {15 % 5}     (整除无余数)")
# 工程应用：每 10 个载荷步输出一次日志
for step in range(1, 26):
    if step % 10 == 0:
        print(f"  [日志] 载荷步 {step} 完成")

# 整除 // — 向下取整
print(f"\n整除: 7 // 2 = {7 // 2}     (3.5 → 3)")
print(f"      -7 // 2 = {-7 // 2}    (-3.5 → -4) ← 注意向下取整")


# ═══════════════════════════════════════════════════════════════
# 2. 比较运算符 — 工程判据的基础
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. 比较运算符")
print("=" * 60)

sigma_vm = 180.5     # von Mises 应力 [MPa]
sigma_y = 235.0      # 屈服强度 [MPa]
safety_factor = 1.5
allowable = sigma_y / safety_factor

# 所有比较运算返回 bool
print(f"σ_vm = {sigma_vm} MPa, [σ] = {allowable:.1f} MPa")
print(f"σ_vm < [σ]     → {sigma_vm < allowable}    ← 强度通过")
print(f"σ_vm > sigma_y → {sigma_vm > sigma_y}    ← 未屈服")
print(f"σ_vm == 180.5  → {sigma_vm == 180.5}     ← 精确比较")
print(f"σ_vm != 0      → {sigma_vm != 0}         ← 非零应力")

# 浮点数比较陷阱 — 使用容差
measured = 0.1 + 0.2
target = 0.3
print(f"\n浮点比较陷阱:")
print(f"  0.1 + 0.2 == 0.3  → {measured == target}")
print(f"  abs((0.1+0.2)-0.3) < 1e-9 → {abs(measured - target) < 1e-9}")


# ═══════════════════════════════════════════════════════════════
# 3. 逻辑运算符 — 组合多个判据
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 逻辑运算符")
print("=" * 60)

# 典型工程判据：强度 AND 刚度 AND 稳定性都通过
strength_ok = sigma_vm < allowable
stiffness_ok = True    # 假设刚度通过
stability_ok = True    # 假设稳定性通过

design_pass = strength_ok and stiffness_ok and stability_ok
print(f"强度通过: {strength_ok}")
print(f"刚度通过: {stiffness_ok}")
print(f"稳定性通过: {stability_ok}")
print(f"设计通过 (AND): {design_pass}")

# OR — 任一条件满足
has_warning = (sigma_vm > 0.8 * sigma_y) or (not stiffness_ok)
print(f"有警告 (OR): {has_warning}")

# NOT — 取反
print(f"NOT 通过 = {not design_pass}")

# 短路求值 — 节省计算
print(f"\n短路求值示例:")
def expensive_check():
    print("    执行了昂贵检查...")
    return True

# and 短路：左边 False 时不执行右边
result = False and expensive_check()
print(f"  False and expensive_check() → {result}  (右边未执行)")

# or 短路：左边 True 时不执行右边
result = True or expensive_check()
print(f"  True or expensive_check() → {result}  (右边未执行)")


# ═══════════════════════════════════════════════════════════════
# 4. 赋值运算符 — 简洁更新变量
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 赋值运算符")
print("=" * 60)

# 基本赋值
x = 10

# 复合赋值
x += 5    # x = x + 5
print(f"x += 5  → {x}")

x -= 3    # x = x - 3
print(f"x -= 3  → {x}")

x *= 2    # x = x * 2
print(f"x *= 2  → {x}")

x /= 4    # x = x / 4
print(f"x /= 4  → {x}")

# 工程应用：累加多个工况的损伤
total_damage = 0.0
damages = [0.05, 0.12, 0.08, 0.15, 0.03]
for d in damages:
    total_damage += d  # 等价于 total_damage = total_damage + d
print(f"\n累积损伤: {total_damage}")

# 多重赋值（元组解包）
sx, sy, sz = 100.0, -20.0, -5.0
print(f"应力分量: σx={sx}, σy={sy}, σz={sz}")


# ═══════════════════════════════════════════════════════════════
# 5. 运算符优先级 — 括号是最佳文档
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 运算符优先级")
print("=" * 60)

print("""
  优先级从高到低:
  1. ()        括号（最高）
  2. **        幂运算
  3. +x, -x    正负号
  4. *, /, //, %  乘除
  5. +, -      加减
  6. <, >, ==, !=  比较
  7. not       逻辑非
  8. and       逻辑与
  9. or        逻辑或（最低）
""")

# 不加括号 — 依赖优先级
a = 2 + 3 * 4
print(f"2 + 3 * 4 = {a}    (先乘后加)")

# 加括号 — 意图明确
b = (2 + 3) * 4
print(f"(2 + 3) * 4 = {b}  (括号改变顺序)")

# 复杂的工程表达式 — 务必加括号！
# von Mises 应力
vm1 = 0.5 * ((sx - sy)**2 + (sy - sz)**2 + (sz - sx)**2
             + 6 * (10**2 + 5**2 + 2**2))
# 推荐：用括号分组，即使不是必须
vm2 = (0.5 * ((sx - sy)**2 + (sy - sz)**2 + (sz - sx)**2
              + 6 * (10**2 + 5**2 + 2**2)))
print(f"\n推荐做法：复杂表达式用括号显式分组")

# 逻辑运算的优先级陷阱
print(f"\n逻辑优先级陷阱:")
print(f"  True or False and False → {True or False and False}")
print(f"  (True or False) and False → {(True or False) and False}")
print(f"  ← and 优先级高于 or！加括号明确意图")


# ═══════════════════════════════════════════════════════════════
# 6. 工程表达式实战
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 工程表达式实战")
print("=" * 60)

# 实战1：载荷组合（建筑结构）
DL = 5000.0    # 恒载 [N]
LL = 3000.0    # 活载 [N]
WL = 2000.0    # 风载 [N]
# 基本组合：1.2DL + 1.4LL
combo_basic = 1.2 * DL + 1.4 * LL
# 含风组合：1.2DL + 1.4LL + 0.84WL
combo_wind = 1.2 * DL + 1.4 * LL + 0.84 * WL
print(f"载荷组合:")
print(f"  基本组合: {combo_basic:.0f} N")
print(f"  含风组合: {combo_wind:.0f} N")

# 实战2：安全系数校核
def check_strength(stress, yield_stress, sf=1.5):
    """检查应力是否在安全范围内。"""
    allowable = yield_stress / sf
    utilization = stress / allowable
    passed = utilization <= 1.0
    return {
        "allowable": allowable,
        "utilization": utilization,
        "passed": passed,
        "margin": (1.0 - utilization) * 100  # 安全裕度百分比
    }

result = check_strength(180.5, 235.0)
print(f"\n强度校核:")
print(f"  许用应力: {result['allowable']:.1f} MPa")
print(f"  利用率:   {result['utilization']:.1%}")
print(f"  安全裕度: {result['margin']:.1f}%")
print(f"  通过:     {result['passed']}")

# 实战3：收敛判断
residual = 1.2e-4
tolerance = 1.0e-3
iteration = 15
max_iter = 100

converged = (residual < tolerance) or (iteration >= max_iter)
print(f"\n收敛判断:")
print(f"  残差 {residual:.2e} < 容差 {tolerance:.2e} → {residual < tolerance}")
print(f"  迭代 {iteration} >= 最大 {max_iter} → {iteration >= max_iter}")
print(f"  停止迭代: {converged}")


# ═══════════════════════════════════════════════════════════════
# 7. 练习
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 计算以下表达式并用手算验证：
     - 2 ** 3 ** 2
     - (2 ** 3) ** 2
     - 10 / 3 * 3
     - 10 // 3 * 3

  2. 一个支架承受三个方向的力 Fx=500N, Fy=800N, Fz=200N。
     计算合力 F = sqrt(Fx² + Fy² + Fz²)。
     用 Python 的 ** 和 math.sqrt 两种方式实现。

  3. 以下哪个判断是正确的？为什么？
     - if stress < allowable and displacement < limit:
     - if stress < allowable or displacement < limit:
     （提示：强度校核需要同时满足强度和刚度）

  4. 写一个表达式判断某节点应力是否在 ±10% 的目标值范围内。
     目标值 = 100 MPa，当前值 = 108 MPa。
""")
