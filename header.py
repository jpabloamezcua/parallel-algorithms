# header used for basically every plot
from matplotlib import pyplot as plt
import matplotlib.colors as mcolors
import matplotlib.patches as mpatches
import matplotlib.lines as mlines
import matplotlib.ticker as mtick
import numpy as np
import pandas as pd
import seaborn as sns
from scipy.optimize import curve_fit
import mplcursors
import math
import bisect
import copy
import warnings
from colour import Color
from matplotlib.collections import QuadMesh
from matplotlib.patches import Ellipse
from matplotlib.patches import Rectangle
from matplotlib.text import OffsetFrom
from matplotlib.ticker import MaxNLocator
from IPython.display import display, Math, Markdown
from math import log10, floor
from operator import itemgetter
import json
import decimal
import numbers
from src.huge_num import Huge, log
import matplotx


from src.standard_codes import *
from src.processed_data import *
from src.helper_functions import *


plt.style.use('default')

CUR_YEAR=2024
MAIN_MODEL = 330 # MIMD-TC CRCW

all_colors = ['', '#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff', '#00ffff',
                '#777777',
              '#7700ff', '#0077ff', '#00ff77', '#777700', '#77ff77', '#ff7777', '#000000']

COLORS = list(mcolors.TABLEAU_COLORS.values())

PROCESSOR_COLORS = ['#3cb44b','#ffe119','#a9a9a9'] # green, yellow, grey
# MODEL_COLORS = ['#ff0000', '#00ff00', '#0000ff', '#ffff00', '#ff00ff',
#                 '#00ffff', '#777777', '#7700ff', '#469990']
SEQ_PAR_COLORS = ['#F5C8AF','#58D68D']

#blue
ALGO_COLORS = ["#AEDBFF", "#369BFF", "#6FBFFF"]
ALGO_LINE_COLOR ="#0A2A4F"
#red
# ALGO_COLORS = ["#FFC1C1", "#E63946", "#FF6B6B"]
# ALGO_LINE_COLOR ="#4B0A0A"

n_COLORS = ['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray', 'tab:olive', 'tab:cyan']

COLORS_GRADIENT = ['#88CCEE', '#6BAEDC', '#4E94C6', '#3970A5', '#2B5580']
WORK_EFF_COLORS =["#4477AA", "#88CCEE", "#FDB863", "#D55E00"]

MODEL_COLORS = {
    100: '#0000ff', # 130
    110: '#ff0000',
    120: '#00ff00',
    130: '#0000ff',
    131: '#0000ff', # 130
    132: '#0000ff', # 130
    133: '#0000ff', # 130
    135: '#0000ff', # 130
    200: '#ffff00',
    210: '#ffff00', # 200
    220: '#ffff00', # 200
    300: '#ff00ff',
    310: '#ff00ff', #300
    320: '#ff00ff', #300
    330: '#ff00ff', #300
    400: '#00ffff',
    500: '#777777',
    510: '#777777', #500
    520: '#777777', #500
    600: '#7700ff',
    610: '#7700ff', #600
    700: '#469990',
    800: '#dcbeff'}

# all PRAMs, MIMDs, and SIMDs
PRAM_LIKE_MODELS = {100, 110, 120, 130, 131, 132, 133, 135, 200, 210, 220,
                    300, 310, 320, 330}


# SAVE_LOC = "Plots/PostFeedback/"
#SAVE_LOC = "Plots/Feb18 data/"
# SAVE_LOC = "Plots/Mar9 data/"
#SAVE_LOC = "Plots/May1 data/"
SAVE_LOC = "Plots/Jul21 data/"
