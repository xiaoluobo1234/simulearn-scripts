"""
SimuLearn Scripts — 初级 #10：文件读写
=======================================
知识点：file-io

仿真数据交换的最常见格式：
  - .csv  — 表格结果
  - .json — 结构化配置
  - .txt  — 日志和关键值

本节涵盖：
  1. 文本文件读写
  2. CSV 文件操作
  3. JSON 配置管理
  4. with 语句与资源管理
  5. 编码处理
  6. 工程文件处理实战

运行方式：
  python file_io.py
"""

import csv
import json
import os
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# 1. 文本文件读写基础
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 文本文件读写基础")
print("=" * 60)

# 写入文本文件
output_path = Path("./output")
output_path.mkdir(exist_ok=True)

filepath = output_path / "demo_log.txt"
with open(filepath, "w", encoding="utf-8") as f:
    f.write("SimuLearn 分析日志\n")
    f.write("=" * 40 + "\n")
    f.write(f"运行时间: 2026-06-29\n")
    for i in range(1, 4):
        f.write(f"载荷步 {i}: 收敛 ✅\n")

print(f"已写入: {filepath.absolute()}")

# 读取文本文件
with open(filepath, "r", encoding="utf-8") as f:
    content = f.read()

print(f"\n文件内容:")
print(content)

# 逐行读取（适合大文件）
print(f"逐行读取:")
with open(filepath, "r", encoding="utf-8") as f:
    for line_no, line in enumerate(f, start=1):
        print(f"  L{line_no}: {line.rstrip()}")

# 读取所有行到列表
with open(filepath, "r", encoding="utf-8") as f:
    lines = f.readlines()
print(f"\n共 {len(lines)} 行")


# ═══════════════════════════════════════════════════════════════
# 2. 文件打开模式
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. 文件打开模式")
print("=" * 60)

print("""
  模式   含义              适用场景
  ─────────────────────────────────────────
  'r'   只读 (默认)      读取结果文件
  'w'   写入 (覆盖)      输出新报告
  'a'   追加 (不覆盖)    记录日志
  'r+'  读写             更新配置文件
  'b'   二进制模式       读取 ANSYS 二进制 (.rst)
""")

# 追加模式 — 日志持续写入
log_path = output_path / "demo_log.txt"
with open(log_path, "a", encoding="utf-8") as f:
    f.write(f"\n[追加] 后处理完成\n")

print(f"追加后的文件内容:")
print(log_path.read_text(encoding="utf-8"))


# ═══════════════════════════════════════════════════════════════
# 3. CSV 文件操作
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. CSV 文件操作")
print("=" * 60)

# 写入 CSV — 仿真结果导出
csv_path = output_path / "demo_results.csv"

with open(csv_path, "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    # 写表头
    writer.writerow(["Node", "SX_MPa", "SY_MPa", "SZ_MPa",
                      "SXY_MPa", "SYZ_MPa", "SXZ_MPa", "VM_MPa"])
    # 写数据行
    writer.writerow([1, 100.5, -20.3, -5.1, 10.0, 5.2, 2.8, 112.3])
    writer.writerow([2, 98.7, -18.9, -4.8, 9.5, 4.9, 2.5, 108.5])
    writer.writerow([3, 102.1, -21.0, -5.3, 10.8, 5.5, 3.0, 115.8])

print(f"已写入 CSV: {csv_path.absolute()}")

# 读取 CSV — 两种方式

# 方式A：csv.reader — 返回列表
print(f"\n读取 CSV (list):")
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)  # 跳过表头
    print(f"  表头: {header}")
    for row in reader:
        node = int(row[0])
        vm = float(row[-1])
        print(f"  节点 {node}: VM = {vm:.1f} MPa")

# 方式B：csv.DictReader — 返回字典（推荐！）
print(f"\n读取 CSV (dict):")
with open(csv_path, "r", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        print(f"  节点 {row['Node']}: "
              f"SX={row['SX_MPa']} MPa, "
              f"VM={row['VM_MPa']} MPa")


# ═══════════════════════════════════════════════════════════════
# 4. JSON 配置管理
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. JSON 配置管理")
print("=" * 60)

# 配置数据 — 用 JSON 替代硬编码
config = {
    "project": "支架强度校核",
    "material": {
        "name": "Q345",
        "E_GPa": 206,
        "yield_MPa": 345,
    },
    "geometry": {
        "beam_length_m": 2.0,
        "section_width_mm": 50,
        "section_height_mm": 100,
    },
    "loads": [
        {"name": "自重", "factor": 1.2},
        {"name": "活载", "factor": 1.4},
        {"name": "风载", "factor": 0.84},
    ],
    "mesh_size_mm": 5.0,
    "safety_factor": 1.5,
}

# 保存配置
config_path = output_path / "demo_config.json"
with open(config_path, "w", encoding="utf-8") as f:
    json.dump(config, f, indent=2, ensure_ascii=False)

print(f"已保存配置: {config_path.absolute()}")

# 读取配置
with open(config_path, "r", encoding="utf-8") as f:
    loaded_config = json.load(f)

print(f"\n读取配置:")
print(f"  项目: {loaded_config['project']}")
print(f"  材料: {loaded_config['material']['name']}")
print(f"  载荷组合数: {len(loaded_config['loads'])}")
print(f"  网格尺寸: {loaded_config['mesh_size_mm']} mm")

# 访问嵌套数据
for load in loaded_config["loads"]:
    print(f"  {load['name']}: 系数={load['factor']}")


# ═══════════════════════════════════════════════════════════════
# 5. with 语句与资源管理
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. with 语句 — 自动关闭")
print("=" * 60)

print("""
  ✅ with open(...) as f:
         data = f.read()
     # f 自动关闭，即使发生异常

  ❌ f = open(...)
     data = f.read()
     # 如果中间出错，f 不会关闭！
     f.close()  # 可能执行不到

  对比：
  - with 语句 = try/finally 的语法糖
  - 确保资源 (文件、网络连接等) 正确释放
  - 是 Python 的最佳实践
""")


# ═══════════════════════════════════════════════════════════════
# 6. 编码处理
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  6. 编码处理")
print("=" * 60)

# 始终指定 encoding="utf-8"
# 不指定会使用系统默认编码，在不同机器上行为不同

# 正确
with open(output_path / "demo_utf8.txt", "w", encoding="utf-8") as f:
    f.write("弹性模量 E = 200 GPa  应力 σ = 235 MPa")

# 如果遇到编码错误
try:
    with open("nonexistent.txt", "r", encoding="utf-8") as f:
        pass
except FileNotFoundError:
    print("文件不存在 — 这是预期的错误")

# 处理可能的编码问题
# errors="replace" — 替换无法解码的字符
# errors="ignore"  — 跳过无法解码的字符
print("  编码错误处理策略: 'strict'(默认), 'replace', 'ignore'")


# ═══════════════════════════════════════════════════════════════
# 7. 工程文件处理实战
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  7. 工程文件处理实战")
print("=" * 60)

# 实战1：批量读取多个工况的 CSV 结果
print("实战1 — 批量结果汇总:")

# 先生成模拟数据
case_names = ["Dead_Load", "Live_Load", "Wind_Load"]
for case in case_names:
    case_path = output_path / f"case_{case}.csv"
    with open(case_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["Node", "Displacement_mm"])
        for node in range(1, 4):
            writer.writerow([node, round(0.1 * node + hash(case) % 10 * 0.05, 3)])

# 汇总所有工况
summary = {}
for case in case_names:
    case_path = output_path / f"case_{case}.csv"
    with open(case_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        summary[case] = {}
        for row in reader:
            summary[case][int(row["Node"])] = float(row["Displacement_mm"])

print(f"工况汇总:")
for case, data in summary.items():
    max_disp = max(data.values())
    print(f"  {case}: 最大位移 = {max_disp:.3f} mm @ 节点{max(data, key=data.get)}")

# 实战2：读取 APDL 输出并提取关键数据
print(f"\n实战2 — APDL 输出提取:")

# 模拟 ANSYS 输出
apdl_text = """***** POST1 NODAL SOLUTION *****
  NODE     UX          UY          UZ          USUM
     1  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00
     2  1.2345E-04 -2.3456E-05  1.0000E-06  1.2572E-04
     3  2.4689E-04 -4.6912E-05  2.0000E-06  2.5141E-04

 MAXIMUM ABSOLUTE VALUES
  NODE       3          1          3          3
  VALUE  2.4689E-04 -4.6912E-05 2.0000E-06  2.5141E-04
"""

# 写临时文件
apdl_path = output_path / "demo_apdl_output.txt"
apdl_path.write_text(apdl_text, encoding="utf-8")

# 读取并解析
displacements = []
with open(apdl_path, "r", encoding="utf-8") as f:
    in_data = False
    for line in f:
        stripped = line.strip()
        if "NODE" in stripped and "UX" in stripped:
            in_data = True
            continue
        if in_data and stripped:
            if "MAXIMUM" in stripped:
                break
            parts = stripped.split()
            if len(parts) >= 5:
                try:
                    displacements.append({
                        "node": int(parts[0]),
                        "ux": float(parts[1]),
                        "uy": float(parts[2]),
                        "uz": float(parts[3]),
                        "usum": float(parts[4]),
                    })
                except ValueError:
                    continue

print(f"解析到位移数据: {len(displacements)} 个节点")
for d in displacements:
    print(f"  节点 {d['node']}: UX={d['ux']:.4e} mm, "
          f"USUM={d['usum']:.4e} mm")


# ═══════════════════════════════════════════════════════════════
# 8. pathlib 便捷方法
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  8. pathlib 便捷方法")
print("=" * 60)

# Python 3.5+ pathlib 提供直接读写
demo_path = output_path / "demo_pathlib.txt"
demo_path.write_text("第一行\n第二行\n", encoding="utf-8")
content = demo_path.read_text(encoding="utf-8")
print(f"pathlib 直接读写: {repr(content[:20])}")

# 便捷的文件存在性检查
print(f"\n文件检查:")
print(f"  demo_path.exists() = {demo_path.exists()}")
print(f"  demo_path.is_file() = {demo_path.is_file()}")
print(f"  output_path.is_dir() = {output_path.is_dir()}")


# ═══════════════════════════════════════════════════════════════
# 9. 练习
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 编写一个函数 save_results_csv(nodes, stresses, filename):
     nodes = [(1, 100.5), (2, 98.7), (3, 102.1)]
     保存为 CSV 文件，包含表头。

  2. 用 json 保存和读取仿真配置，包含以下字段：
     project_name, author, material_dict, mesh_size, load_cases (list)

  3. 读取一个大型 ANSYS 输出文件，统计其中包含 "WARNING" 和
     "ERROR" 的行数。使用逐行读取避免内存问题。

  4. 以下代码有什么隐患？
     f = open("results.csv")
     data = csv.reader(f)
     do_something_that_might_crash(data)
     f.close()
""")

# 清理演示文件（可选）
import shutil
# shutil.rmtree(output_path)  # 取消注释以清理
