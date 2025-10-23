import cld3

def detect_language_mix(text,exclude_strings=[]):
    for string in exclude_strings:
        text = re.sub(string, "", text)  
    result = cld3.get_frequent_languages(text, num_langs=3)
    if len(result) <= 1:
        return False, {result[0].language:result[0].proportion}
    languages = {r.language:r.proportion for r in result}
    return True, languages


# Example usage
if __name__ == "__main__":
    # text = "今天我们有一个important的presentation"
    # text = "今天我们有一个重要的演示！"
    # text = "I want to analyze why certain airports in coastal regions appear frequently mentioned near failed or interrupted migration paths shown in bir d tracks while others do not。 Generate distilled comparison chart highlighting airport_towns city above exposure levels对应风向改变、压力气压和湿度等factors影响 scientist taggers recorded将会中断理由:</final_Query>"
    # text = "First identify all explicit mentions of \"Chinese imports\" in Trump rally speeches paired wi thin±5 IS线米 over _vt废quotesthen qualify hon roud many_of these references co-occur_with either\"[东亚胁减压\"M易占関 or 半 concrete quantitative地|reban figure descriptions placed附近相同 passage一份 highlight such combined examples.{后续 calculate总体占比百分比of这种 coincidences relativeсто总数 OF进口相关 comment##_在讲话记录中"
    text = "I need to analyze discussions about mental health support requests mentioned in our counseling dataset stored in JSON format under json_data/, specifically looking for instances where suicide prevention resources were provided. First locate all .json or .jsonl files related to counseling conversations, then scan their content entries highlighting mentions of suicide hotline numbers or crisis intervention guidance."
    text = 'First verify if the "家电销售.xlsx" file contains more than 50 sales entries, then create a ZIP archive named "backup_sales_netflix.zip" containing both the Netflix movies CSV and the家电销售 Excel file, ensuring the ZIP includes both files.'
    text = 'I need to analyze repetitive terms in China student scores datasets first identify 和高频exam subjects appearing over多个成绩tables 随后批量 replace all matched terms 加上annual ranking suffix 在各个成绩单Spreadsheet细胞里面.'
    text = 'Move the "学生成绩表.xlsx" file to a new folder named "academic_records", then check its permissions, and finally calculate the average math score from the "数学" sheet while saving the result to a CSV file in the same directory.'
    text = "Filter the CPU_分段合并.xlsx file to include only rows where the notes column contains '主推型号', save the results to a CSV, then show me the metadata of the new file."
    text = "Analyze the '商品大类' column in the 家电销售.xlsx file to determine which appliance categories have been sold most frequently overall across all stores和create individually labeled lines{for top three stores}显示他们的 monthly total profits过 TABLE TIME'."
    text = "Show me the list of files in the directory where the filtered results are saved after extracting rows from the '创意素材' sheet of '达人数据.xlsx' where the '创意名称' contains '护肝', then save this list to a text file named 'filtered_files_summary.txt'."
    has_mix, langs = detect_language_mix(text)
    print(has_mix)  # True
    print(langs)    # {'zh-cn', 'en'}
