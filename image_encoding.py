
# 建立 image_encoding.py → Z碼圖編碼模組

import numpy as np
import math

from PIL import Image
from binary_operations import int_to_binary, binary_to_int

def z_to_image(z_bits):
  """
  功能:
    將 Z 碼位元列表編碼成灰階圖片
  """
  num_bits = len(z_bits)
  num_pixels = math.ceil(num_bits / 8)

  if num_bits % 8 != 0:
    padding = 8 - (num_bits % 8)
    z_bits = z_bits + [0] * padding
  
  pixels = []
  for i in range(0, len(z_bits), 8):
    byte = z_bits[i:i+8]
    pixel_value = binary_to_int(byte)
    pixels.append(pixel_value)
  
  width = int(math.sqrt(num_pixels))
  height = math.ceil(num_pixels / width)
  
  while len(pixels) < width * height:
    pixels.append(0)
  
  pixel_array = np.array(pixels, dtype=np.uint8)
  pixel_array = pixel_array[:width * height].reshape(height, width)
  
  image = Image.fromarray(pixel_array, mode='L')
  
  return image

def image_to_z(image, original_bit_length=None):
  """
  功能:
    從灰階圖片解碼 Z 碼位元列表
  """
  pixel_array = np.array(image)
  pixels = pixel_array.flatten()
  
  z_bits = []
  for pixel in pixels:
    binary = int_to_binary(pixel, 8)
    z_bits.extend(binary)
  
  if original_bit_length is not None:
    z_bits = z_bits[:original_bit_length]
  
  return z_bits

def decide_msb_bits(secret size,block capacity):
  """
  secret size :機密資訊位元數
  block capacity : 每個block的最大容量
  """
  num block = math.ceil(secret size/block capacity)

  """
  判斷式
  """
  if secret size < block capacity *1:
    return [7]
  elif secret_size < block_capacity * 2:
    return [6, 7]  # 使用兩個 MSB
  elif secret_size < block_capacity * 3:
    return [5, 6, 7]  # 使用三個 MSB
  elif secret_size < block_capacity * 4:
    return [4, 5, 6, 7]  # 使用四個 MSB
  elif secret_size < block_capacity * 5:
    return [3, 4, 5, 6, 7] # 使用五個 MSB
  elif secret_size < block_capacity * 6:
    return [2, 3, 4, 5, 6, 7] # 使用六個 MSB
  elif secret_size < block_capacity * 7:
    return [1, 2, 3, 4, 5, 6, 7] # 使用七個 MSB
  else:
    return [0, 1, 2, 3, 4, 5, 6, 7] # 使用八個 MSB

def decide_msb_bits_dyanamic(secret_size, cover_image_shape):
  height, width = cover_image_shape
  num_pixels = height * width

  max_capacity = num_pixels *8
  if secret_size > max_capacity:
    rasie ValueError("Secret data too big! over the size.)

  avg_bits_needed = math ceil(secret_size/(height*width))

  num_msb = min(max(avg_bits_needed, 1),8)

  msb_bits = list(range(8 - num_msb,8))

  return msb_bits, avg_bits_needed
