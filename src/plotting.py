import streamlit as st
import pandas as pd
import plotly.graph_objects as go

plotting_types = {
    0: "lines",
    1: "markers"
}

# create plotly figure from data = (name, pd.Dataframe)
def create_figure(fig, data):
    for d in data:
        df, name, mode = d
        
        style = {
            "size": 12
        }

        if "buy" in name.lower().split():
            style["color"] = "green"

        elif "sell" in name.lower().split():
            style["color"] = "red"

        series = go.Scatter(x=df["x"], y=df["y"], name=name, mode=mode, marker=style)
        fig.add_trace(series)
    return fig

# dataframe as list
def create_list(data):
    df = pd.DataFrame.from_dict(data, orient="index", columns=[""])
    st.table(df)

def candelstick(df):
    fig = go.Figure(data=[go.Candlestick(
        x=df.index,
        open=df["Open"],
        high=df["High"],
        low=df["Low"],
        close=df["Close"]
    )])
    fig.update_layout(xaxis_rangeslider_visible=False)
    st.plotly_chart(fig, use_container_width=True)

# parse the chart section
def parse_charts(data):
    charts = data["Charts"]
    orders = data["Orders"]

    for chart_name, chart in charts.items():
        series = chart["Series"]
        if series is None:
            continue

        data = []

        for series_name, serie in series.items():
            df = pd.DataFrame.from_dict(serie["Values"])

            try:
                df["x"] = pd.to_datetime(df["x"], unit="s")
                # get the type for the plot or default to lines
                plot_type = plotting_types.get(serie["SeriesType"], "lines")
                data.append((df, series_name, plot_type))
            except KeyError as e:
                st.write(f"ERROR: {e}")
                continue
        fig = go.Figure()
        create_figure(fig, data)

        expander = st.beta_expander(chart_name)
        with expander: 
            st.plotly_chart(fig, use_container_width=True)

# parse TotalPerformance section
def parse_total_performance(data):

    total_performance = data["TotalPerformance"]
    expander = st.beta_expander("Total Performance")

    with expander:
        col1, col2 = st.beta_columns(2)

        with col1:
            st.subheader("Trade Statistics")
            create_list(total_performance["TradeStatistics"])
        with col2:
            st.subheader("Portfolio Statistics")
            create_list(total_performance["PortfolioStatistics"])

def parse_orders(data):

    expander = st.beta_expander("Closed Trades")
    with expander:
        trades = data["TotalPerformance"]["ClosedTrades"]

        if len(trades) is 0:
            return

        for i, trade in enumerate(trades):
            trades[i]["Symbol"] = trade["Symbol"]["Value"]

        df = pd.DataFrame.from_dict(trades)
        df.set_index("Symbol", inplace=True)
        st.table(df)

# parse the last 2 Statistics sections
def parse_statistics(data):

    expander = st.beta_expander("Statistics")

    with expander:
        col1, col2 = st.beta_columns(2)

        with col1:
            st.subheader("Statistics")
            create_list(data["Statistics"])
        with col2:
            st.subheader("Runtime Statistics")
            create_list(data["RuntimeStatistics"])
        
        