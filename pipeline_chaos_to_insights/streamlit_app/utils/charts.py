import plotly.express as px

def bar_chart(df, x_col, y_col, title):
    """Generates a descending bar chart with gradient colors and animation."""
    df_sorted = df.sort_values(by=y_col, ascending=False)

    fig = px.bar(
        df_sorted,
        x=x_col,
        y=y_col,
        title=title,
        text=y_col,
        color=y_col,
        color_continuous_scale=px.colors.sequential.Plasma,
    )
    fig.update_traces(
        texttemplate='%{text:.3f}',
        textposition='outside',
        marker_line_color='black',
        marker_line_width=1.5,
        marker_opacity=0.85,
        cliponaxis=False,
    )
    fig.update_layout(
        uniformtext_minsize=8,
        uniformtext_mode='hide',
        margin=dict(l=20, r=20, t=50, b=20),
        coloraxis_colorbar=dict(title="Rate"),
        font=dict(family="Montserrat, sans-serif", size=14, color="#550088"),
        transition_duration=1000,
    )
    fig.update_yaxes(title=y_col, autorange="reversed")  # Keep reversed if you want top-to-bottom order
    fig.update_xaxes(title=x_col)
    return fig

def line_chart(df, x_col, y_col, title):
    """Line chart with similar style."""
    fig = px.line(df, x=x_col, y=y_col, title=title, markers=True)
    fig.update_layout(
        margin=dict(l=20, r=20, t=40, b=20),
        hovermode="x unified",
        font=dict(family="Montserrat, sans-serif", size=14, color="#550088"),
        transition_duration=800,
    )
    return fig

def pie_chart(df, names_col, values_col, title):
    """Pie chart for visualizing proportions."""
    fig = px.pie(df, names=names_col, values=values_col, title=title, hole=0.3)
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family="Montserrat, sans-serif", size=14, color="#550088"),
        transition_duration=800,
    )
    return fig

def scatter_chart(df, x_col, y_col, size_col, title):
    """Scatter plot with size variation."""
    fig = px.scatter(
        df,
        x=x_col,
        y=y_col,
        size=size_col,
        title=title,
        size_max=40,
        color=y_col,
        color_continuous_scale=px.colors.sequential.Plasma,
    )
    fig.update_layout(
        margin=dict(l=20, r=20, t=50, b=20),
        font=dict(family="Montserrat, sans-serif", size=14, color="#550088"),
        transition_duration=800,
    )
    return fig
