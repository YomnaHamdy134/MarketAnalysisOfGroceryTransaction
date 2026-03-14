import pandas as pd
# import numpy as np
from mlxtend.preprocessing import TransactionEncoder # OR...from mlxtend.preprocessing import OnehotTransactions
from mlxtend.frequent_patterns import apriori, association_rules

def run_market_basket(df):

    df.columns = ['Items']
    items=df['Items'].values

    transactions=[]

    for i in range(0,len(items)):
        transactions.append(items[i].split(','))
    transactions = [[item.strip() for item in t] for t in transactions] # To make sure that there isn't any whitespace
    encoder=TransactionEncoder()
    trans=encoder.fit_transform(transactions)

    encoded_data=pd.DataFrame(trans,columns=encoder.columns_,dtype=int) 

    frequent_itemsets=apriori(encoded_data,min_support=0.1,use_colnames=True)
    frequent_itemsets.sort_values(by = 'support', ascending = False)

    rules=association_rules(frequent_itemsets,metric='confidence',min_threshold=0.3)
    rules.sort_values('confidence',ascending=False)


    return frequent_itemsets, rules