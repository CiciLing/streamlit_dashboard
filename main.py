import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
from pyvis.network import Network
import ast


st.title("Streamlit Dashboard Challenge - Jiaxizi(Cici) Ling")
st.markdown("This dashboard aims to present visualizations and provide insights based on a Github "
            "[Dataset](https://www.kaggle.com/datasets/nikhil25803/github-dataset/) from Kaggle. "
            "The decision to select 'repository_data' dataset was motivated by its extensive nature, "
            "encompassing a larger set of columns. This characteristic enhances the potential for discovering more intriguing "
            "and valuable insights within the dataset")

tab1, tab2, tab3 = st.tabs(['Language Usage', 'Language Correlation','Top Repos'])
with tab1:
    #as the year goes by, trend of language
    # data clean up since there are N/A fields for language
    repo = pd.read_csv("repository_data.csv")
    print(repo.isnull())
    repo_cleaned = repo.dropna()
    # removed 1446340 rows
    print(len(repo_cleaned))

    # Parse 'created_at' to extract the year
    repo_cleaned['year'] = pd.to_datetime(repo_cleaned['created_at']).dt.year

    #create the line graph that tracks language usage over the year
    st.header('Primary Language Usage Over the Years')
    st.markdown('You can choose multiple languages to track and compare their usages over the years. Something to note is that'
                ' this dataset has data ranging from 2009-01-01 to 2023-01-21, so you will likely see a drop in 2023 data.')
    selected_languages = st.multiselect('Select languages:', sorted(repo_cleaned['primary_language'].unique()),default=  ['Python', 'Java'])

    # Filter data for the selected languages
    language_data = repo_cleaned[repo_cleaned['primary_language'].isin(selected_languages)]

    # Group by year and language, and count the number of projects
    projects_per_year_language = language_data.groupby(['year', 'primary_language']).size().unstack().fillna(0)

    # Create a Matplotlib figure and axis
    fig, ax = plt.subplots()

    # Create a line chart
    for language in selected_languages:
        ax.plot(projects_per_year_language.index, projects_per_year_language[language], marker='o', label=language)

    # Customize the plot
    ax.set_title(f'{selected_languages} Usage Over the Years')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Repositories')
    ax.legend()

    # Show the plot in Streamlit
    st.pyplot(fig)

with tab2:
    repo_cleaned['languages_used'] = repo_cleaned['languages_used'].apply(ast.literal_eval)
    st.header('Language Correlation Visualization')
    st.markdown('By selecting a language, you will be able to see the network graph of it with other languages in the selected year. '
                'The weight that is written on the edge indicates how many time they were used together. Edges with weight equal to 1 is filtered out'
                ' for simplicity.')
    # Multiselect widget for selecting a language
    selected_language = st.selectbox('Select a language:', sorted(repo_cleaned['primary_language'].unique()), index= 150)
    selected_year = st.selectbox('Select a year:',sorted(repo_cleaned['year'].unique()), index= 4)
    # Filter data for the selected year and primary language
    filtered_data = repo_cleaned[(repo_cleaned['year'] == selected_year) & (repo_cleaned['primary_language'] == selected_language)]

    G = nx.Graph()
    # Add nodes and edges for each language
    for lang_list in filtered_data['languages_used']:
        for i in range(len(lang_list) - 1):
            lang1, lang2 = lang_list[i], lang_list[i + 1]

            # Add nodes
            if lang1 == selected_language or lang2 == selected_language:
                if not G.has_node(lang1):
                    G.add_node(lang1)
                if not G.has_node(lang2):
                    G.add_node(lang2)

                # Add edge
                if G.has_edge(lang1, lang2):
                    G[lang1][lang2]['weight'] += 1
                else:
                    G.add_edge(lang1, lang2, weight=1)

    # Streamlit app for network graph
    st.subheader('Language Co-occurrence Network Graph')
    # Filter edges with weight greater than 1
    edges_to_remove = [(u, v) for u, v, data in G.edges(data=True) if data['weight'] == 1]
    G.remove_edges_from(edges_to_remove)

    nodes_to_remove = [node for node in G.nodes() if G.degree(node) == 0]
    G.remove_nodes_from(nodes_to_remove)

    # Draw the graph with custom node and edge colors
    pos = nx.kamada_kawai_layout(G)

    fig, ax = plt.subplots()
    ax.set_title(f'{selected_language} relationship graph with other languages in ' f'{selected_year}')

    # Draw nodes
    nx.draw_networkx_nodes(G, pos, ax=ax, node_size=800)
    # Draw edges
    nx.draw_networkx_edges(G, pos,ax=ax)
    # Draw labels
    nx.draw_networkx_labels(G, pos, ax=ax)
    # Draw edge labels
    nx.draw_networkx_edge_labels(G, pos, edge_labels={(u, v): G[u][v]['weight'] for u, v, data in G.edges(data=True)},
                                 ax=ax)
    st.pyplot(fig)

with tab3:
    st.header("Top Repositories based on different metrics")
    st.markdown('You can choose any category to see the top 10 repositories based on '
                'the selected category.')
    option_column = {'Stars Count': 'stars_count',
                     'Forks Count': 'forks_count',
                     'Watchers': 'watchers',
                     'Pull Requests': 'pull_requests',
                     'Commit Count': 'commit_count'}

    option = st.selectbox(
        'Select Category:',
        list(option_column.keys()),
        index=0
    )
    user_color = st.color_picker('Choose a color for the bars:', value='#1f78b4')  # Default: Blue

    # simple bar charts for top stars_count/forks_count/watchers/pull_requests/commit_count
    top_10_repositories = repo.nlargest(10, option_column[option])

    # Plotting the bar chart using Matplotlib for customization
    fig, ax = plt.subplots()
    ax.bar(top_10_repositories['name'], top_10_repositories[option_column[option]], color = user_color)
    ax.set_xticklabels(top_10_repositories['name'], rotation=50, ha='right')  # Adjust rotation angle as needed
    ax.set_title('Top 10 repos based on ' f'{option}')
    ax.set_xlabel('Repo Name')
    ax.set_ylabel(option_column[option])

    # Show the plot in Streamlit
    st.pyplot(fig)
    st.write(top_10_repositories)



