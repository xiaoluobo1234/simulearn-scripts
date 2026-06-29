"""
SimuLearn Scripts — 初级 #05：条件判断
=======================================
知识点：control-flow-if

条件判断让脚本根据计算结果自动分支：
  - 通过 / 不通过
  - 弹性 / 塑性
  - 收敛 / 发散

本节涵盖：
  1. if / elif / else 语法
  2. 嵌套条件
  3. 条件表达式（三元运算符）
  4. 多条件组合
  5. 仿真判据实战

运行方式：
  python conditionals.py
"""

# ═══════════════════════════════════════════════════════════════
# 1. 基本 if / elif / else
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 基本 if / elif / else")
print("=" * 60)

# 仿真中最常见的判断：应力是否超标
max_stress = 180.5   # MPa
allowable = 156.7    # MPa

if max_stress < allowable:
    status = "✅ 通过"
elif max_stress == allowable:
    status = "⚠️ 临界"
else:
    status = "❌ 不通过"

print(f"应力 {max_stress} MPa vs 许用 {allowable} MPa → {status}")

# 注意缩进！Python 用缩进定义代码块
# 以下两种写法等价，但第一种是 Python 惯例（4空格）
if True:
    print("  这是正确的缩进（4空格）")

# if True:
# print("  这是错误的缩进！会报 IndentationError")


# ═══════════════════════════════════════════════════════════════
# 2. 多分支 — 仿真状态分类
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. 多分支 — 仿真状态分类")
print("=" * 60)

# 根据收敛残差判断求解状态
def classify_convergence(residual: float) -> str:
    """根据残差对求解状态分类。"""
    if residual < 1e-8:
        return "🟢 完全收敛（残差 < 1e-8）"
    elif residual < 1e-6:
        return "🟡 良好收敛（残差 < 1e-6）"
    elif residual < 1e-4:
        return "🟠 弱收敛（残差 < 1e-4）"
    elif residual < 1e-2:
        return "🔴 未收敛（残差 < 1e-2）"
    else:
        return "💥 发散（残差 ≥ 1e-2）"

residuals = [1e-9, 5e-7, 3e-5, 8e-3, 0.5]
for r in residuals:
    print(f"  残差 {r:.1e}: {classify_convergence(r)}")

# ⚠️ 注意 elif 的顺序！从最严格到最宽松
# 如果把 < 1e-2 放在前面，会吞掉所有更严格的判断


# ═══════════════════════════════════════════════════════════════
# 3. 嵌套条件
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 嵌套条件")
print("=" * 60)

# 工程判据往往有多层：先看应力级别，再看位置
def evaluate_node(stress_MPa: float, is_critical_zone: bool) -> str:
    """评估节点安全性。

    关键区域的标准更严格。
    """
    if is_critical_zone:
        # 关键区域：更严格的限值
        if stress_MPa > 150:
            return "❌ 关键区域超限"
        elif stress_MPa > 120:
            return "⚠️ 关键区域接近限值"
        else:
            return "✅ 关键区域安全"
    else:
        # 非关键区域：标准限值
        if stress_MPa > 235:
            return "❌ 超限"
        elif stress_MPa > 200:
            return "⚠️ 接近限值"
        else:
            return "✅ 安全"

test_cases = [
    (160, True),
    (130, True),
    (100, True),
    (200, False),
    (240, False),
]
for stress, critical in test_cases:
    zone = "关键区" if critical else "普通区"
    result = evaluate_node(stress, critical)
    print(f"  应力 {stress} MPa @ {zone}: {result}")

# ⚠️ 嵌套不要太深 — 超过3层考虑提取函数


# ═══════════════════════════════════════════════════════════════
# 4. 条件表达式（三元运算符）
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 条件表达式（三元运算符）")
print("=" * 60)

# 语法: value_if_true if condition else value_if_false
stress = 180.5
status = "通过" if stress < 235 else "不通过"
print(f"三元运算: stress={stress} → {status}")

# 等效的 if-else 写法（更冗长）
if stress < 235:
    status2 = "通过"
else:
    status2 = "不通过"
print(f"if-else:   stress={stress} → {status2}")

# 适合简单赋值，不适合复杂逻辑
# ❌ 不要这样写（可读性差）
# result = "A" if x > 10 else "B" if x > 5 else "C" if x > 0 else "D"

# ✅ 这样更好
def classify_value(x):
    if x > 10:
        return "A"
    elif x > 5:
        return "B"
    elif x > 0:
        return "C"
    else:
        return "D"


# ═══════════════════════════════════════════════════════════════
# 5. 多条件组合
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 多条件组合")
print("=" * 60)

# 强度 AND 刚度 AND 稳定性 全部满足
strength_ok = True
stiffness_ok = True
stability_ok = False

if strength_ok and stiffness_ok and stability_ok:
    print("✅ 全部通过")
elif not strength_ok:
    print("❌ 强度不足")
elif not stiffness_ok:
    print("❌ 刚度不足")
elif not stability_ok:
    print("❌ 稳定性不足")

# 使用 all() / any() 简化多条件
checks = [strength_ok, stiffness_ok, stability_ok]
check_names = ["强度", "刚度", "稳定性"]

if all(checks):
    print("✅ 全部检查通过")
else:
    failed = [name for name, ok in zip(check_names, checks) if not ok]
    print(f"❌ 失败项: {', '.join(failed)}")

# any() — 任一条件满足
has_critical = any([stress > 200 for stress in [150, 180, 220, 160]])
print(f"\n存在应力 > 200 MPa: {has_critical}")


# ═══════════════════════════════════════════════════════════════
# 6. 仿真判据实战
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 仿真判据实战")
print("=" * 60)

# 实战1：完整的结构校核函数
def structural_check(
    von_mises_MPa: float,
    displacement_mm: float,
    buckling_factor: float,
    material_yield_MPa: float = 235.0,
    safety_factor: float = 1.5,
    disp_limit_mm: float = 1.0,
    buckling_limit: float = 3.0,
) -> dict:
    """完整的结构校核：强度 + 刚度 + 稳定性。

    Returns:
        包含各项检查结果的字典
    """
    allowable = material_yield_MPa / safety_factor

    # 强度
    if von_mises_MPa < 0.8 * allowable:
        strength_status = "pass"
        strength_msg = f"强度充裕 (利用率 {von_mises_MPa/allowable:.1%})"
    elif von_mises_MPa < allowable:
        strength_status = "warn"
        strength_msg = f"强度接近限值 (利用率 {von_mises_MPa/allowable:.1%})"
    else:
        strength_status = "fail"
        strength_msg = f"强度不足 (利用率 {von_mises_MPa/allowable:.1%})"

    # 刚度
    if displacement_mm < 0.5 * disp_limit_mm:
        stiffness_status = "pass"
        stiffness_msg = f"刚度充裕 ({displacement_mm:.3f} < {0.5*disp_limit_mm:.3f} mm)"
    elif displacement_mm < disp_limit_mm:
        stiffness_status = "warn"
        stiffness_msg = f"刚度接近限值 ({displacement_mm:.3f} mm)"
    else:
        stiffness_status = "fail"
        stiffness_msg = f"刚度不足 ({displacement_mm:.3f} > {disp_limit_mm} mm)"

    # 稳定性
    if buckling_factor > buckling_limit:
        stability_status = "pass"
        stability_msg = f"稳定性充裕 (屈曲因子 {buckling_factor:.1f})"
    elif buckling_factor > 1.0:
        stability_status = "warn"
        stability_msg = f"稳定性偏低 (屈曲因子 {buckling_factor:.1f})"
    else:
        stability_status = "fail"
        stability_msg = f"失稳 (屈曲因子 {buckling_factor:.1f} < 1.0)"

    # 综合判断
    all_status = [strength_status, stiffness_status, stability_status]
    if "fail" in all_status:
        overall = "❌ 不通过"
    elif "warn" in all_status:
        overall = "⚠️ 有条件通过"
    else:
        overall = "✅ 通过"

    return {
        "overall": overall,
        "strength": strength_msg,
        "stiffness": stiffness_msg,
        "stability": stability_msg,
    }

# 测试
result = structural_check(180.5, 0.35, 4.2)
print(f"结论: {result['overall']}")
print(f"  {result['strength']}")
print(f"  {result['stiffness']}")
print(f"  {result['stability']}")

# 边界情况测试
print(f"\n边界情况测试:")
result2 = structural_check(230, 0.95, 1.5)
print(f"结论: {result2['overall']}")
print(f"  {result2['strength']}")
print(f"  {result2['stiffness']}")
print(f"  {result2['stability']}")

# 实战2：ANSYS 接触状态判断
print(f"\n接触状态判断:")
contact_status = 2  # 2=Sticking, 1=Sliding, 0=Near-field, -1=Far-field
if contact_status == 2:
    state = "粘合 (Sticking)"
elif contact_status == 1:
    state = "滑动 (Sliding)"
elif contact_status == 0:
    state = "近场 (Near-field)"
else:
    state = "远场 (Far-field)"
print(f"  接触状态码 {contact_status} → {state}")

# 使用字典映射替代长 if-elif（更优雅）
status_map = {
    2: "粘合 (Sticking)",
    1: "滑动 (Sliding)",
    0: "近场 (Near-field)",
    -1: "远场 (Far-field)",
}
state2 = status_map.get(contact_status, "未知状态")
print(f"  字典映射方式: {state2}")


# ═══════════════════════════════════════════════════════════════
# 7. 常见错误
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  7. 常见错误")
print("=" * 60)

print("""
  ❌ 错误1: if-if-if 替代 if-elif-else
     if stress > 200: print("高应力")
     if stress > 100: print("中应力")  ← 也会触发！
     if stress > 0:   print("低应力")   ← 也会触发！
     三个条件不是互斥的！

  ✅ 正确: 互斥条件用 if-elif-else
     if stress > 200: print("高应力")
     elif stress > 100: print("中应力")
     elif stress > 0: print("低应力")

  ❌ 错误2: 浮点数直接比较
     if stress == 235.0:  ← 可能永远不成立
  ✅ 正确: 使用容差
     if abs(stress - 235.0) < 1e-9:

  ❌ 错误3: 忘记冒号
     if stress > 100   ← 缺少冒号
  ✅ 正确:
     if stress > 100:

  ❌ 错误4: 赋值 (=) 与比较 (==) 混淆
     if stress = 100:  ← 这是赋值，不是比较！
  ✅ 正确:
     if stress == 100:
""")


# ═══════════════════════════════════════════════════════════════
# 8. 练习
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 编写函数 evaluate_temperature(temp_C):
     - temp < 0:    "低温脆性风险"
     - 0 ≤ temp < 100: "正常工况"
     - 100 ≤ temp < 300: "高温蠕变关注"
     - temp ≥ 300:  "超出材料使用温度"

  2. 一个螺栓连接有3个失效模式：拉伸、剪切、挤压。
     每种失效模式有各自的利用率 U_t, U_s, U_b。
     写代码判断：如果任一利用率 > 1.0 则"不通过"，
     如果全部 < 0.8 则"充裕"，否则"关注"。

  3. 以下代码有什么问题？
     if x > 0:
         print("正数")
     if x > 10:
         print("大于10")
     if x > 100:
         print("大于100")

  4. 用字典映射重构以下代码：
     if error_code == 1: msg = "文件不存在"
     elif error_code == 2: msg = "权限不足"
     elif error_code == 3: msg = "内存不足"
     else: msg = "未知错误"
""")
