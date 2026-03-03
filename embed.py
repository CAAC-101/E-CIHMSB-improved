# embed.py → 嵌入模組（支援文字和圖片，含對象密鑰）

import numpy as np

from config import Q_LENGTH, TOTAL_AVERAGES_PER_UNIT, BLOCK_SIZE, calculate_capacity
from permutation import generate_Q_from_block, apply_Q_three_rounds
from image_processing import calculate_hierarchical_averages
from binary_operations import get_msbs
from mapping import map_to_z
from secret_encoding import text_to_binary, image_to_binary

def embed_secret(cover_image, secret, secret_type='text', contact_key=None):
    """
    功能:
        將機密內容嵌入無載體圖片，產生 Z 碼
    
    參數:
        cover_image: numpy array，灰階圖片 (H×W) 或彩色圖片 (H×W×3)
        secret: 機密內容（字串或 PIL Image）
        secret_type: 'text' 或 'image'
        contact_key: 對象專屬密鑰（字串），用於加密
    
    返回:
        z_bits: Z 碼位元列表
        capacity: 圖片的總容量
        info: 額外資訊（機密內容的相關資訊）
    
    流程:
        1. 圖片預處理（彩色轉灰階、檢查尺寸）
        2. 計算容量並檢查
        3. 對每個 8×8 區塊進行嵌入（使用 contact_key 生成 Q）
    
    格式:
        [1 bit 類型標記] + [機密內容]
        類型標記: 0 = 文字, 1 = 圖片
    """
    cover_image = np.array(cover_image)
    
    # ========== 步驟 1：圖片預處理 ==========
    # 1.1 若為彩色圖片，轉成灰階
    if len(cover_image.shape) == 3:
        cover_image = (
            0.299 * cover_image[:, :, 0] + 
            0.587 * cover_image[:, :, 1] + 
            0.114 * cover_image[:, :, 2]
        ).astype(np.uint8)
    
    height, width = cover_image.shape
    
    # 1.2 檢查圖片大小是否為 8 的倍數
    if height % 8 != 0 or width % 8 != 0:
        raise ValueError(f"圖片大小必須是 8 的倍數！當前大小: {width}×{height}")
    
    # ========== 步驟 2：計算容量並檢查 ==========
   # 1. 計算機密內容總位元數
    if secret_type == 'text':
        type_marker = [0]
        content_bits = text_to_binary(secret)
    else:
        type_marker = [1]
        # 注意：此處需先暫定最大容量來轉換圖片，或預先計算圖片二進位長度
        content_bits, orig_size, mode = image_to_binary(secret, (num_units * 21 * 7) - 1)
    
    secret_bits = type_marker + content_bits
    total_needed = len(secret_bits)
    
    # 2. 決定每個平均值需要嵌入幾個位元 (bpa: bits per average)
    # 每個 8x8 區塊有 21 個平均值
    total_averages = num_units * TOTAL_AVERAGES_PER_UNIT
    bpa = (total_needed + total_averages - 1) // total_averages # 無條件進位
    
    if bpa > 7:
        raise ValueError(f"機密內容太大！即使每個像素嵌入 7 bits 仍不足。請更換更大的圖片。")
    if bpa < 1: bpa = 1
    
    print(f"動態容量調整：每個平均值將嵌入 {bpa} 個位元")

    # 3. 嵌入過程
    z_bits = []
    secret_bit_index = 0
    
    for i in range(num_rows):
        for j in range(num_cols):
            # ... (提取 block, 生成 Q, 計算 averages_21, 排列 reordered_averages) ...
            
            # 遍歷該區塊的 21 個平均值
            for avg_val in reordered_averages:
                # 根據計算出的 bpa，從該平均值提取對應數量的位元
                # 例如 bpa=2，則取 MSB(第1位) 和 第2位
                for bit_pos in range(bpa):
                    if secret_bit_index < len(secret_bits):
                        m_bit = secret_bits[secret_bit_index]
                        
                        # 提取平均值的第 (bit_pos + 1) 個位元 (從 MSB 開始算)
                        # 例如 bit_pos=0 是 MSB (128), bit_pos=1 是 64...
                        shift = 7 - bit_pos
                        current_avg_bit = (avg_val >> shift) & 1
                        
                        # 使用現有的映射函數
                        z_bit = map_to_z(m_bit, current_avg_bit)
                        z_bits.append(z_bit)
                        secret_bit_index += 1
    
    # 注意：接收方也需要知道 bpa 才能解碼，建議將 bpa 資訊放入 header 或約定好
    return z_bits, total_averages * bpa, info
