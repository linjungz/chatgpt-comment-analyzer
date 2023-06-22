from comment_analyzer import CommentAnalyzer
import pandas as pd
import argparse

#  Parse command line arguments
parser = argparse.ArgumentParser(description='Analyze comments from excel file')
parser.add_argument('--input', type=str, required=True, help='input excel file path')
parser.add_argument('--sheet', type=str, required=False, default="Sheet1", help='sheet name in the input excel file')
parser.add_argument('--output', type=str, required=True, help='output excel file path')
parser.add_argument('--count', type=int, required=False, default=0, help='number of comments to process')
args = parser.parse_args()

# Load the comments from excel to a Dataframe
data = pd.read_excel(args.input, sheet_name=args.sheet)
df = pd.DataFrame(data, columns=['POST ID', '评论内容'])

analyzer = CommentAnalyzer()

# Generate output as dataframe
output_list = []
processed_count = 0
for index, row in df.iterrows():
    result = []
    result.append(row['POST ID'])
    comment = row['评论内容']
    result.append(comment)

    llm_output = analyzer.analyze(
        social_media_channel='小红书',
        company='宝洁',
        product='护舒宝',
        product_description='护舒宝卫生巾产品包括普通卫生巾，液体卫生巾和安睡裤',
        comment=comment,
    )
    if llm_output != None:
        for key, value in llm_output.items():
            result.append(value)
    else:
        result.append("异常")
        # append the rest of the columns with empty string
        for i in range(analyzer.reponse_schema_fiels_count - 1):
            result.append("")
        
    print(result)
    output_list.append(result)
    
    processed_count += 1
    if args.count > 0 and processed_count >= args.count:
        break

output_df = pd.DataFrame(
    output_list,
    columns=['POSTID', 'TOP20评论内容', '情感分析结果', '情感分析理由', '场所', '时间', '使用场景', '产品']
)

output_df.to_excel(args.output, index=False)

