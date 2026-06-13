---
name: win-py-runner
description: Safely execute Python code on Windows without PowerShell encoding issues. Use when: (1) Running Python code on Windows from a POSIX-like shell (Git Bash, MSYS2, BusyBox) or PowerShell where Chinese characters, emoji, or Unicode may garble output. (2) Avoiding the python -c "..." inline approach that suffers from PowerShell quote-escape hell and GBK encoding failure. (3) Any situation where Python stdout contains non-ASCII characters that need clean UTF-8 output.
---

# Win Py Runner — Windows Python 执行器

## 问题

Windows 上通过 PowerShell 或 POSIX shell 执行 `python -c "代码"` 时，中文/emoji 输出乱码（GBK vs UTF-8 冲突），且 PowerShell 的引号转义规则复杂，容易写错。

## 核心规则

### 规则 1：永远用文件执行，不用 python -c

**错误方式（禁止）：**
```
python -c "print('你好')"
```
PowerShell 会拦截双引号内的内容，GBK 编码中文会崩。

**正确方式：**
```
# 先写文件（用 write 工具，UTF-8 保存）
write("temp.py", "print('你好')")

# 再执行
python temp.py
```

### 规则 2：执行时设 PYTHONIOENCODING=utf-8

确保 Python 输出用 UTF-8 编码：

```powershell
$env:PYTHONIOENCODING='utf-8'; python script.py
```

或一次性：

```powershell
$env:PYTHONIOENCODING='utf-8'; python -u script.py  # -u 禁用 stdout 缓冲
```

## 工作流

### 场景 A：执行一段 Python 代码

```python
# 1. 用 write 工具写临时文件
Path: C:\Users\tzz\.openclaw\workspace\_temp_py.py
Content:
import sys
# 你的代码
print("你好 ✅")

# 2. 用 exec 执行
exec: $env:PYTHONIOENCODING='utf-8'; python "C:\Users\tzz\.openclaw\workspace\_temp_py.py"

# 3. 清理（可选）
```

### 场景 B：需要捕获 stdout/stderr

```python
# 用 subprocess 自己捕获
import subprocess, sys
proc = subprocess.run(
    [sys.executable, "-u", "-c", "print('你好')"],
    capture_output=True, text=True,
    env={**__import__('os').environ, "PYTHONIOENCODING": "utf-8"}
)
print(proc.stdout)  # 干净的 UTF-8 字符串
```

### 场景 C：复杂的多文件执行

用 `run_py.py` 脚本（scripts/run_py.py）：

```powershell
# 执行文件
$env:PYTHONIOENCODING='utf-8'; python scripts/run_py.py my_script.py

# 执行内联代码（仅当代码无中文/特殊字符时）
$env:PYTHONIOENCODING='utf-8'; python scripts/run_py.py -c "print(1+1)"
```

## 调试编码问题

如果输出仍然乱码：

```powershell
# 检当前编码
python -c "import sys; print(sys.stdout.encoding)"

# 测试输出
$env:PYTHONIOENCODING='utf-8'; python -c "print('中文测试 ✅')"
```

预期输出：`中文测试 ✅`

## 不同环境对比

| 环境 | 编码问题 | 推荐操作 |
|------|---------|---------|
| **PowerShell (powershell.exe)** | ⚠️ GBK 默认 | 写文件 + PYTHONIOENCODING |
| **PowerShell Core (pwsh.exe)** | ✅ UTF-8 默认 | 写文件即可 |
| **Git Bash / MSYS2** | ⚠️ GBK 输出通道 | 写文件 + PYTHONIOENCODING |
| **WSL** | ✅ UTF-8 | 无问题 |
| **Linux / macOS** | ✅ UTF-8 | 无问题，python -c 可用 |
