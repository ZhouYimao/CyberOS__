import cv2
from paddleocr import PaddleOCR
import numpy as np
import networkx as nx

# 初始化 PaddleOCR
ocr = PaddleOCR(use_angle_cls=True, lang='ch', show_log=False)

# 加载思维导图图像
img_path = '../test_file/mine/thinkAny.webp'
image = cv2.imread(img_path)

# 检查图像是否成功加载
if image is None:
    raise FileNotFoundError(f"无法加载图像，请检查路径：{img_path}")

# 转换为灰度图像
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# 使用形态学操作去除线条和框框
kernel = np.ones((5, 5), np.uint8)
dilated = cv2.dilate(gray, kernel, iterations=1)
eroded = cv2.erode(dilated, kernel, iterations=1)

# 使用连通组件分析来检测文本区域
_, binary = cv2.threshold(eroded, 128, 255, cv2.THRESH_BINARY_INV)
num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary, connectivity=8)

# 用于存储节点
nodes = []

# 遍历每个连通组件
for i in range(1, num_labels):  # 从 1 开始，跳过背景
    x, y, w, h, area = stats[i]
    roi = image[y:y + h, x:x + w]
    result = ocr.ocr(roi, cls=True)  # OCR 识别

    # 检查 OCR 结果是否有效
    if result and len(result) > 0 and result[0]:
        text = " ".join([line[1][0] for line in result[0] if line])
        nodes.append((text, (x, y, w, h)))  # 添加节点
        print(f"识别的文本：{text}")

# 构建图结构
G = nx.DiGraph()
for node in nodes:
    G.add_node(node[0])

# 输出节点及其层次结构
print("节点:", G.nodes())
