#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from datetime import datetime
import matplotlib.pyplot as plt


# In[ ]:

def add_params(df):
    # First drop duplicate and reset the index. 
    df.drop_duplicates(subset="Post Title", inplace=True)
    df = df.reset_index(drop=True)
    
    # Convert Datetime then split seperate columns
    df['Post Datetime'] = pd.to_datetime(df["Post Datetime"])
    df['Post Date'] = df['Post Datetime'].dt.date
    df['Post Time'] = df['Post Datetime'].dt.time
    # Add city code and area code to make Post area code
    df["PostAreaCode"] = df["City Code"] + df["Area Code"]

    lower_neighbor = []
    for area in df["Neighborhood"]:
        neighbor = area.lower()
        lower_neighbor.append(neighbor)
    df["Neighborhood"] = lower_neighbor

    # df = df[["PostAreaCode", 'Post Datetime', 'Post Date', 'Post Time', 'Post Title', 'Post URL', 'Neighborhood', 'Bedroom', 'SQFT', 'Price']]
    
    # Convert Bedroom number strings to Integer then NaN value to 0 assume 0 bedroom is studio appartment. 
    df["Bedroom"] = pd.to_numeric(df["Bedroom"], errors='ignore').astype('Int64')
    df["Bedroom"] = df["Bedroom"].fillna(0)
    
    # Check if word 'furnished' in the title post, if finds it, I put this as furnished suite. 
    # If furnished == 1, not furnished == 0
    search_word = 'furnished'
    furnished = []
    for i in range(len(df)):
        post_title_list = df['Post Title'][i].lower().split(" ")
        if any(word == search_word for word in post_title_list):
            furnished.append(1)
        else:
            furnished.append(0)
    df["IsFurnished"] = furnished
    
    # Calculate Price/SQFT
    df["Price/SQFT"] = df["Price"] / df["SQFT"]
    df['Price/SQFT'].fillna(0, inplace=True)
    df["SQFT"] = df["SQFT"].fillna(0)
    
    # Chnage PostAreaCode to numeric values
    area_coded = pd.Categorical(df["PostAreaCode"]).codes
    df["PostArea_coded"] = area_coded
    
    # Categorize the price range by price/SQFT
    df['price_range'] = pd.cut(df['Price/SQFT'], bins=[-1, 0.5, 3.4, 4.2, 5.8, max(df['Price/SQFT'])+1], labels=[0, 1, 2, 3, 4], include_lowest=False)
    
    # Sort DataFrame by Datetime
    df.sort_values(by="Post Datetime", axis=0, ascending=False, inplace=True)
    
    
    return df[["PostAreaCode", "PostArea_coded", 'City Code', 'Area Code', 'Post Datetime', 'Post Date', 'Post Time', 'Post Title', 'Post URL', 'Neighborhood', 'Bedroom', 'SQFT', 'Price', 'IsFurnished', 'Price/SQFT', 'price_range']]

def subplot_by_cluster(df, i, param='cluster_labels'):
    """
    Plot result by cluster. 
        plot1: Price histgram. 
        plot2: Price/SQFT histgram
        plot3: Number of ads by area 
        plot4: Number of ads by the number of bedrooms
        plot5: Scatter plot Price / SQFT
        plot6: Number of Furnished suite vs not Furnished
    """
    
    cluster = df[df[param] == i]
    plt.rcParams.update({"figure.figsize": (10, 10), "figure.dpi": 120})
    print(f'{param}: {i}\nLength of DataFrame: {len(cluster)}')
    fig, axs = plt.subplots(3, 2)

    # Plot Price histgram
    axs[0, 0].hist(cluster['Price'], bins=50)
    axs[0, 0].set_title(f"Price on cluster {i}", fontsize=16)
    axs[0, 0].set_xlabel("Price", fontsize=14)
    axs[0, 0].set_ylabel("Number of Lisitng", fontsize=14)

    # Plot Price/SQFT histgram
    axs[0, 1].hist(cluster['Price/SQFT'], bins=50)
    axs[0, 1].set_title(f"Price/SQFT on cluster {i}", fontsize=16)
    axs[0, 1].set_xlabel("Price/SQFT", fontsize=14)
    axs[0, 1].set_ylabel("Number of Lisitng", fontsize=14)

    # Plot Area to number of ads
    by_area = cluster["PostAreaCode"].value_counts().sort_values(ascending=True)
    axs[1, 0].barh(by_area.index, by_area.values)
    axs[1, 0].set_title(f"By Area cluster {i}", fontsize=16)
    axs[1, 0].set_xlabel("Number of ads", fontsize=14)
    axs[1, 0].set_ylabel("Area Name", fontsize=14)

    # Plot Number of Bedroom per ads
    bedroom = cluster['Bedroom'].value_counts().sort_values(ascending=True)
    axs[1, 1].barh(bedroom.index, bedroom.values)
    axs[1, 1].set_title(f"Number of Bedroom on cluster {i}", fontsize=16)
    axs[1, 1].set_xlabel("Number of Ads", fontsize=14)
    axs[1, 1].set_ylabel("Number of Bedrooms", fontsize=14)

    # Plot Price/SQFT scatterplot
    axs[2, 0].scatter(x=cluster["Price"], y=cluster['SQFT'])
    axs[2, 0].set_title(f"Price / SQFT cluster {i}", fontsize=16)
    axs[2, 0].set_xlabel("Price", fontsize=14)
    axs[2, 0].set_ylabel("SQFT", fontsize=14)

    # Plot furnished or not
    furnished = cluster["IsFurnished"].value_counts().sort_values(ascending=False)
    axs[2, 1].bar(['0', '1'], furnished.values)
    axs[2, 1].set_title(f"Furnished or not cluster {i}", fontsize=16)
    axs[2, 1].set_xlabel("Furnished/not Furnished", fontsize=14)
    axs[2, 1].set_ylabel("Number of ads", fontsize=14)

    fig.tight_layout()
    plt.show()
    
def remove_outliers(df):
    # lower-end of outliers
    one_dollar = df[df["Price"] == 1]
    zero_dollar = df[df["Price"] == 0]
    
    # Higher-end of outliers
    high_prices = df[df["Price"] > 100_000]
    # Drop low-end outliers rows
    drop_index = []
    for idx in one_dollar.index:
        drop_index.append(idx)
    for idx in zero_dollar.index:
        drop_index.append(idx)
    for idx in high_prices.index:
        drop_index.append(idx)
    print(f"Original DataFrame Size:{len(df)}\nNumber of Dropped Rows: {len(drop_index)}")
    df.drop(drop_index,axis=0, inplace=True)
    print(f"DataFrame size after drop rows: {len(df)}")
    
    
    
    return df

