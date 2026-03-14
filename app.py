import streamlit as st
import pandas as pd
import numpy as np
from analysis_app import run_market_basket
import matplotlib.pyplot as plt
import arabic_reshaper
from bidi.algorithm import get_display
import networkx as nx


st.title("Market Basket Analysis")


uploaded_file = st.file_uploader("Upload .csv or .xlsx file", type=["csv", "xlsx"])


if uploaded_file:    
# To determine the type of file
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    elif uploaded_file.name.endswith('.xlsx'):
        df = pd.read_excel(uploaded_file)

    frequent_itemsets, rules = run_market_basket(df)

    st.subheader("Association Rules")
    n_rows=st.slider('Choose Number Of Rows to display:',min_value=5,max_value=len(rules),step=1)
    columns_to_show=st.multiselect("Select Columns to show",rules.columns.tolist(),default=rules.columns.tolist())
    numerical_columns=rules.select_dtypes(include=np.number).columns.tolist()

    st.write(rules[:n_rows][columns_to_show])

    frequent_itemsets['length'] = frequent_itemsets['itemsets'].apply(lambda x: len(x))
    single_items = frequent_itemsets[frequent_itemsets['length'] == 1]
    top_items = single_items.sort_values(by='support', ascending=True)

    labels = top_items['itemsets'].astype(str)

    arabic_labels = [
        get_display(arabic_reshaper.reshape(label))
        for label in labels
    ]

    tab1,tab2,tab3,tab4,tab5,tab6=st.tabs(['Bar Plot','Network Diagram','Scatter Plot',"Bubble Plot",'Histogram','Heatmap'])

# Bar Plot
    with tab1:
        st.subheader("Top Frequent Items")
        fig, ax = plt.subplots(figsize=(8,6))
        ax.barh(arabic_labels, top_items['support'], color='skyblue')
        ax.set_xlabel("Support")
        ax.set_ylabel("Items")
        ax.set_title("Top Frequent Items")
        st.pyplot(fig)  

# Network
    with tab2:
        def fix_arabic(text):
            return get_display(arabic_reshaper.reshape(text))

        strong_rules = rules[(rules['lift'] > 1.2) &
            (rules['confidence'] > 0.4)]

        G = nx.DiGraph()

        for _, row in strong_rules.iterrows():
            
            antecedent = list(row['antecedents'])[0]
            consequent = list(row['consequents'])[0]
            
            G.add_edge(
                fix_arabic(antecedent),
                fix_arabic(consequent)
            )

        st.subheader("Association Rules Network Graph")

        fig2, ax2 = plt.subplots(figsize=(8,6))
        pos = nx.spring_layout(G)
        nx.draw(
            G,
            pos,
            with_labels=True,
            node_size=3000,
            node_color="lightblue",
            font_size=10,
            font_weight="bold",
            ax=ax2
        )
        ax2.set_title("Association Rules Network Graph")
        st.pyplot(fig2)
# Scatter Plot
    with tab3:
        col1,col2,col3=st.columns(3)
        with col1:
            x_column=st.selectbox("Choose X Column",numerical_columns)
        with col2:
            y_column=st.selectbox("Choose Y Column",numerical_columns)
        st.subheader("Association Rules Strength")

        fig, ax = plt.subplots(figsize=(7,5))

        ax.scatter(
            rules[x_column],
            rules[y_column],
        )

        ax.set_xlabel(x_column)
        ax.set_ylabel(y_column)
        ax.set_title("Association Rules Strength")

        st.pyplot(fig)
#Bubble Plot
    with tab4:
        st.subheader("Association Rules Bubble Chart")

        fig, ax = plt.subplots(figsize=(7,5))

        scatter = ax.scatter(
            rules['confidence'],
            rules['lift'],
            s=rules['support'] * 2000,   # حجم الفقاعة
            alpha=0.6
        )

        ax.set_xlabel("Confidence")
        ax.set_ylabel("Lift")
        ax.set_title("Bubble Chart of Association Rules By Support")

        st.pyplot(fig)
#Histogram
    with tab5:
        hist_feature=st.selectbox('Select Feature to histogram',numerical_columns)
        st.subheader(f"{hist_feature} Distribution")      
        fig, ax = plt.subplots(figsize=(7,5))

        ax.hist(
            rules[hist_feature],
            bins=10
        )

        ax.set_xlabel(hist_feature)
        ax.set_ylabel("Frequency")
        ax.set_title(f"Histogram of {hist_feature}")

        st.pyplot(fig)
#HeatMap
    with tab6:        
        rules['antecedents'] = rules['antecedents'].apply(lambda x: list(x)[0])
        rules['consequents'] = rules['consequents'].apply(lambda x: list(x)[0])
        pivot = rules.pivot_table(
            index='antecedents',
            columns='consequents',
            values='confidence'
        )

        pivot.index = pivot.index.map(fix_arabic)
        pivot.columns = pivot.columns.map(fix_arabic)

        fig, ax = plt.subplots(figsize=(8,6))

        heatmap = ax.imshow(pivot, cmap="YlGnBu")

        ax.set_xticks(np.arange(len(pivot.columns)))
        ax.set_yticks(np.arange(len(pivot.index)))

        ax.set_xticklabels(pivot.columns)
        ax.set_yticklabels(pivot.index)

        plt.setp(ax.get_xticklabels(), rotation=45)

        ax.set_title("Association Rules Heatmap")

        fig.colorbar(heatmap)

        st.pyplot(fig)
