import pandas as pd
import numpy as np

from sklearn.decomposition import PCA
from sklearn import preprocessing
import statsmodels.api as sm
from statsmodels.formula.api import ols


import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
from plotly.subplots import make_subplots


from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.inspection import permutation_importance


class Answer():
    """ 
    Takes in appropriate dataframe of analysis inputs, made from code like this: 

    sing_df = pd.read_excel("sheets/land_use_constrained_data.xlsx", sheet_name=1, header=5, usecols="B:V", nrows=9)

    sf_df = pd.read_excel("sheets/land_use_constrained_data.xlsx", sheet_name=1, header=55, usecols="B:V", nrows=11)
    
    """
    def __init__(self, dataframe, shift=15):
        self.df = dataframe.dropna(axis=1)

        # seperate dataframe 
        self.landuse = self.df.iloc[:, 2:8]
        self.dists = self.df.iloc[:, 8:12]
        self.costs = self.df.iloc[:, 12:shift]
        self.qol = self.df.iloc[:, shift:]

    
    def get_pca_vals(self, df, name):
        scaled_df  = preprocessing.scale(df)
        pca = PCA()
        pca.fit(scaled_df)

        pca_data = pca.transform(scaled_df)

        #The following code constructs the Scree plot
        per_var = np.round(pca.explained_variance_ratio_* 100, decimals=1)
        short_labels = ['PC' + str(x) for x in range(1, len(per_var)+1)]
        labels = [name + '_PC' + str(x) for x in range(1, len(per_var)+1)]
        
        fig, (ax0, ax) = plt.subplots(nrows=1, ncols=2, figsize=[10,3])
        ax0.bar(x=range(1,len(per_var)+1), height=per_var, tick_label=short_labels)
        ax0.set_ylabel('Percentage of Explained Variance')
        ax0.set_xlabel('Principal Component')
        ax0.set_title('Scree Plot')
        # plt.close()


        pca_df = pd.DataFrame(pca_data, columns=labels)

        # plot_fig, ax = plt.subplots()
    
        ax.scatter(pca_df[f"{name}_PC1"], pca_df[f"{name}_PC2"])
        ax.set_title('PCA Graph')
        ax.set_xlabel('PC1 - {0}%'.format(per_var[0]))
        ax.set_ylabel('PC2 - {0}%'.format(per_var[1]))
        
        for sample in pca_df.index:
            ax.annotate(sample, (pca_df[f"{name}_PC1"].loc[sample], pca_df[f"{name}_PC2"].loc[sample]))
        
        plt.close()

        return pca_df, fig



    def create_pca_df(self, sig=[2,2,1,1]):
        # PCA 
        # TODO => selections may change!
        df0, f0 = self.get_pca_vals(self.landuse, name="landuse")
        self.landuse_pca = df0.iloc[:, 0:sig[0]]

        df1, f1 = self.get_pca_vals(self.dists, "dists")
        self.dists_pca = df1.iloc[:, 0:sig[1]]

        df2, f2 = self.get_pca_vals(self.costs, "costs")
        self.costs_pca = df2.iloc[:, 0:sig[2]]

        df3, f3 = self.get_pca_vals(self.qol, "qol")
        self.qol_pca = df3.iloc[:, 0:sig[3]]

        self.pca_df = pd.concat([self.landuse_pca, self.dists_pca, self.costs_pca, self.qol_pca], axis=1,)

        self.pca_figs = [f0, f1, f2, f3]

    
    def analyze_pca_corr(self):
        self.corr_map = sns.heatmap(self.pca_df.corr(), annot=True, center=0)


    def create_sig_pca_df(self, col_ix=[0,3,4,5]):
        self.sig_pca_df = self.pca_df.iloc[:, col_ix]
        self.pairplot = sns.pairplot(self.sig_pca_df , height=1, aspect =2)


    def rf_r2(self, y, X, columns=[]):
        if len(columns) == 0:
            columns = X.columns
            
        X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42)
        forest = RandomForestRegressor(random_state=1)
        forest.fit(X_train, y_train)

        # alt way to calc
        result = permutation_importance(
        forest, X_test, y_test, n_repeats=10, random_state=42, n_jobs=2
        )
        
        forest_importances = pd.Series(result.importances_mean, index=columns)


        fig, ax = plt.subplots()
        forest_importances.plot.bar(yerr=result.importances_std, ax=ax)
        ax.set_title("Feature importances using permutation on full model")
        ax.set_ylabel("Mean accuracy decrease")
        fig.tight_layout()
        plt.close()

        r2 = forest.score(X_test, y_test)
        # y_test_pred = forest.predict(X_test)
        # r2 = r2_score(y_test, y_test_pred)

        return r2, fig 
    

    def run_rf(self):
        r2s = []
        figs = []

        # whole df analysis 
        y_orig = self.qol
        y = preprocessing.scale(y_orig)
        X_orig = pd.concat([self.landuse, self.dists, self.costs], axis=1)
        X = preprocessing.scale(X_orig)

        r2, fig = self.rf_r2(y, X, X_orig.columns)
        r2s.append(r2)
        figs.append(fig)


        # non-filtered pca  
        y = self.pca_df["qol_PC1"]
        X = self.pca_df.iloc[:, 0:-1]
        r2, fig = self.rf_r2(y, X)
        r2s.append(r2)
        figs.append(fig)


        # filtered pca
        y = self.sig_pca_df["qol_PC1"]
        X = self.sig_pca_df.iloc[:, 0:3]
        r2, fig = self.rf_r2(y, X)
        r2s.append(r2)
        figs.append(fig)

        self.r2s = r2s
        self.rf_figs = figs 






