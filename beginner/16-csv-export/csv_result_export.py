"""
SimuLearn Scripts — 初级 #16：CSV 结果导出
===========================================
知识点：csv-result-export

仿真结果的 CSV 导出是数据交换的生命线：
  - ANSYS 结果 → CSV → Excel/Python 后处理
  - 参数化扫描 → CSV → 汇总对比
  - 自动化报告 → CSV → 图表

本节涵盖：
  1. csv.writer 基础写入
  2. csv.DictWriter — 列名安全写入
  3. csv.reader / DictReader 读取
  4. 仿真结果表格格式化
  5. 批量导出多个工况
  6. 常见坑与最佳实践

运行方式：
  python csv_result_export.py
"""

import csv
import io
import math
from pathlib import Path
from typing import List, Dict, Any

# ═══════════════════════════════════════════════════════════════
# 1. csv.writer 基础写入
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. csv.writer 基础写入")
print("=" * 60)

# 模拟一批节点的 von Mises 应力结果
nodal_stress = [
    (1,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0,   0.0),
    (2,   120.5, -30.2,  -5.1,  45.0,  12.3,   8.9, 132.7),
    (3,   115.8, -28.7,  -4.8,  42.3,  11.5,   8.2, 127.4),
    (4,   110.2, -25.0,  -4.2,  38.7,  10.1,   7.5, 121.0),
    (5,   105.0, -22.0,  -3.5,  35.0,   9.0,   6.8, 115.3),
]

output_dir = Path("./output")
output_dir.mkdir(exist_ok=True)

# 方式 A：直接用 writerow 逐行写
filepath_a = output_dir / "stress_basic.csv"
with open(filepath_a, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Node", "SX", "SY", "SZ", "SXY", "SYZ", "SXZ", "von_Mises"])
    for row in nodal_stress:
        writer.writerow(row)

print(f"已写入: {filepath_a}")

# 方式 B：writerows 批量写入（性能更好）
filepath_b = output_dir / "stress_batch.csv"
with open(filepath_b, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Node", "SX", "SY", "SZ", "SXY", "SYZ", "SXZ", "von_Mises"])
    writer.writerows(nodal_stress)

print(f"已写入: {filepath_b}")

# ── 坑：newline="" 必须加 ──
print("\n⚠ 提醒: 在 Windows 上 open() 必须带 newline=''，")
print("  否则 CSV 行间会多出空行（\\r\\n 变 \\r\\r\\n）。")


# ═══════════════════════════════════════════════════════════════
# 2. csv.DictWriter — 列名安全写入
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. csv.DictWriter — 按列名写入")
print("=" * 60)

# 用字典表示数据更安全：不依赖列顺序，列名自文档
results: List[Dict[str, Any]] = [
    {"load_case": "LC1-Dead",   "max_stress_MPa": 235.0, "max_disp_mm": 1.25, "mass_kg": 1450.0},
    {"load_case": "LC2-Live",   "max_stress_MPa": 198.0, "max_disp_mm": 2.10, "mass_kg": 1450.0},
    {"load_case": "LC3-Wind",   "max_stress_MPa": 312.0, "max_disp_mm": 8.75, "mass_kg": 1450.0},
    {"load_case": "LC4-Seismic","max_stress_MPa": 445.0, "max_disp_mm": 25.30, "mass_kg": 1450.0},
    {"load_case": "LC5-Combo",  "max_stress_MPa": 398.0, "max_disp_mm": 18.20, "mass_kg": 1450.0},
]

fieldnames = ["load_case", "max_stress_MPa", "max_disp_mm", "mass_kg"]
filepath_c = output_dir / "load_cases.csv"

with open(filepath_c, "w", newline="", encoding="utf-8") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)

    # writeheader() 自动写表头
    writer.writeheader()
    writer.writerows(results)

print(f"已写入: {filepath_c}")

# 验证 — 读回来检查
with open(filepath_c, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    rows = list(reader)
    print(f"  验证: 读回 {len(rows)} 行, 列名: {reader.fieldnames}")

# ── DictWriter 的好处 ──
print("\n💡 DictWriter 优势:")
print("  1. 列顺序由 fieldnames 控制，不依赖字典插入顺序")
print("  2. 多余键自动忽略（extrasaction='ignore'）")
print("  3. 缺键报错（默认 extrasaction='raise'），防 typo")


# ═══════════════════════════════════════════════════════════════
# 3. csv.reader / DictReader 读取
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. csv.reader / DictReader 读取")
print("=" * 60)

# 模拟从 ANSYS 导出的 CSV（可能有空行、注释行）
ansys_csv_content = """\
# ANSYS PRNSOL Export — Nodal Stress
# Generated: 2025-06-15 14:30:00
Node,SX (MPa),SY (MPa),SZ (MPa),von Mises (MPa)
1,100.5,-20.3,-5.1,115.2
2,98.7,-18.9,-4.8,113.0
3,102.1,-21.0,-5.3,117.5
4,95.3,-15.6,-3.9,108.8
5,105.8,-22.4,-5.8,121.6
"""

# 方式 A：csv.reader — 按索引访问列
print("\n--- 用 csv.reader 读取 ---")
with io.StringIO(ansys_csv_content) as f:
    reader = csv.reader(f)
    for row in reader:
        # 跳过空行和注释
        if not row or row[0].startswith("#"):
            continue
        print(f"  {row}")

# 方式 B：csv.DictReader — 按列名访问（推荐）
print("\n--- 用 csv.DictReader 读取 ---")
with io.StringIO(ansys_csv_content) as f:
    reader = csv.DictReader(f)
    for row in reader:
        # DictReader 自动跳过注释行
        # 注意：DictReader 会把第一非注释行当表头
        node = row.get("Node")
        von_mises = row.get("von Mises (MPa)", "N/A")
        print(f"  Node {node}: von Mises = {von_mises} MPa")

# ── 实用技巧：跳过表头前的注释 ──
print("\n--- 跳过表头前注释行 ---")
with io.StringIO(ansys_csv_content) as f:
    # 跳过注释行直到表头
    lines = f.readlines()
    data_start = 0
    for i, line in enumerate(lines):
        if not line.startswith("#") and line.strip():
            data_start = i
            break

    reader = csv.DictReader(lines[data_start:])
    for row in reader:
        print(f"  Node {row['Node']}: SX = {row['SX (MPa)']} MPa")


# ═══════════════════════════════════════════════════════════════
# 4. 仿真结果表格 — 格式化输出
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 仿真结果表格格式化")
print("=" * 60)

def export_parameter_sweep(
    filename: Path,
    thicknesses: List[float],
    loads: List[float],
) -> None:
    """参数化扫描结果导出。

    扫描厚度 × 载荷，计算简支板中心应力和挠度。
    导出带工程单位、格式化的 CSV。

    Args:
        filename: 输出 CSV 路径
        thicknesses: 板厚列表 [mm]
        loads: 均布载荷列表 [MPa]
    """
    # 板参数（固定）
    a = 500.0  # 长边 [mm]
    b = 300.0  # 短边 [mm]
    E = 210000.0  # 弹性模量 [MPa]
    nu = 0.3

    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # 元数据头
        writer.writerow(["# Parameter Sweep Results"])
        writer.writerow(["# Plate:", f"{a}x{b} mm", "E:", f"{E} MPa", "nu:", nu])
        writer.writerow([])  # 空行分隔

        # 数据表头
        writer.writerow([
            "Thickness (mm)", "Load (MPa)",
            "Max Stress (MPa)", "Max Deflection (mm)",
            "Utilization", "Status"
        ])

        allowable = 235.0  # 许用应力 [MPa] (Q235)

        for t in thicknesses:
            for q in loads:
                # 四边简支板中心应力 (近似公式)
                # σ_max ≈ β · q · b² / t²
                beta = 0.2874  # a/b ≈ 1.67 时的系数
                stress = beta * q * (b ** 2) / (t ** 2)

                # 中心挠度
                # w_max ≈ α · q · b⁴ / (E · t³)
                alpha = 0.0444
                D = E * t**3 / (12 * (1 - nu**2))
                deflection = alpha * q * (b ** 4) / D

                utilization = stress / allowable
                status = "PASS" if utilization < 1.0 else "FAIL"

                writer.writerow([
                    f"{t:.1f}",
                    f"{q:.4f}",
                    f"{stress:.2f}",
                    f"{deflection:.3f}",
                    f"{utilization:.3f}",
                    status
                ])

    print(f"参数扫描结果已导出: {filename}")
    print(f"  扫描 {len(thicknesses)} 厚度 × {len(loads)} 载荷 = {len(thicknesses)*len(loads)} 工况")


# 运行参数扫描
thicknesses = [5.0, 8.0, 10.0, 12.0]  # mm
loads = [0.01, 0.05, 0.10, 0.20]  # MPa

filepath_d = output_dir / "param_sweep.csv"
export_parameter_sweep(filepath_d, thicknesses, loads)

# 展示导出内容摘要
with open(filepath_d, "r", encoding="utf-8") as f:
    lines = f.readlines()
    print(f"\n  文件预览 ({len(lines)} 行):")
    for line in lines[:10]:
        print(f"    {line.rstrip()}")
    if len(lines) > 10:
        print(f"    ... ({len(lines) - 10} more lines)")


# ═══════════════════════════════════════════════════════════════
# 5. 批量导出多个工况
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 批量导出多个工况 — 实战模式")
print("=" * 60)

def batch_export_results(
    base_dir: Path,
    load_cases: List[Dict[str, Any]],
) -> List[Path]:
    """为每个工况生成独立 CSV 文件，并生成汇总表。

    这是仿真后处理的标准工作流：
      每个工况一个详细结果文件 + 一个汇总对比表。

    Args:
        base_dir: 输出目录
        load_cases: 工况列表，每个包含 name, fx, fy, fz, mx, my, mz

    Returns:
        生成的文件路径列表
    """
    base_dir.mkdir(parents=True, exist_ok=True)
    generated = []

    summary_rows = []

    for case in load_cases:
        case_name = case["name"]

        # 模拟"计算结果"——实际中这些来自求解器
        fx, fy, fz = case["fx"], case["fy"], case["fz"]
        mx, my, mz = case["mx"], case["my"], case["mz"]

        # 合成位移和应力（简化计算）
        total_force = math.sqrt(fx**2 + fy**2 + fz**2)
        total_moment = math.sqrt(mx**2 + my**2 + mz**2)
        max_disp = 0.001 * total_force + 0.0001 * total_moment  # 简化的刚度关系
        max_stress = total_force / 100.0 + total_moment / 500.0

        # 1) 详细结果文件
        detail_file = base_dir / f"{case_name}_detail.csv"
        with open(detail_file, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["# Load Case:", case_name])
            writer.writerow([])
            writer.writerow(["Component", "Force (N)", "Moment (N·mm)"])
            writer.writerow(["FX", f"{fx:.2f}", f"{mx:.2f}"])
            writer.writerow(["FY", f"{fy:.2f}", f"{my:.2f}"])
            writer.writerow(["FZ", f"{fz:.2f}", f"{mz:.2f}"])
            writer.writerow([])
            writer.writerow(["Result", "Value", "Unit"])
            writer.writerow(["Max Displacement", f"{max_disp:.4f}", "mm"])
            writer.writerow(["Max von Mises Stress", f"{max_stress:.2f}", "MPa"])

        generated.append(detail_file)

        # 2) 收集汇总行
        summary_rows.append({
            "case": case_name,
            "fx": fx, "fy": fy, "fz": fz,
            "max_disp_mm": round(max_disp, 4),
            "max_stress_MPa": round(max_stress, 2),
        })

    # 3) 汇总表
    summary_file = base_dir / "_summary.csv"
    with open(summary_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "case", "fx", "fy", "fz",
            "max_disp_mm", "max_stress_MPa"
        ])
        writer.writeheader()
        writer.writerows(summary_rows)

    generated.append(summary_file)
    return generated


# 构造 8 个工况
load_cases = []
for i in range(1, 9):
    load_cases.append({
        "name": f"LC{i:02d}",
        "fx": 1000 * i,
        "fy": 500 * math.sin(i * math.pi / 4),
        "fz": -2000 - 200 * i,
        "mx": 10000 * (i % 3),
        "my": 5000 * ((i + 1) % 3),
        "mz": 2000 * i,
    })

batch_dir = output_dir / "batch_results"
files = batch_export_results(batch_dir, load_cases)

print(f"批量导出完成: {len(files)} 个文件")
for f in files:
    print(f"  {f.name}")


# ═══════════════════════════════════════════════════════════════
# 6. 常见坑与最佳实践
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 常见坑与最佳实践")
print("=" * 60)

pitfalls = [
    ("坑1: Windows 换行符",
     "open() 不加 newline='' → 行间多余空行",
     "始终 open(..., newline='', encoding='utf-8')"),

    ("坑2: 编码问题",
     "中文/特殊字符 → UnicodeEncodeError",
     "明确指定 encoding='utf-8-sig' (BOM) 让 Excel 正确识别"),

    ("坑3: 数字精度丢失",
     "float → str → CSV 再读回 float 精度变化",
     "导出时用 f-string 控制小数位数: f'{val:.6f}'"),

    ("坑4: 大文件内存",
     "一次性读入所有行 → 内存爆炸",
     "用 for row in reader 逐行处理，或 csv.field_size_limit()"),

    ("坑5: 混合类型列",
     "同一列有数字和 'N/A' → 后处理困难",
     "统一用字符串，后处理时显式转换 + 异常处理"),

    ("坑6: ANSYS 输出中的科学计数法",
     "0.1234E-03 不是标准浮点格式",
     "用 float() 直接转换即可，Python 支持 'E' 和 'e'"),
]

for title, problem, solution in pitfalls:
    print(f"\n  ⚠  {title}")
    print(f"     问题: {problem}")
    print(f"     解决: {solution}")

# ── 演示：UTF-8-BOM 让 Excel 正确显示中文 ──
filepath_e = output_dir / "chinese_header.csv"
with open(filepath_e, "w", newline="", encoding="utf-8-sig") as f:
    writer = csv.writer(f)
    writer.writerow(["节点号", "X向应力(MPa)", "Y向应力(MPa)", "等效应力(MPa)"])
    writer.writerow([1, 120.5, -30.2, 132.7])
    writer.writerow([2, 115.8, -28.7, 127.4])

print(f"\n✅ 中文表头 CSV (UTF-8-BOM): {filepath_e}")
print("  用 Excel 打开可正确显示中文列名。")


# ═══════════════════════════════════════════════════════════════
# 7. 练习
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  7. 练习")
print("=" * 60)

print("""
  [练习 1] 修改 export_parameter_sweep 函数，增加输出：
           - 安全系数 (allowable / stress)
           - 刚度利用率 (deflection / allowable_deflection)

  [练习 2] 写一个函数 read_and_filter(csv_path, column, threshold)：
           - 读取 CSV
           - 筛选 column 值 > threshold 的行
           - 返回筛选后的列表

  [练习 3] 从 ANSYS PRNSOL 文本输出生成 CSV：
           - 用正则提取节点号和六个应力分量
           - 计算 von Mises 应力
           - 导出为 CSV

  [练习 4] 处理大文件 (> 100MB)：
           - 用 csv.reader 逐行读取
           - 每 10000 行写入一个分片文件
           - 测试 field_size_limit 设置
""")

print("✅ 知识点 16 完成: CSV 结果导出")
