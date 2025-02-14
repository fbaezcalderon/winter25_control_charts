import seaborn as sns
import pandas as pd
import numpy as np
import matplotlib.pyplot as plot

class ControlChart():
    
    def __init__(self,data):
        self.data = data
        self.observations_labels =  [column for column in data.columns if column.startswith('x') and column[1]!='_'  ]
        self.sample_size =  len(self.observations_labels)
        
        pass

    def rule1_validator(self,data,ucl,lcl,kind):
        data['Rule 1'] =  np.nan
        for index, row in data.iterrows():
            if row[kind] > ucl:
                data.loc[index,['Rule 1']] = row[kind]
            elif row[kind] < lcl:
                data.loc[index,['Rule 1']] = row[kind]

        return data
    
    def _calculate_mean(self,kind):
        if kind =='R' or self.sample_size > 1:
            self.data['R']= self.data.loc[:,self.observations_labels].max(axis=1) \
                            -self.data.loc[:,self.observations_labels].min(axis=1)
            variability_mean  =  self.data['R'].mean()

        if kind == 'x_mean':
            self.data['x_mean'] =  self.data.loc[:,self.observations_labels].mean(axis=1)
        
        return variability_mean 

    def  _calculate_centre_lines(self,kind):
        return self.data[kind].mean()
        
    
    def _calculate_limits(self, variability_mean,kind):
        factor_df  = pd.read_csv('factors.csv')
        centre_line =  self._calculate_centre_lines(kind)

        if kind == 'x_mean':
            a2 =  factor_df.loc[factor_df['sample_size']==self.sample_size]['A2'].values[0]
            return centre_line + a2 * variability_mean , centre_line - a2 * variability_mean
                    # x_ba_bar  + a2 * r_bar           ,    x_bar_bar - a2 * r_bar

        if kind == 'R':
            d4 = factor_df.loc[factor_df['sample_size']==self.sample_size]['D4'].values[0]

            d3 = factor_df.loc[factor_df['sample_size']==self.sample_size]['D3'].values[0]

            return d4*variability_mean, d3*variability_mean
                    # d4 * r_bar                  d3 * r_bar




    def _plot_control_chart(self,cl, ucl, lcl, kind):
        g = sns.FacetGrid(self.data, height= 6, aspect=3 )
        g.map(sns.lineplot,'sample_no',kind)  
        g.map(sns.scatterplot,'sample_no',kind)  # oplot data points
        g.refline(y=cl,color='orange',label = 'Centre Line')  # plot centre line
        g.refline(y=ucl,color='green', label = 'Upper control limit')
        g.refline(y=lcl,color='green', label ='Lower control limit ' )
        self.data = self.rule1_validator(self.data,ucl,lcl,kind)
        g.map(sns.scatterplot,'sample_no','Rule 1',color = 'red')
    

    def create_control_chart(self,kind):

        variabiliy_mean = self._calculate_mean(kind)
        centre_line =  self._calculate_centre_lines(kind)
        ucl,lcl = self._calculate_limits(variabiliy_mean,kind)
        g=self._plot_control_chart(centre_line,ucl,lcl,kind)
