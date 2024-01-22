import os
import re

def renameall():
   fileList = os.listdir('.')
   currentPath = os.getcwd()
   for file_name in fileList:
      pat = "[0-9]+"
      pattern = re.findall(pat, file_name)
      os.rename(file_name, "dpc_qft" + "_" + pattern[0].zfill(2) + ".qasm")

renameall()