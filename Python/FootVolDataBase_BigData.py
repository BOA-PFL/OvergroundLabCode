# -*- coding: utf-8 -*-
"""
Created on Tue May 10 11:08:58 2022

@author: Bethany.Kilpatrick
"""

import pandas as pd
import numpy as np 
from tkinter.filedialog import askopenfilename
 


filename = askopenfilename() # Open CMJ file

dat = pd.read_csv(filename, sep='\t', header = 0)