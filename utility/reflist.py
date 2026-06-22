#!/usr/bin/env python3
"""
从 .bbl 文件提取纯文本参考文献列表（零依赖，纯 Python 标准库）。
- 自动搜索上级目录及其子目录中的 main.bbl 或 thesis.bbl
- 输出为每行一条的纯文本，默认带序号 [1] [2] ...，无额外空行
用法：
  python reflist.py                           # 自动查找 .bbl，输出带序号的 reflist.txt
  python reflist.py input.bbl out.txt         # 手动指定
  python reflist.py --no-numbered             # 自动查找，但不加序号
"""
import re
import os
import sys
import argparse
import glob


# ----------------------------------------------------------------------
#  LaTeX 重音与特殊字符 → Unicode 转换
# ----------------------------------------------------------------------
def expand_latex_accents(text: str) -> str:
    """展开 LaTeX 重音命令（如 \'{e} -> é），需在去除花括号前调用。"""
    accent_map = {
        "\\'":  {'a': 'á', 'e': 'é', 'i': 'í', 'o': 'ó', 'u': 'ú',
                 'A': 'Á', 'E': 'É', 'I': 'Í', 'O': 'Ó', 'U': 'Ú'},
        '\\`':  {'a': 'à', 'e': 'è', 'i': 'ì', 'o': 'ò', 'u': 'ù',
                 'A': 'À', 'E': 'È', 'I': 'Ì', 'O': 'Ò', 'U': 'Ù'},
        '\\^':  {'a': 'â', 'e': 'ê', 'i': 'î', 'o': 'ô', 'u': 'û',
                 'A': 'Â', 'E': 'Ê', 'I': 'Î', 'O': 'Ô', 'U': 'Û'},
        '\\"':  {'a': 'ä', 'e': 'ë', 'i': 'ï', 'o': 'ö', 'u': 'ü',
                 'A': 'Ä', 'E': 'Ë', 'I': 'Ï', 'O': 'Ö', 'U': 'Ü'},
        '\\~':  {'a': 'ã', 'o': 'õ', 'n': 'ñ',
                 'A': 'Ã', 'O': 'Õ', 'N': 'Ñ'},
        '\\c':  {'c': 'ç', 'C': 'Ç'},
        '\\aa': {'a': 'å', 'A': 'Å'},
        '\\o':  {'o': 'ø', 'O': 'Ø'},
        '\\ae': {'a': 'æ', 'A': 'Æ'},
        '\\oe': {'o': 'œ', 'O': 'Œ'},
        '\\ss': {'s': 'ß'},
        '\\l':  {'l': 'ł', 'L': 'Ł'},
    }

    for cmd, subs in accent_map.items():
        if cmd in ('\\aa', '\\o', '\\ae', '\\oe', '\\ss', '\\l'):
            pattern = re.escape(cmd) + r'(?:\{([^}]*)\}|(\s*))'
            def repl(m, s=subs):
                content = m.group(1) if m.group(1) else m.group(2).strip()
                return s.get(content, s.get('a', cmd))
            text = re.sub(pattern, repl, text)
        else:
            pattern = re.escape(cmd) + r'\{([^}]+)\}'
            def repl(m, s=subs):
                key = m.group(1)
                return s.get(key, m.group(0))
            text = re.sub(pattern, repl, text)

    extra = [
        ("\\'a", 'á'), ("\\'A", 'Á'), ("\\'e", 'é'), ("\\'E", 'É'),
        ("\\'i", 'í'), ("\\'I", 'Í'), ("\\'o", 'ó'), ("\\'O", 'Ó'),
        ("\\'u", 'ú'), ("\\'U", 'Ú'),
        ("\\`a", 'à'), ("\\`A", 'À'), ("\\`e", 'è'), ("\\`E", 'È'),
        ("\\`i", 'ì'), ("\\`I", 'Ì'), ("\\`o", 'ò'), ("\\`O", 'Ò'),
        ("\\`u", 'ù'), ("\\`U", 'Ù'),
        ('\\^a', 'â'), ('\\^A', 'Â'), ('\\^e', 'ê'), ('\\^E', 'Ê'),
        ('\\^i', 'î'), ('\\^I', 'Î'), ('\\^o', 'ô'), ('\\^O', 'Ô'),
        ('\\^u', 'û'), ('\\^U', 'Û'),
        ('\\"a', 'ä'), ('\\"A', 'Ä'), ('\\"e', 'ë'), ('\\"E', 'Ë'),
        ('\\"i', 'ï'), ('\\"I', 'Ï'), ('\\"o', 'ö'), ('\\"O', 'Ö'),
        ('\\"u', 'ü'), ('\\"U', 'Ü'),
        ('\\~a', 'ã'), ('\\~A', 'Ã'), ('\\~o', 'õ'), ('\\~O', 'Õ'),
        ('\\~n', 'ñ'), ('\\~N', 'Ñ'),
        ('\\c{c}', 'ç'), ('\\c{C}', 'Ç'),
    ]
    for pat, repl in extra:
        text = text.replace(pat, repl)
    return text


def latex_to_plain_text(text: str) -> str:
    """完整管线：LaTeX 片段 → 纯净 Unicode 文本。"""
    text = text.replace(r'\_', '_')
    text = expand_latex_accents(text)
    text = text.replace('~', ' ')
    text = text.replace('---', '\u2014').replace('--', '\u2013')
    static_repl = [
        ('\\&', '&'), ('\\%', '%'), ('\\#', '#'),
        ('\\{', '{'), ('\\}', '}'),
        ('\\textbackslash', '\\'),
        ('``', '\u201C'), ("''", '\u201D'),
        ('\\alpha', 'α'), ('\\beta', 'β'), ('\\gamma', 'γ'),
        ('\\delta', 'δ'), ('\\epsilon', 'ε'), ('\\theta', 'θ'),
        ('\\mu', 'μ'), ('\\lambda', 'λ'),
    ]
    for a, b in static_repl:
        text = text.replace(a, b)

    text = re.sub(r'\\url\{([^{}]*)\}', r'\1', text)
    text = re.sub(r'\\href\{[^}]*\}\{([^{}]*)\}', r'\1', text)

    for cmd in ['emph', 'textbf', 'textit', 'textsl', 'textsc', 'texttt', 'textsf']:
        text = re.sub(r'\\' + cmd + r'\{((?:[^{}]|\{[^{}]*\})*)\}', r'\1', text)

    text = re.sub(r'\\doi\s*\{?', '', text)
    text = re.sub(r'[{}]', '', text)
    text = re.sub(r'\\[a-zA-Z]+\s?', ' ', text)
    text = re.sub(r'\s+(\[[A-Za-z/]+\])', r'\1', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


# ----------------------------------------------------------------------
#  文件解析与输出
# ----------------------------------------------------------------------
def extract_bbl_to_txt(bbl_path: str, txt_path: str, numbered: bool = True):
    with open(bbl_path, 'r', encoding='utf-8') as f:
        content = f.read()

    parts = re.split(r'\\bibitem(?:\[.*?\])?\{[^}]*\}', content)
    entries = parts[1:]

    if not entries:
        print("未找到任何参考文献条目，请检查 .bbl 文件。")
        return

    cleaned = []
    for i, entry in enumerate(entries, start=1):
        entry = entry.strip()
        end_match = re.search(r'(.*?)\\end\{', entry, re.DOTALL)
        if end_match:
            entry = end_match.group(1)
        plain = latex_to_plain_text(entry)
        if plain:
            if numbered:
                plain = f"[{i}] {plain}"
            cleaned.append(plain)

    with open(txt_path, 'w', encoding='utf-8') as out:
        out.write('\n'.join(cleaned) + '\n')

    print(f"成功导出 {len(cleaned)} 条参考文献: {txt_path}")


# ----------------------------------------------------------------------
#  自动查找 .bbl 文件
# ----------------------------------------------------------------------
def find_default_bbl() -> str | None:
    parent = os.path.abspath(os.path.join(os.getcwd(), '..'))
    all_bbl = glob.glob(os.path.join(parent, '**', '*.bbl'), recursive=True)
    if not all_bbl:
        return None
    for preferred in ('main.bbl', 'thesis.bbl'):
        for path in all_bbl:
            if os.path.basename(path) == preferred:
                return path
    return all_bbl[0]


# ----------------------------------------------------------------------
#  主入口
# ----------------------------------------------------------------------
if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='从 .bbl 文件提取纯文本参考文献列表（默认带序号，无空行）')
    parser.add_argument(
        'bbl_file', nargs='?', default=None,
        help='输入的 .bbl 文件（默认自动搜索 ../ 下子目录中的 main.bbl 或 thesis.bbl）')
    parser.add_argument(
        'output', nargs='?', default='reflist.txt',
        help='输出的文本文件（默认 reflist.txt）')
    parser.add_argument(
        '--no-numbered', action='store_true',
        help='不添加序号（默认添加 [1] [2] …）')
    args = parser.parse_args()

    if args.bbl_file is None:
        auto_path = find_default_bbl()
        if auto_path is None:
            print("未找到 .bbl 文件。请先编译论文，或手动指定路径，如：python reflist.py input.bbl out.txt")
            sys.exit(1)
        print(f"自动选择 .bbl 文件：{auto_path}")
        args.bbl_file = auto_path

    numbered = not args.no_numbered
    extract_bbl_to_txt(args.bbl_file, args.output, numbered)