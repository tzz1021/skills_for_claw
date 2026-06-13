"""
win-py-runner — 在 Windows 上安全执行 Python 代码

作用：
  代替 python -c "..." 命令行内嵌方式，避免 PowerShell GBK 编码和引号转义问题。

用法：
  python run_py.py <脚本内容或文件路径>
  python run_py.py <脚本文件路径>               # 执行已有文件
  python run_py.py -c "print('hello')"          # 从参数传入代码（需处理引号转义）
  python run_py.py -                            # 从 stdin 读取代码

推荐用法（避坑）：
  # 1. 先写入临时文件（用 write 工具）
  # 2. 再执行：
  python "C:\path\to\temp_script.py"
  
  完全绕过 python -c，不经过 PowerShell 引号解析。

编码处理：
  - 脚本文件保存为 UTF-8（write 工具默认）
  - Python 读取 UTF-8 文件无编码问题
  - 如果执行结果含中文/emoji 打印到终端乱码，加环境变量：
    $env:PYTHONIOENCODING='utf-8'; python script.py

快速模板（PYTHONIOENCODING 预制）：
  $env:PYTHONIOENCODING='utf-8'; python script.py
"""

import sys
import os
import subprocess
import tempfile
import pathlib

def run_script(code: str, cwd: str | None = None) -> tuple[int, str, str]:
    """执行 Python 代码，返回 (returncode, stdout, stderr)"""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    proc = subprocess.run(
        [sys.executable, "-u", "-c", code],
        capture_output=True,
        text=True,
        cwd=cwd or os.getcwd(),
        env=env,
    )
    return proc.returncode, proc.stdout, proc.stderr

def run_file(filepath: str, cwd: str | None = None) -> tuple[int, str, str]:
    """执行 Python 文件，返回 (returncode, stdout, stderr)"""
    env = os.environ.copy()
    env["PYTHONIOENCODING"] = "utf-8"
    
    proc = subprocess.run(
        [sys.executable, "-u", filepath],
        capture_output=True,
        text=True,
        cwd=cwd or os.getcwd(),
        env=env,
    )
    return proc.returncode, proc.stdout, proc.stderr

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法:")
        print("  python run_py.py <文件路径>")
        print("  python run_py.py -c <代码>")
        print("  python run_py.py -    # 从 stdin")
        sys.exit(1)
    
    if sys.argv[1] == "-c":
        code = " ".join(sys.argv[2:])
        rc, stdout, stderr = run_script(code)
    elif sys.argv[1] == "-":
        code = sys.stdin.read()
        rc, stdout, stderr = run_script(code)
    else:
        rc, stdout, stderr = run_file(sys.argv[1])
    
    if stdout:
        print(stdout, end="")
    if stderr:
        print(stderr, file=sys.stderr, end="")
    sys.exit(rc)
