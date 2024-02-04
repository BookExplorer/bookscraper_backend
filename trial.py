import pandas as pd
import plotly.express as px
import plotly.graph_objs as go
import pycountry

country_names = {"country": [country.name for country in pycountry.countries]}

all_countries = pd.DataFrame(country_names)


# Sample data
country_counts = pd.DataFrame(
    {
        "country": [
            "United States",
            "United Kingdom",
            "France",
            "Germany",
            "Canada",
            "Australia",
            "Brazil",
        ],
        "count": [20, 15, 10, 8, 5, 3, 2],
    }
)

complete_data = all_countries.merge(country_counts, on="country", how="left").fillna(0)

# Create a base map to show all country borders
fig = go.Figure(
    data=go.Choropleth(
        locations=complete_data["country"],
        z=complete_data["count"],
        locationmode="country names",
        colorscale="Blues",
        marker_line_color="black",  # Lines between countries
        marker_line_width=0.5,
        colorbar_title="Number of Authors",
    )
)

# Update the layout to add the title and adjust geo settings
fig.update_layout(
    title_text="Number of Authors by Country",
    geo=dict(showframe=False, showcoastlines=False, projection_type="equirectangular"),
)

# Show the figure
fig.show()
