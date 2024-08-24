import os

def extract_filename_and_extension(relative_path):
    # 将相对路径转换为绝对路径
    absolute_path = os.path.abspath(relative_path)
    
    # 检查路径是否指向一个文件
    if os.path.isfile(absolute_path):
        # 提取文件名（包含后缀）
        filename_with_extension = os.path.basename(absolute_path)
        
        # 提取文件名（不包含后缀）
        filename = os.path.splitext(filename_with_extension)[0]
        
        # 提取文件后缀名
        extension = os.path.splitext(filename_with_extension)[1]
        
    else:
        print(f"提供的路径不是一个文件: {relative_path}")
    return filename,extension

# 假设你有一个相对路径
relative_path = './2312.04547.pdf'
extract_filename_and_extension(relative_path)