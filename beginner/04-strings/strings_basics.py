"""
SimuLearn Scripts — 初级 #04：字符串处理基础
=============================================
知识点：strings-basics

工程脚本中字符串无处不在：
  - 文件路径拼接
  - 单位标注和格式化输出
  - 日志消息
  - 结果文件命名

本节涵盖：
  1. 字符串创建与引号
  2. 字符串格式化 (f-string, .format(), %)
  3. 常用字符串方法
  4. 路径处理 (pathlib)
  5. ANSYS 输出中的字符串处理

运行方式：
  python strings_basics.py
"""

from pathlib import Path

# ═══════════════════════════════════════════════════════════════
# 1. 字符串创建
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  1. 字符串创建")
print("=" * 60)

# 单引号和双引号等效
material1 = 'Q345'
material2 = "Q345"
print(f"单引号: {material1}, 双引号: {material2}")

# 包含引号的字符串
note = "材料的弹性模量 E = 200 GPa"
note_with_quote = '他说："这个应力值偏大"'
print(f"含双引号: {note_with_quote}")

# 多行字符串 — 用于 APDL 宏、长日志等
apdl_macro = """/PREP7
MP,EX,1,200e9        ! 弹性模量 [Pa]
MP,NUXY,1,0.3        ! 泊松比
MP,DENS,1,7850       ! 密度 [kg/m³]
/SOLU
SOLVE
"""
print(f"多行字符串 (APDL 宏):\n{apdl_macro}")

# 原始字符串 — 避免转义，适合正则和 Windows 路径
raw_path = r"C:\Users\Engineer\analysis\results.out"
print(f"原始字符串: {raw_path}")


# ═══════════════════════════════════════════════════════════════
# 2. 字符串格式化 — f-string 是首选
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  2. 字符串格式化")
print("=" * 60)

stress = 235.5678    # MPa
displacement = 0.001234  # m
node_id = 42
material = "Q345"

# f-string (Python 3.6+) — 推荐方式
print(f"f-string 格式化:")
print(f"  应力 = {stress:.1f} MPa")         # 1位小数
print(f"  应力 = {stress:8.1f} MPa")        # 定宽8字符
print(f"  位移 = {displacement:.3e} m")     # 科学计数法
print(f"  节点 {node_id:06d}")              # 补零到6位
print(f"  材料: {material:<10s}")            # 左对齐
print(f"  完成率: {0.852:.1%}")              # 百分比

# .format() — Python 3 传统方式
print(f"\n.format() 方式:")
print("  应力 = {:.1f} MPa".format(stress))
print("  节点 {:06d} 材料 {}".format(node_id, material))

# % 格式化 — 老式风格，仍在遗留代码中常见
print(f"\n% 格式化 (遗留风格):")
print("  应力 = %.1f MPa" % stress)
print("  节点 %06d 材料 %s" % (node_id, material))

# 命名占位符
print(f"\n命名占位符 (.format):")
template = "{name} 在 {temp}°C 下的弹性模量为 {E} GPa"
print(template.format(name="Q345", temp=200, E=190))


# ═══════════════════════════════════════════════════════════════
# 3. 常用字符串方法
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  3. 常用字符串方法")
print("=" * 60)

result_line = "   Maximum Stress = 235.5 MPa  "

# 去空白
print(f"原始:   '{result_line}'")
print(f"strip:  '{result_line.strip()}'")
print(f"lstrip: '{result_line.lstrip()}'")
print(f"rstrip: '{result_line.rstrip()}'")

# 大小写
unit = "MPa"
print(f"\n'MPa'.upper() → '{unit.upper()}'")
print(f"'MPa'.lower() → '{unit.lower()}'")

# 查找与替换
log = "ERROR: 求解器在第 15 步发散"
print(f"\n查找:")
print(f"  'ERROR' in log → {'ERROR' in log}")
print(f"  log.startswith('ERROR') → {log.startswith('ERROR')}")
print(f"  log.find('发散') → {log.find('发散')} (位置索引)")
print(f"  log.replace('ERROR', 'WARNING') → '{log.replace('ERROR', 'WARNING')}'")

# 分割与连接
csv_line = "1,100.5,-20.3,-5.1,10.0"
parts = csv_line.split(",")
print(f"\n分割: '{csv_line}'.split(',') → {parts}")

joined = " | ".join(parts)
print(f"连接: ' | '.join(parts) → '{joined}'")

# 判断内容
print(f"\n内容判断:")
print(f"  '235.5'.isdigit() → {'235.5'.isdigit()}    ← 含小数点，非纯数字")
print(f"  '235'.isdigit()   → {'235'.isdigit()}      ← 纯数字")
print(f"  '235.5'.replace('.','').isdigit() → "
      f"{'235.5'.replace('.','').isdigit()}")

# 统计
apdl_output = "NODE    SX       SY       SZ"
print(f"\n统计: '{apdl_output}'")
print(f"  长度: {len(apdl_output)}")
print(f"  'NODE' 出现次数: {apdl_output.count('NODE')}")


# ═══════════════════════════════════════════════════════════════
# 4. 路径处理 — pathlib 是最佳实践
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  4. 路径处理 (pathlib)")
print("=" * 60)

# 创建路径对象 — 跨平台
project_dir = Path("C:/Simulation/Project_A")
result_file = project_dir / "results" / "stress.rst"
print(f"项目目录: {project_dir}")
print(f"结果文件: {result_file}")

# 路径组成部分
print(f"\n路径组成部分:")
print(f"  .parent:  {result_file.parent}")
print(f"  .name:    {result_file.name}")
print(f"  .stem:    {result_file.stem}")    # 无扩展名
print(f"  .suffix:  {result_file.suffix}")  # 扩展名

# 路径操作
print(f"\n路径操作:")
print(f"  .exists():    {project_dir.exists()}")

# 批量生成文件名
print(f"\n批量生成工况文件名:")
for load_case in range(1, 4):
    filename = project_dir / f"load_case_{load_case:02d}" / "results.csv"
    print(f"  工况 {load_case}: {filename}")

# 为什么用 pathlib 而不是字符串拼接？
print(f"\n对比:")
# 错误方式（Windows）
wrong = "C:\\Simulation\\" + "Project_A" + "\\" + "results.csv"
# 正确方式
right = Path("C:/Simulation") / "Project_A" / "results.csv"
print(f"  字符串拼接: {wrong}")
print(f"  pathlib:     {right}")
print(f"  优势: pathlib 自动处理 / 和 \\ 的转换")


# ═══════════════════════════════════════════════════════════════
# 5. ANSYS 输出中的字符串处理实战
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  5. ANSYS 输出字符串处理")
print("=" * 60)

# 模拟 ANSYS 输出行
ansys_output = """
***** POST1 NODAL STRESS LISTING *****
 THE FOLLOWING X,Y,Z VALUES ARE IN GLOBAL COORDINATES
   NODE    SX       SY       SZ      SXY      SYZ      SXZ
     1  100.5    -20.3     -5.1    10.0      5.2      2.8
     2   98.7    -18.9     -4.8     9.5      4.9      2.5
     3  102.1    -21.0     -5.3    10.8      5.5      3.0

 MAXIMUM VALUES
   NODE      3        1        3        3        3        3
   VALUE  102.1    -18.9     -4.8    10.8      5.5      3.0
"""

# 提取数据行
lines = ansys_output.strip().split("\n")
data_lines = []
for line in lines:
    stripped = line.strip()
    # 跳过标题、空行、非数据行
    if not stripped:
        continue
    if stripped.startswith("*") or "VALUES" in stripped:
        continue
    if "NODE" in stripped and "SX" in stripped:
        continue
    # 尝试按空格分割
    parts = stripped.split()
    if len(parts) >= 7:
        try:
            # 第一列必须是数字（节点号）
            int(parts[0])
            data_lines.append(parts)
        except ValueError:
            continue

print(f"解析到 {len(data_lines)} 行数据:")
for row in data_lines:
    print(f"  节点 {row[0]}: SX={float(row[1]):.1f} SY={float(row[2]):.1f}")

# 提取最大值行
print(f"\n提取最大值行:")
for line in lines:
    if "MAXIMUM" in line or "VALUE" in line:
        print(f"  {line.strip()}")


# ═══════════════════════════════════════════════════════════════
# 6. 工程报告格式化
# ═══════════════════════════════════════════════════════════════

print("\n" + "=" * 60)
print("  6. 工程报告格式化")
print("=" * 60)

# 生成格式化的分析摘要
results = {
    "project": "支架强度校核",
    "material": "Q345",
    "max_stress_MPa": 180.5,
    "allowable_MPa": 156.7,
    "max_disp_mm": 0.127,
    "disp_limit_mm": 0.5,
    "passed": False,
}

report = f"""
╔══════════════════════════════════════╗
║  分析摘要：{results['project']:<20s}      ║
╠══════════════════════════════════════╣
║  材料:     {results['material']:<24s} ║
║  最大应力: {results['max_stress_MPa']:>8.1f} MPa{'':>13s}║
║  许用应力: {results['allowable_MPa']:>8.1f} MPa{'':>13s}║
║  最大位移: {results['max_disp_mm']:>8.3f} mm{'':>13s}║
║  位移限值: {results['disp_limit_mm']:>8.3f} mm{'':>13s}║
║  结论:     {'通过 ✅' if results['passed'] else '不通过 ❌':<22s}║
╚══════════════════════════════════════╝
"""
print(report)


# ═══════════════════════════════════════════════════════════════
# 7. 练习
# ═══════════════════════════════════════════════════════════════

print("=" * 60)
print("  练习")
print("=" * 60)
print("""
  1. 用 f-string 格式化以下输出：
     节点 123 在 X 方向的位移为 0.001234 m (1.234 mm)

  2. 编写一个函数 generate_filename(base_dir, load_case, extension)
     返回格式为 "base_dir/LoadCase_01.extension" 的路径。
     使用 pathlib。

  3. 解析以下 ANSYS 错误行，提取错误代码和描述：
     "*** ERROR ***  CP = 15.2  TIME= 12:30:45
      Element 5421 has a negative radius of curvature."

  4. 用字符串方法检查用户输入的文件名是否以 ".rst" 或 ".rth" 结尾，
     如果是则打印"ANSYS 结果文件"，否则打印"未知格式"。
""")
