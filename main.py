import pandas as pd
from flask import Flask, render_template
import pyodbc
import numpy as np


cnxn_str = ("Driver={SQL Server};"
            "Server=192.168.1.207,1433;"
            "Database=mldata;"
            "UID=rudra;"
            "PWD=MlIsFun!;"
            "Trusted_Connection=no;")

cnxn = pyodbc.connect(cnxn_str)
cursor=cnxn.cursor()

#From SQL to Pandas DataFrame
#Fetching data from dbo.fTransactions$ , dbo.dProduct$ table of SQL Server

df = pd.read_sql_query('SELECT * FROM dbo.fTransactions$', cnxn)
df_products = pd.read_sql_query('SELECT * FROM dbo.dProduct$', cnxn)
cnxn.close()


#Merging transactions and products table on Products to get Quantity
data=pd.merge(df,df_products,on='Product')
data=data.drop('Date',axis=1) # dropped Date table as not required in report

#Creating New Columns in dataframe
# Calculate Total Sales,Total Revenue, Gross Profit,Product with Highest Gross Profit,Pr with highest revenue
#Total Revenue($)=data['Quantity']*data['RetailPrice']*1-data['RevenueDiscount']
#Total COGS($) =data['Quantity']*data['StandardCost']*data['NetStandardCost']
#GrossProfit($)=data['Total_Revenue']-data['COGS']

data['COGS']=data['Quantity']*data['StandardCost']*data['NetStandardCost']
data['Total_Revenue']=data['Quantity']*data['RetailPrice']*1-data['RevenueDiscount']
data['Profit']=data['Total_Revenue']-data['COGS']


#Creating groups of data based on Products
grouped=data.groupby('Product')

# Getting sum of Total_Revenue,COGS,Profit for each product
Profit_data=grouped['Profit'].agg(np.sum)
Revenue_data=grouped['Total_Revenue'].agg(np.sum)
COGS_data=grouped['COGS'].agg(np.sum)


#Top 5 products in terms of Profit
#Bar chart
Products_top5_profit=Profit_data.sort_values(ascending=False).iloc[0:5]
barprofit_labels=list(Products_top5_profit.keys())
barprofit_values=list(Products_top5_profit.values)


#PIE CHART
#Top 5 Products in terms of No of Transactions

No_of_trans=grouped['Quantity'].agg(np.size).sort_values(ascending=False).iloc[0:5]
pietransaction_labels=list(No_of_trans.keys())
pietransaction_values=list(No_of_trans.values)


#LINE CHART for full data showing
#COGS,,REVENUE
line_labels=list(COGS_data.keys())
linecogs_values=list(COGS_data.values)
linerevenue_values=list(Revenue_data.values)


# DOGNUT CHART for products with highest revenue
top_products_rev=Revenue_data.iloc[0:5]
dognut_labels=list(top_products_rev.keys())
dognut_values=list(top_products_rev.values)


app = Flask(__name__)

@app.route("/")
def home():
    return render_template('index.html',barprofit_labels=barprofit_labels,barprofit_values=barprofit_values,pietransaction_labels=pietransaction_labels,pietransaction_values=pietransaction_values,line_labels=line_labels,linecogs_values=linecogs_values,linerevenue_values=linerevenue_values,dognut_labels=dognut_labels,dognut_values=dognut_values)


if __name__ =='__main__':
    app.run(debug = True)