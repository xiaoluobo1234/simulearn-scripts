"""
SimuLearn Scripts — APDL 输出解析器
====================================
知识点：读取 APDL 输出文件 (beginner/15-apdl-parse)

提供从 ANSYS APDL 文本输出中提取数据的通用函数。
支持 PRNSOL（节点解）和 PRESOL（单元解）两种常见格式。

使用方式：
  from utils.apdl_parser import parse_prnsol, parse_presol

  nodes = parse_prnsol("results.out")
  elements = parse_presol("results.out")
"""

import re
from collections import defaultdict
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class NodeResult:
    """单节点结果。"""
    node_id: int
    values: dict[str, float] = field(default_factory=dict)


@dataclass
class ElementResult:
    """单单元结果。"""
    element_id: int
    node_id: int          # 单元内的节点
    values: dict[str, float] = field(default_factory=dict)


# ─────────────────────────────────────────────────────────────
# 通用解析辅助函数
# ─────────────────────────────────────────────────────────────

def _find_section_start(
    lines: list[str],
    keyword: str,
    start_from: int = 0,
) -> int:
    """在行列表中查找 ANSYS 输出关键字所在行。

    返回行号（0-based），未找到返回 -1。
    """
    for i, line in enumerate(lines[start_from:], start_from):
        if keyword in line:
            return i
    return -1


def _parse_data_block(
    lines: list[str],
    start: int,
    columns: list[str],
    id_col: str = "NODE",
) -> list[dict]:
    """解析 ANSYS 输出的数据块。

    ANSYS 典型输出格式:
      ***** POST1 NODAL STRESS LISTING *****
      THE FOLLOWING X,Y,Z VALUES ARE IN GLOBAL COORDINATES
        NODE    SX       SY       SZ      SXY      SYZ      SXZ
          1  100.0    -20.0     -5.0    10.0      5.0      2.0
          2   98.5    -18.3     -4.8     9.5      4.8      1.9
        ...

    Args:
        lines: 所有行
        start: 数据起始行号（表头行）
        columns: 列名列表
        id_col: ID 列名

    Returns:
        数据字典列表
    """
    results = []

    # 从表头下一行开始
    i = start + 1
    while i < len(lines):
        line = lines[i].strip()

        # 空行 → 继续
        if not line:
            i += 1
            continue

        # 遇到新的节标题 → 停止
        if line.startswith("*****") or "LISTING" in line:
            break

        # 遇到分页标记 → 跳过
        if line.startswith("\x0c") or "PAGE" in line:
            i += 1
            continue

        # 尝试解析数值行
        parts = line.split()
        if len(parts) >= len(columns):
            try:
                row = {}
                for j, col in enumerate(columns):
                    row[col] = float(parts[j])
                results.append(row)
            except (ValueError, IndexError):
                # 非数据行（标题等），跳过
                pass

        i += 1

    return results


# ─────────────────────────────────────────────────────────────
# PRNSOL 解析
# ─────────────────────────────────────────────────────────────

# ANSYS 不同 PRNSOL 输出的列名映射
_PRNSOL_PATTERNS = {
    # 节点应力 (PRNSOL, S)
    "NODAL STRESS": ["NODE", "SX", "SY", "SZ", "SXY", "SYZ", "SXZ"],
    "NODAL STRESS": ["NODE", "S1", "S2", "S3", "SINT", "SEQV"],

    # 节点位移 (PRNSOL, U)
    "NODAL DISPLACEMENT": ["NODE", "UX", "UY", "UZ", "USUM"],
    "NODAL DISPLACEMENT": ["NODE", "UX", "UY", "UZ", "ROTX", "ROTY", "ROTZ", "USUM"],

    # 节点温度 (PRNSOL, TEMP)
    "NODAL TEMPERATURE": ["NODE", "TEMP"],
}


def parse_prnsol(
    filepath: str,
    component: str = "S",
) -> list[dict]:
    """解析 ANSYS PRNSOL 输出文件。

    Args:
        filepath: .out 或 .txt 文件路径
        component: 结果类型 ("S"=应力, "U"=位移, "TEMP"=温度)

    Returns:
        节点结果列表 [{NODE: 1, SX: 100.0, SY: -20.0, ...}, ...]
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {filepath}")

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    lines = content.split("\n")

    # 确定搜索关键字和列名
    if component.upper() == "S":
        keyword = "NODAL STRESS"
        columns = ["NODE", "SX", "SY", "SZ", "SXY", "SYZ", "SXZ"]
        alt_columns = ["NODE", "S1", "S2", "S3", "SINT", "SEQV"]
    elif component.upper() == "U":
        keyword = "NODAL DISPLACEMENT"
        columns = ["NODE", "UX", "UY", "UZ", "USUM"]
        alt_columns = ["NODE", "UX", "UY", "UZ", "ROTX", "ROTY", "ROTZ", "USUM"]
    elif component.upper() in ("TEMP", "T"):
        keyword = "NODAL TEMPERATURE"
        columns = ["NODE", "TEMP"]
        alt_columns = None
    else:
        raise ValueError(f"未知的结果类型: {component} (应为 S/U/TEMP)")

    # 查找数据块起始位置
    start = _find_section_start(lines, keyword)
    if start < 0:
        return []

    # 先尝试主格式
    results = _parse_data_block(lines, start, columns)

    # 如果为空且存在备选格式，尝试备选
    if not results and alt_columns:
        # 需要重新搜索，因为可能是下一个 section
        next_start = _find_section_start(lines, keyword, start + 1)
        if next_start > start:
            results = _parse_data_block(lines, next_start, alt_columns)

    return results


# ─────────────────────────────────────────────────────────────
# PRESOL 解析
# ─────────────────────────────────────────────────────────────

def parse_presol(
    filepath: str,
    component: str = "S",
) -> list[dict]:
    """解析 ANSYS PRESOL 输出文件（单元解）。

    Args:
        filepath: .out 文件路径
        component: 结果类型 ("S"=应力, "EPEL"=弹性应变)

    Returns:
        单元结果列表 [{ELEM: 1, NODE: 1, SX: 100.0, ...}, ...]
    """
    path = Path(filepath)
    if not path.exists():
        raise FileNotFoundError(f"文件不存在: {filepath}")

    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()

    lines = content.split("\n")

    if component.upper() == "S":
        keyword = "ELEMENT STRESS"
        columns = ["ELEM", "NODE", "SX", "SY", "SZ", "SXY", "SYZ", "SXZ"]
    elif component.upper() == "EPEL":
        keyword = "ELEMENT ELASTIC STRAIN"
        columns = ["ELEM", "NODE", "EPELX", "EPELY", "EPELZ",
                   "EPELXY", "EPELYZ", "EPELXZ"]
    else:
        raise ValueError(f"未知的结果类型: {component} (应为 S/EPEL)")

    start = _find_section_start(lines, keyword)
    if start < 0:
        return []

    return _parse_data_block(lines, start, columns)


# ─────────────────────────────────────────────────────────────
# 便捷转换函数
# ─────────────────────────────────────────────────────────────

def prnsol_to_structured(results: list[dict]) -> dict[int, dict]:
    """将 PRNSOL 结果列表转为 {node_id: {col: value}} 字典。

    适用于按节点 ID 快速查询。
    """
    structured = {}
    for row in results:
        node_id = int(row["NODE"])
        structured[node_id] = {k: v for k, v in row.items() if k != "NODE"}
    return structured


def extract_column(results: list[dict], column: str) -> list[float]:
    """提取结果列表中某一列的所有值。

    Example:
        sx_values = extract_column(results, "SX")
    """
    return [row[column] for row in results if column in row]


# ─────────────────────────────────────────────────────────────
# 正则解析（备选方案 — 更灵活）
# ─────────────────────────────────────────────────────────────

def parse_with_regex(
    text: str,
    pattern: str = r"(\d+)\s+([-+]?\d*\.?\d+(?:[eE][+-]?\d+)?)"
) -> list[tuple]:
    """用正则表达式从 ANSYS 输出文本中提取数值对。

    这是一个更灵活的备选方案，适合非标准输出格式。

    Args:
        text: 原始文本
        pattern: 正则模式，默认匹配 "整数 浮点数"

    Returns:
        (ID, value) 元组列表
    """
    return re.findall(pattern, text)


# ─────────────────────────────────────────────────────────────
# 自测
# ─────────────────────────────────────────────────────────────

if __name__ == "__main__":
    # 用模拟数据测试
    sample_output = """***** POST1 NODAL STRESS LISTING *****
 THE FOLLOWING X,Y,Z VALUES ARE IN GLOBAL COORDINATES
   NODE    SX       SY       SZ      SXY      SYZ      SXZ
     1  100.0    -20.0     -5.0    10.0      5.0      2.0
     2   98.5    -18.3     -4.8     9.5      4.8      1.9
     3  102.1    -21.0     -5.2    11.0      5.5      2.3
"""

    # 写入临时文件
    import tempfile
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".out", delete=False, encoding="utf-8"
    ) as f:
        f.write(sample_output)
        tmp_path = f.name

    try:
        results = parse_prnsol(tmp_path, "S")
        print(f"解析到 {len(results)} 个节点结果")
        for r in results:
            print(f"  节点 {int(r['NODE'])}: SX={r['SX']} SY={r['SY']} SXY={r['SXY']}")

        # 结构化转换
        structured = prnsol_to_structured(results)
        print(f"\n结构化查询: 节点2的SX = {structured[2]['SX']}")

        # 提取列
        sx_all = extract_column(results, "SX")
        print(f"所有节点 SX: {sx_all}")

        assert len(results) == 3
        assert results[0]["SX"] == 100.0
        assert structured[2]["SY"] == -18.3

        print("\n✅ 所有解析测试通过")

    finally:
        Path(tmp_path).unlink()
