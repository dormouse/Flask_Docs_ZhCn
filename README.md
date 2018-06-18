# Flask 简体中文文档

## 关于译者
由 Dormouse Young 发起并独立翻译，其余参与和修正伙伴参见 contributors 。

Initiate and translated by Dormouse Young.

## 版本

现在正在翻译的是 Flask 1.0.2 的文档。

Flask 1.0.2 docs are being translating now.

## 线上地址

[http://dormousehole.rtfd.org](http://dormousehole.rtfd.org)

## 制作本地文档

### Html 文档

主要步骤为：

* 克隆本项目
* 创建虚拟环境（示例使用 anaconda ）
* 安装依赖
* 生成文档（文档生成在 _bulid 目录下)

命令示例：

```shell
git clone git@github.com:dormouse/Flask_Docs_ZhCn.git
cd Flask_Docs_ZhCn/
conda create -n flask_doc python=3*
source activate flask_doc
pip install -r requirements.txt
make html
```

### PDF 文档

参见 https://dormouse.github.io/rst-pdf.html



