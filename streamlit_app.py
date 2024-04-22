import streamlit as st
import altair as alt
import pandas as pd
from vega_datasets import data
import warnings

# Ignore all warnings
warnings.filterwarnings('ignore')
countries = alt.topo_feature(data.world_110m.url, 'countries')

# to plot your own data, replace data.csv and further down,
# rename "fantasy_value" by something descriptive for your data
values = pd.read_csv("burden-disease-from-each-mental-illness.csv")

# Assuming your DataFrame is named df_country_with_id
# You can rename the columns and replace 'country-code' with 'id' using the following code:

values.rename(columns={
    'Entity': 'name',
    'Code': 'alpha-3',
    'DALYs from depressive disorders per 100,000 people in, both sexes aged age-standardized': 'Depressive',
    'DALYs from schizophrenia per 100,000 people in, both sexes aged age-standardized': 'Schizophrenia',
    'DALYs from bipolar disorder per 100,000 people in, both sexes aged age-standardized': 'Bipolar_Disorder',
    'DALYs from eating disorders per 100,000 people in, both sexes aged age-standardized': 'Eating_Disorders',
    'DALYs from anxiety disorders per 100,000 people in, both sexes aged age-standardized': 'Anxiety_Disorders',
}, inplace=True)
values_all_years = values
# values = values[values['Year'] == 2019]
quantitative_columns = ['alpha-3','Depressive', 'Schizophrenia', 'Bipolar_Disorder', 'Eating_Disorders', 'Anxiety_Disorders']
values.dropna(subset=quantitative_columns, inplace=True)


# Enable Panel extensions
alt.data_transformers.disable_max_rows()
countries = alt.topo_feature(data.world_110m.url, "countries")
    # https://en.wikipedia.org/wiki/ISO_3166-1_numeric    
country_codes = pd.read_csv(
    "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"
)

# Define a function to create and return a plot

def create_plot(values, subgroup, year=2019):
    values_tmp = values[values['Year'] == year]
    # Apply any required transformations to the data in pandas
    background = alt.Chart(countries).mark_geoshape(fill="lightgray")

    # we transform twice, first from "ISO 3166-1 numeric" to name, then from name to value
    selection = alt.selection_point(fields=["name"], empty="none")
    opacity_condition = alt.condition(selection, 
                                alt.value(1), 
                                alt.value(0.85))
    stroke_condition = alt.condition(selection,
                                    alt.value("black"),
                                    alt.value("white"))
    stroke_width_condition = alt.condition(selection,
                                    alt.value(1.5),
                                    alt.value(0.1))

    foreground = (
        alt.Chart(countries)
        .mark_geoshape()
        .transform_lookup(
            lookup="id",
            from_=alt.LookupData(data=country_codes, key="country-code", fields=["alpha-3"]),
        )
        .transform_lookup(
            lookup="alpha-3",
            from_=alt.LookupData(data=values_tmp, key="alpha-3", fields=["name",f"{subgroup}"]),
        )
        .encode(
            fill=alt.Color(
                f"{subgroup}:Q",
                scale=alt.Scale(scheme="reds"),  # adjust the domain as needed
            ),
            stroke=stroke_condition,
            strokeWidth=stroke_width_condition,
            tooltip=["name:N", f"{subgroup}:Q"],
            opacity=opacity_condition,
        )
    ).properties(
        title=f"{subgroup} per 100,000 people in Year {year}"
    )

    chart = (
        (background + foreground)
        .properties(width=600, height=600)
        .project(
            type="mercator"
        ).add_params(
            selection
        )
    ).properties(
        width = 400,
    )

    pop_bar_chart = (
        alt.Chart(
            values_tmp.nlargest(10, subgroup)
        ).mark_bar().encode(
            x=alt.X(f"{subgroup}:Q", title=f'{subgroup} per 100,000 people'),
            y=alt.Y("name:N", sort='-x', title='Name'),
            color=alt.Color(f"{subgroup}:Q",scale=alt.Scale(scheme="reds"),legend=None),
            opacity=opacity_condition,
            tooltip=["name:N", f"{subgroup}:Q"],
        ).add_selection(
            selection
        ).properties(
            title=f"Top 10 countries by {subgroup} in Year {year}"
        )
    ).properties(
        width = 200,
        height = 200
    )

    global_trend = (
        alt.Chart(values_all_years)
        .mark_line()
        .encode(
            x=alt.X("Year:O", title='Year'),
            y=alt.Y(f"mean({subgroup}):Q", title=f'Average {subgroup} per 100,000 people'),
            color=alt.value('lightgrey'),  # Use a neutral color like grey for the global line
        )
        .properties(
            title=f"Global and Country-Specific {subgroup} Trend"
        )
    )

    country_trend = (
        alt.Chart(values_all_years)
        .mark_line()
        .encode(
            x=alt.X("Year:O", title='Year'),
            y=alt.Y(f"{subgroup}:Q"),
            color=alt.Color("name:N", scale=alt.Scale(scheme="reds"),legend=None),
            opacity=alt.condition(selection, alt.value(1), alt.value(0))  # Link the selection to the line chart
        )
        .transform_filter(
            selection  # Filter based on the selected country
        )
        .properties(
            title=f"Country-Specific {subgroup} and Trend per 100,000 people"
        )
    )

    line_plot = alt.layer(global_trend, country_trend).add_selection(
        selection
    ).properties(
        width = 200,
        height = 150
    )

    final_visualization = chart | (pop_bar_chart & line_plot)
    final_visualization = final_visualization.configure_title(fontSize=16).configure_legend(titleFontSize=11, labelFontSize=11)
    return final_visualization
    
if __name__ == '__main__':
    st.markdown(
    f"""
    <style>
        .reportview-container .main .block-container{{
            margin-left: {1}rem;
            max-width: {1800}px;
            padding-top: {1}rem;
            padding-right: {1}rem;
            padding-left: {1}rem;
            padding-bottom: {1}rem;
        }}
        .reportview-container .main {{
            color: white;
            background-color: black;
        }}
    </style>
    """
    ,unsafe_allow_html=True,
    )
    warnings.filterwarnings('ignore')
    countries = alt.topo_feature(data.world_110m.url, 'countries')

    # to plot your own data, replace data.csv and further down,
    # rename "fantasy_value" by something descriptive for your data
    values = pd.read_csv("burden-disease-from-each-mental-illness.csv")

    # Assuming your DataFrame is named df_country_with_id
    # You can rename the columns and replace 'country-code' with 'id' using the following code:

    values.rename(columns={
        'Entity': 'name',
        'Code': 'alpha-3',
        'DALYs from depressive disorders per 100,000 people in, both sexes aged age-standardized': 'Depressive',
        'DALYs from schizophrenia per 100,000 people in, both sexes aged age-standardized': 'Schizophrenia',
        'DALYs from bipolar disorder per 100,000 people in, both sexes aged age-standardized': 'Bipolar_Disorder',
        'DALYs from eating disorders per 100,000 people in, both sexes aged age-standardized': 'Eating_Disorders',
        'DALYs from anxiety disorders per 100,000 people in, both sexes aged age-standardized': 'Anxiety_Disorders',
    }, inplace=True)
    values_all_years = values
    quantitative_columns = ['alpha-3','Depressive', 'Schizophrenia', 'Bipolar_Disorder', 'Eating_Disorders', 'Anxiety_Disorders']
    values.dropna(subset=quantitative_columns, inplace=True)


    # Enable Panel extensions
    alt.data_transformers.disable_max_rows()
    countries = alt.topo_feature(data.world_110m.url, "countries")
        # https://en.wikipedia.org/wiki/ISO_3166-1_numeric    
    country_codes = pd.read_csv(
        "https://raw.githubusercontent.com/lukes/ISO-3166-Countries-with-Regional-Codes/master/all/all.csv"
    )
    st.title('Disease Explorer')
    subgroup_choice = st.sidebar.selectbox("Select the disease you would like to explore:", ['Depressive', 'Schizophrenia', 'Bipolar_Disorder', 'Eating_Disorders', 'Anxiety_Disorders'])
    year_choice = st.sidebar.selectbox("Select the year you would like to explore:", [2019, 2018, 2017, 2016, 2015, 2014, 2013, 2012, 2011, 2010, 2009, 2008, 2007, 2006, 2005, 2004, 2003, 2002, 2001, 2000, 1999, 1998, 1997, 1996, 1995, 1994, 1993, 1992, 1991, 1990])
    # Whenever the selection changes, this will re-run and update the plot.
    st.altair_chart(create_plot(values, subgroup_choice, year_choice), use_container_width=True)
# st.title('Disease Explorer')
# subgroup_choice = st.selectbox("Select the disease you would like to explore:", ['Depressive', 'Schizophrenia', 'Bipolar_Disorder', 'Eating_Disorders', 'Anxiety_Disorders'])

# # Whenever the selection changes, this will re-run and update the plot.
# st.altair_chart(create_plot(subgroup_choice), use_container_width=True)
