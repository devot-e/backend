import pandas as pd
import numpy as np
from ctgan import CTGAN
loaded_model = CTGAN.load("model.pkl")
new_data = loaded_model.sample(100)
print(new_data)