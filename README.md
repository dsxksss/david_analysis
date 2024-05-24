# tcmio_extractor

## 简介

david_analysis 富集通路提取脚本

## Tip 运行前请先确保python环境中存在 pandas, zeep 依赖

### 支持参数

| 参数 | 描述 |
| --- | --- |
| --input_file | 输入文件名称 |
| --auth_email | 验证邮箱 |
| --output_file | 输出文件名称, 默认chartReport.csv |
| --identifier | 输入文件中数据的类型, 默认UNIPROT_ACCESSION |
| --pvalue | 设定pvalue值, 默认0.1 |
| --count | 设定最少数量阈值, 默认2 |
| --category | 设定需要过滤的category值, 默认不过滤 |

### 使用例子

```bash
python src/david_analysis --input_file "test.txt" --auth_email "xxxxxxxxx@qq.com"
```
