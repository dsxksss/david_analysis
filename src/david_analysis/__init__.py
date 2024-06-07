import argparse
from time import sleep
import pandas as pd
import sys
from zeep import Client, exceptions


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
    print(
        f"Read {len(df)} gene IDs from {file_path}"
    )  # Debug: print number of gene IDs read
    return input_ids


def get_chart_report(
    input_file, output_file, auth_email, identifier, p_value, count, category, species
):
    try:
        client = Client(
            "https://david.ncifcrf.gov/webservice/services/DAVIDWebService?wsdl"
        )
        client.service.authenticate(auth_email)
        input_ids = read_file(input_file, identifier)
        print("Input IDs:", input_ids)  # Debug: print input IDs

        client.service.setCategories(category)
        print("Setting categories:", category)  # Debug: print categories

        if identifier == "OFFICIAL_GENE_SYMBOL":
            client.service.setCurrentSpecies(species)
            print("Setting species:", species)  # Debug: print species

        client.service.addList(input_ids, identifier, "david_webservice_added", 0)

        chartReport = client.service.getChartReport(p_value, count)
        
        if not chartReport:
            print("No chart report returned")  # Debug: print if no chart report
            return
        else:
            print(
                f"Chart report has {len(chartReport)} records"
            )

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
    except exceptions.Error as e:
        print("Get chart eeport error:", e)  # Debug: print Zeep error
    except Exception as e:
        print("Unexpected error:", e)  # Debug: print any other unexpected error
        raise Exception("Unexpected error:", e) # Debug: print


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
        default="OFFICIAL_GENE_SYMBOL",
        help="输入文件中数据的类型, 默认OFFICIAL_GENE_SYMBOL",
    )
    parser.add_argument("--pvalue", default=0.1, help="设定pvalue值, 默认0.1")
    parser.add_argument("--count", default=2, help="设定最少数量阈值, 默认2")
    parser.add_argument(
        "--category",
        default="GOTERM_BP_DIRECT,GOTERM_CC_DIRECT,GOTERM_MF_DIRECT,KEGG_PATHWAY",
        help="设定需要过滤的category值(使用,号分割), ''则为all, ,默认只保留 GOTERM_BP_DIRECT, GOTERM_CC_DIRECT, GOTERM_MF_DIRECT, KEGG_PATHWAY",
    )
    parser.add_argument(
        "--species",
        default="9606",
        help="设定需要使用的species值, 只允许使用对应数字ID(使用,号分割), ''则为all, 默认只使用Homo sapiens(9606)",
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
        parsed_args.species,
    )


def main() -> int:
    (
        input_file,
        output_file,
        identifier,
        auth_email,
        pvalue,
        count,
        category,
        species,
    ) = cli_model(sys.argv[1:])
    max_retry = 5
    retry_sleep = 0.5
    current_retry = 0

    while current_retry < max_retry:
        try:
            get_chart_report(
                input_file=input_file,
                identifier=identifier,
                output_file=output_file,
                auth_email=auth_email,
                p_value=pvalue,
                count=count,
                category=category,
                species=species,
            )
            return 0
        except Exception as e:
            print("Connecting failed, retrying...", e)  # Debug: print connection error
            current_retry += 1
            sleep(retry_sleep)

    return 1
