"""
SimuLearn Scripts — 初级 #15：读取 APDL 输出文件
=================================================
知识点：apdl-output-parse

APDL 文本输出有固定格式：表头行 + 数据行。
用正则匹配或逐行解析提取结构。

本节涵盖：
  1. APDL 输出格式识别
  2. 逐行解析方法
  3. 正则表达式提取
  4. 处理分页符和特殊格式
  5. 实战解析

运行方式：
  python parse_apdl_output.py
"""

import re
from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# 1. APDL 输出格式识别
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. APDL 输出格式识别")
print("=" * 60)

# 模拟一段真实的 ANSYS PRNSOL 输出
sample_output = r"""
***** POST1 NODAL STRESS LISTING *****
 PowerGraphics Is Currently Enabled

 THE FOLLOWING X,Y,Z VALUES ARE IN GLOBAL COORDINATES

   NODE    SX       SY       SZ      SXY      SYZ      SXZ
     1  100.50  -20.300   -5.100  10.000    5.200    2.800
     2  98.700  -18.900   -4.800   9.500    4.900    2.500
     3  102.10  -21.000   -5.300  10.800    5.500    3.000
     4  95.300  -15.600   -3.900   8.200    4.100    2.100
     5  105.80  -22.400   -5.800  11.500    6.000    3.300

 MAXIMUM ABSOLUTE VALUES
 NODE       5        1        3        5        5        5
 VALUE  105.80  -15.600   -3.900  11.500    6.000    3.300

 ***** POST1 NODAL DISPLACEMENT LISTING *****

   NODE    UX          UY          UZ          USUM
     1  0.0000E+00  0.0000E+00  0.0000E+00  0.0000E+00
     2  1.2345E-04 -2.3456E-05  1.0000E-06  1.2572E-04
     3  2.4689E-04 -4.6912E-05  2.0000E-06  2.5141E-04
     4  3.7034E-04 -7.0368E-05  3.0000E-06  3.7711E-04
     5  4.9378E-04 -9.3824E-05  4.0000E-06  5.0282E-04

 MAXIMUM ABSOLUTE VALUES
 NODE       5          1          5          5
 VALUE  4.9378E-04 -9.3824E-05 4.0000E-06  5.0282E-04
"""

print("标准 ANSYS PRNSOL 输出格式:")
print("  1. 标题行: ***** POST1 NODAL STRESS LISTING *****")
print("  2. 说明行: THE FOLLOWING X,Y,Z VALUES ARE...")
print("  3. 表头行: NODE    SX    SY    SZ    SXY    SYZ    SXZ")
print("  4. 数据行: 整数 + 6个浮点数")
print("  5. 最大值摘要")


# ═══════════════════════════════════════════════════════════════
# 2. 逐行解析 — 状态机方法
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  2. 逐行解析 — 状态机方法")
print("=" * 60)

def parse_prnsol_state_machine(text: str):
    """用状态机解析 ANSYS PRNSOL 输出。

    状态: SEARCHING → HEADER → DATA → DONE
    """
    lines = text.strip().split("\n")
    state = "SEARCHING"
    data_rows = []
    current_section = None

    for line in lines:
        stripped = line.strip()
        if not stripped:
            continue

        # 状态转换
        if "NODAL STRESS" in stripped:
            state = "HEADER"
            current_section = "stress"
            continue
        elif "NODAL DISPLACEMENT" in stripped:
            state = "HEADER"
            current_section = "displacement"
            continue
        elif "MAXIMUM" in stripped:
            state = "DONE"
            continue

        # 在各状态下处理
        if state == "HEADER":
            # 寻找表头
            if "NODE" in stripped:
                state = "DATA"
            continue

        if state == "DATA":
            # 尝试解析数据行
            parts = stripped.split()
            if len(parts) >= 4:
                try:
                    node_id = int(parts[0])
                    values = [float(v) for v in parts[1:]]
                    data_rows.append({
                        "section": current_section,
                        "node": node_id,
                        "values": values,
                    })
                except ValueError:
                    continue

    return data_rows

# 解析
results = parse_prnsol_state_machine(sample_output)

print(f"解析到 {len(results)} 行数据")
for row in results:
    if row["section"] == "stress":
        print(f"  应力 节点{row['node']}: SX={row['values'][0]:.1f} MPa")
    else:
        print(f"  位移 节点{row['node']}: UX={row['values'][0]:.4e} mm")


# ═══════════════════════════════════════════════════════════════
# 3. 正则表达式提取
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 正则表达式提取")
print("=" * 60)

# 方法A：按行解析（适用于规则格式）
print("方法A — 正则匹配整行:")
pattern = r"^\s*(\d+)\s+([-+]?\d*\.?\d+(?:[eE][+-]?\d+)?)" \
          r"\s+([-+]?\d*\.?\d+(?:[eE][+-]?\d+)?)" \
          r"\s+([-+]?\d*\.?\d+(?:[eE][+-]?\d+)?)" \
          r"\s+([-+]?\d*\.?\d+(?:[eE][+-]?\d+)?)" \
          r"\s+([-+]?\d*\.?\d+(?:[eE][+-]?\d+)?)" \
          r"\s+([-+]?\d*\.?\d+(?:[eE][+-]?\d+)?)" \
          r"\s+([-+]?\d*\.?\d+(?:[eE][+-]?\d+)?)"

for match in re.finditer(pattern, sample_output, re.MULTILINE):
    groups = match.groups()
    node_id = int(groups[0])
    values = [float(v) for v in groups[1:7]]  # 取前6个应力分量
    print(f"  [{node_id}] {[f'{v:.1f}' for v in values]}")

# 方法B：先拆分再识别（适用于不太规则的格式）
print(f"\n方法B — 拆分+类型检测:")
for line in sample_output.split("\n"):
    parts = line.strip().split()
    if len(parts) >= 4:
        # 第一列是整数 → 可能是数据行
        try:
            node_id = int(parts[0])
            floats = []
            for p in parts[1:]:
                try:
                    floats.append(float(p))
                except ValueError:
                    break
            if len(floats) >= 3:
                print(f"  [{node_id}] 解析到 {len(floats)} 个数值")
        except ValueError:
            pass


# ═══════════════════════════════════════════════════════════════
# 4. 处理分页符和特殊格式
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 处理分页符和特殊格式")
print("=" * 60)

# 模拟带分页的输出
paged_output = r"""
***** POST1 NODAL STRESS LISTING *****
   NODE    SX       SY       SZ
     1  100.50  -20.300   -5.100
     2  98.700  -18.900   -4.800

 ***** POST1 NODAL STRESS LISTING ***** (continued)
   NODE    SX       SY       SZ
     3  102.10  -21.000   -5.300
     4  95.300  -15.600   -3.900
"""

# 应对策略
# 1. 移除分页符 (chr(12) = \x0c = ^L)
clean = paged_output.replace("\x0c", "").replace("\f", "")
# 2. 跳过表头重复行 (continued)
# 3. 合并多个 section 的同类型数据

def clean_apdl_output(text: str) -> str:
    """清理 ANSYS 输出中的分页符和冗余行。"""
    # 移除分页符
    text = text.replace("\x0c", "").replace("\f", "")
    # 移除 "PAGE" 行
    text = re.sub(r"^\s*PAGE\s+\d+.*$", "", text, flags=re.MULTILINE)
    # 移除 "(continued)" 标记
    text = text.replace("(continued)", "")
    return text

cleaned = clean_apdl_output(paged_output)
print("清理后的输出:")
for line in cleaned.strip().split("\n"):
    if line.strip():
        print(f"  {line}")


# ═══════════════════════════════════════════════════════════════
# 5. 实战 — 完整解析函数
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. 实战解析 — parse_ansys_output")
print("=" * 60)

def parse_ansys_output(filepath: str) -> dict:
    """解析 ANSYS .out 文件，提取应力/位移/温度数据。

    Args:
        filepath: ANSYS 输出文件路径

    Returns:
        {"stress": [...], "displacement": [...], "temperature": [...]}
    """
    path = Path(filepath)
    if not path.exists():
        # 用模拟数据演示
        text = sample_output
    else:
        # 实际文件读取
        text = path.read_text(encoding="utf-8", errors="replace")

    # 清理
    text = clean_apdl_output(text)

    results = {"stress": [], "displacement": [], "temperature": []}

    # 关键字到结果键的映射
    section_map = {
        "NODAL STRESS": "stress",
        "NODAL DISPLACEMENT": "displacement",
        "NODAL TEMPERATURE": "temperature",
    }

    current_section = None
    in_data = False

    for line in text.split("\n"):
        stripped = line.strip()

        # 检测 section
        for keyword, key in section_map.items():
            if keyword in stripped:
                current_section = key
                in_data = False
                break

        if current_section is None:
            continue

        # 检测表头
        if not in_data and "NODE" in stripped:
            in_data = True
            continue

        # 检测结束
        if "MAXIMUM" in stripped:
            in_data = False
            continue

        # 解析数据
        if in_data and stripped:
            parts = stripped.split()
            try:
                node_id = int(parts[0])
                values = [float(v) for v in parts[1:]]
                results[current_section].append({
                    "node": node_id,
                    "values": values,
                })
            except (ValueError, IndexError):
                continue

    return results

output_path = Path("./output")
output_path.mkdir(exist_ok=True)
sample_file = output_path / "sample_ansys_output.txt"
sample_file.write_text(sample_output, encoding="utf-8")

parsed = parse_ansys_output(str(sample_file))
print(f"应力数据: {len(parsed['stress'])} 个节点")
print(f"位移数据: {len(parsed['displacement'])} 个节点")

if parsed["stress"]:
    node1 = parsed["stress"][0]
    print(f"\n节点 {node1['node']} 应力分量:")
    labels = ["SX", "SY", "SZ", "SXY", "SYZ", "SXZ"]
    for label, val in zip(labels, node1["values"]):
        print(f"  {label}: {val:.1f} MPa")

if parsed["displacement"]:
    node2 = parsed["displacement"][1]
    print(f"\n节点 {node2['node']} 位移分量:")
    for label, val in zip(["UX", "UY", "UZ", "USUM"], node2["values"]):
        print(f"  {label}: {val:.4e} mm")


# ═══════════════════════════════════════════════════════════════
# 6. 工程建议
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. APDL 解析工程建议")
print("=" * 60)

print("""
  1. 先手工确认输出格式
     - 打开 .out 文件，查看实际的数据排列
     - ANSYS 版本不同，列宽和科学计数法格式可能不同

  2. 处理分页
     - 分页符字符: chr(12) 或 ^L
     - 每 56 行一个分页 (默认)
     - 用 .replace() 清理

  3. 验证解析正确性
     - 挑 3-5 个节点手工对比 ANSYS GUI 和 Python 解析结果
     - 检查数值的物理合理性

  4. 处理多载荷步
     - 每个载荷步有独立的 section
     - 用 SET 号或载荷步号区分

  5. 优先使用 DPF 或 PyMAPDL API
     - API 比文本解析更可靠
     - 但文本解析仍是最后的备选方案
""")


# ═══════════════════════════════════════════════════════════════
# 7. 练习
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 修改 parse_ansys_output 函数，使其能处理包含多个
     载荷步的 ANSYS 输出。

  2. 遇到以下 ANSYS 输出行时，如何解析？
     "     1  0.12345E+06  -0.23456E+05"
     写出 Python 代码。

  3. ANSYS 输出中有页眉 (PAGE 1, ..., PAGE N) 和
     列标题重复，编写正则表达式过滤这些行。
""")
