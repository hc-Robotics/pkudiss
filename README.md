# pkuDiss - 北京大学研究生学位论文 LaTeX 模板

pkuDiss 是 **Peking University Dissertation LaTeX Template** 的缩写，提供了一套符合北京大学研究生学位论文（现阶段主要为博士学位论文）排版要求的 LaTeX 模板。模板严格遵循学校相关规范，并针对 **北京大学先进制造与机器人学院** 的格式要求进行适配。

## 主要特性

- **规范驱动**：遵循北京大学研究生院学位论文撰写指南，并符合先进制造与机器人学院相关格式审查。
- **多环境支持**：支持本地编译（推荐 TeX Live + VS Code + LaTeX Workshop）与 Overleaf 云端编译。
- **开箱即用的 VS Code 配置**：内含 `.vscode/settings.json`，启用自动保存编译，所有中间文件与 PDF 输出至 `_build` 目录，保持工作区整洁。
- **实用附件工具**：`utilities/reflist.py` 可从 BibTeX 生成的 `.bbl` 文件中提取纯净的参考文献文本列表，便于图书馆论文提交系统的填写。
- **Git 友好**：可通过 Git 同步至 GitHub 或 Gitee，实现云端备份与协作。

## 快速上手

### 环境要求

- 本地编译需安装 **TeX Live**（推荐最新版），确保 `xelatex` 和 `latexmk` 可用。
- 编辑器建议使用 **VS Code**，并安装扩展 **LaTeX Workshop**。
- Python 3.x（仅在使用 `reflist.py` 工具时需用，非必须）。

### 本地编译（TeX Live + VS Code + LaTeX Workshop）

1. **安装 TeX Live**  
   推荐安装最新版 TeX Live（需包含 XeLaTeX 与 `latexmk`）。  
   下载地址：https://www.tug.org/texlive/

2. **克隆模板仓库** 
   ```bash
   git clone https://github.com/hc-Robotics/pkudiss.git
   cd pkuDiss
   ```


3. **使用 VS Code 打开项目**  
   安装扩展 LaTeX Workshop。

4. **自动编译配置**  
   工作路径下 .vscode/settings.json 已为配置如下：
    ```json
    {
      "latex-workshop.latex.outDir": "_build",
      "latex-workshop.latex.auxDir": "_build",
      "latex-workshop.latex.recipe.default": "xelatexmk",
      "latex-workshop.latex.autoBuild.run": "onSave",
      "latex-workshop.latex.recipes": [
        { "name": "xelatexmk", "tools": ["xelatexmk"] }
      ],
      "latex-workshop.latex.tools": [
        {
          "name": "xelatexmk",
          "command": "latexmk",
          "args": [
            "-synctex=1",
            "-interaction=nonstopmode",
            "-file-line-error",
            "-xelatex",
            "-outdir=%OUTDIR%",
            "-auxdir=%AUXDIR%",
            "%DOC%"
          ]
        }
      ]
    }
    ```
    - 默认编译器为 XeLaTeX（中文支持）。

    - 保存 .tex 文件即自动编译，类似 Overleaf 体验。

    - 编译产物（包括 PDF）统一存放在 _build/ 子目录，根目录保持清爽。

5. **开始写作**  
    打开主文件（如 thesis.tex 或 main.tex），修改内容，保存后即可在 _build/ 下得到 PDF。
    若需手动编译，可在终端执行：
    ```bash
    latexmk -xelatex -outdir=_build -auxdir=_build main.tex
    ```

## 使用 Overleaf 云端编译
1. 下载本仓库的 ZIP 压缩包。

2. 在 Overleaf 中点击 “New Project” → “Upload Project”，上传 ZIP 文件。

3. 进入项目后，点击左上角 Menu，将 Compiler 设置为 XeLaTeX。

4. 打开主 .tex 文件，点击 “Recompile” 即可。

注：免费版 Overleaf 编译速度较慢，大型论文建议使用本地编译。

## 实用工具
### 参考文献列表提取（utilities/reflist.py）
该工具从 BibTeX 编译产生的 .bbl 文件提取纯文本参考文献列表，可直接用于图书馆论文提交系统中的参考文献信息填写。

- **零依赖**：仅使用 Python 3 标准库。

- **自动查找**：默认搜索上级目录及子目录中的 main.bbl 或 thesis.bbl。

- **序号控制**：输出默认带 [1] [2] … 序号，也可生成无序号列表。

```bash
# 自动查找 .bbl，生成带序号的 reflist.txt
python utilities/reflist.py

# 手动指定输入文件与输出文件
python utilities/reflist.py path/to/your.bbl output.txt

# 输出不带序号的参考文献列表
python utilities/reflist.py --no-numbered
```

生成的文件每行一条参考文献，无多余空行，可以直接复制使用。

## 反馈与贡献
遇到任何问题，或者有改进建议，欢迎通过以下方式交流：

- **GitHub Issues**：https://github.com/hc-Robotics/pkuDiss/issues

- **邮件**：hc.robotic@gmail.com

您也可以直接 Fork 本仓库并提交 Pull Request。

## 致谢
本模板建立在早期多位北大 LaTeX 模板维护者的工作之上，感谢他们的付出。当前版本特别依据 北京大学先进制造与机器人学院 的详细格式要求进行了适配，并已通过相关审查。
感谢所有提供反馈和帮助的老师和同学。

提示：不同院系可能有个性化的格式规定，请以北京大学研究生院发布的最新官方文件为准，并适当调整模板样式。本模板力求通用且易定制。

