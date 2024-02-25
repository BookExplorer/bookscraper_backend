import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import pycountry


def generate_graph(country_counts: pd.DataFrame):
    country_names = {"country": [country.name for country in pycountry.countries]}

    all_countries = pd.DataFrame(country_names)

    complete_data = all_countries.merge(
        country_counts, on="country", how="left"
    ).fillna(0)

    # Create a base map to show all country borders
    fig = go.Figure(
        data=go.Choropleth(
            locations=complete_data["country"],
            z=complete_data["count"],
            locationmode="country names",
            colorscale="oranges",
            marker_line_color="black",  # Lines between countries
            marker_line_width=0.5,
            colorbar_title="Number of Authors",
        )
    )
    fig.update_geos(
        projection_type="orthographic",
        showcountries=True,  # show country boundaries
    )
    # Update the layout to add the title and adjust geo settings
    fig.update_layout(
        title_text="Number of Authors by Country",
        coloraxis_colorbar=dict(
            title="Number of Authors",
            tickvals=[
                0,
                complete_data["count"].max(),
            ],  # ensures that 0 is labeled on the colorbar
            ticktext=["0", "Max"],
        ),
        geo=dict(
            showframe=False,
            showcoastlines=False,
            projection_type="equirectangular",
            landcolor="rgba(217, 217, 217, 1)",  # Light grey land color
            lakecolor="rgba(127,205,255,1)",  # Light blue lake color
            oceancolor="rgba(127,205,255,0.5)",  # Slightly transparent ocean color
        ),
    )

    fig.show()
