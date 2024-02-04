import pandas as pd
import plotly.express as px

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

# Generate the choropleth map
fig = px.choropleth(
    country_counts,
    locations="country",
    color="count",
    locationmode="country names",
    color_continuous_scale=px.colors.sequential.Plasma,
    title="Number of Authors by Country",
)

# Show the figure
fig.show()
