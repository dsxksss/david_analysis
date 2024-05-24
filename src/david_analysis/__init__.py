import argparse
import pandas as pd
import sys
from zeep import Client


def read_file(file_path, identifier):
    # Read input gene list file, convert ids to a comma-delimited string
    df = pd.read_csv(
        file_path,
        usecols=[0],
        delimiter="\t",
        index_col=False,
        names=[identifier],
    )
    input_ids = ",".join(df[identifier].astype(str).unique().tolist())
    return input_ids


def get_chart_report(
    input_file, output_file, auth_email, identifier, p_value, count, category
):
    client = Client(
        "https://david.ncifcrf.gov/webservice/services/DAVIDWebService?wsdl"
    )
    client.service.authenticate(auth_email)
    input_ids = read_file(input_file, identifier)
    client.service.addList(input_ids, identifier, "david_analysis", 0)
    client.service.setCategories(category)
    chartReport = client.service.getChartReport(p_value, count)
    chartRow = len(chartReport)
    print("Total chart records:", chartRow)

    with open(output_file, "w") as w:
        w.write(
            "Category\tTerm\tCount\t%\tPvalue\tGenes\tList Total\tPop Hits\tPop Total\tFold Enrichment\tBonferroni\tBenjamini\tFDR\n"
        )
        for simpleChartRecord in chartReport:
            categoryName = simpleChartRecord.categoryName
            termName = simpleChartRecord.termName
            listHits = simpleChartRecord.listHits
            percent = simpleChartRecord.percent
            ease = simpleChartRecord.ease
            Genes = simpleChartRecord.geneIds
            listTotals = simpleChartRecord.listTotals
            popHits = simpleChartRecord.popHits
            popTotals = simpleChartRecord.popTotals
            foldEnrichment = simpleChartRecord.foldEnrichment
            bonferroni = simpleChartRecord.bonferroni
            benjamini = simpleChartRecord.benjamini
            FDR = simpleChartRecord.afdr
            rowList = [
                categoryName,
                termName,
                str(listHits),
                str(percent),
                str(ease),
                Genes,
                str(listTotals),
                str(popHits),
                str(popTotals),
                str(foldEnrichment),
                str(bonferroni),
                str(benjamini),
                str(FDR),
            ]
            w.write("\t".join(rowList) + "\n")
        print("Write file to:", output_file)


def cli_model(args):
    parser = argparse.ArgumentParser(description="David Analysis Command Line Tool")

    parser.add_argument("--input_file", required=True, help="输入文件名称")
    parser.add_argument("--auth_email", required=True, help="验证邮箱")
    parser.add_argument(
        "--output_file",
        default="chartReport.csv",
        help="输出文件名称, 默认chartReport.csv",
    )
    parser.add_argument(
        "--identifier",
        default="UNIPROT_ACCESSION",
        help="输入文件中数据的类型, 默认UNIPROT_ACCESSION",
    )
    parser.add_argument("--pvalue", default=0.1, help="设定pvalue值, 默认0.1")
    parser.add_argument("--count", default=2, help="设定最少数量阈值, 默认2")
    parser.add_argument(
        "--category", default="", help="设定需要过滤的category值, 默认不过滤"
    )

    parsed_args = parser.parse_args(args)

    return (
        parsed_args.input_file,
        parsed_args.output_file,
        parsed_args.identifier,
        parsed_args.auth_email,
        parsed_args.pvalue,
        parsed_args.count,
        parsed_args.category,
    )


def main() -> int:
    input_file, output_file, identifier, auth_email, pvalue, count, category = (
        cli_model(sys.argv[1:])
    )
    get_chart_report(
        input_file=input_file,
        identifier=identifier,
        output_file=output_file,
        auth_email=auth_email,
        p_value=pvalue,
        count=count,
        category=category,
    )
    return 0
