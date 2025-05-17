#if want to test -> Remember to change directory 


import seaborn as sns
import matplotlib.pyplot as plt

sns.histplot([1, 2, 2, 3, 3, 3, 4, 4, 5], bins=5, kde=True, color='blue')

plt.show() 