import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.figure_factory as ff
import matplotlib

st.set_page_config(page_title="Superstore", page_icon=":bar_chart:", layout="wide")
st.title(":bar_chart: Sample Supermart RDA")

st.markdown("""
<style>
    div.block-container{
            padding-top: 2rem;
            }

</style>
""", unsafe_allow_html=True)
fp = st.sidebar.file_uploader(":file_folder: Upload a File", type=(['csv', 'xlsx', 'xls']))

if fp is not None:
    filename = fp.name
    st.sidebar.write(f"Uploaded file: {filename}")

    if filename.endswith('.csv'):
        df = pd.read_csv(fp)

    elif filename.endswith('.xlsx') or filename.endswith('.xls'):
        df = pd.read_excel(fp, index_col = 0)
else:
    st.stop()

col1, col2 = st.columns((2))
df['Order Date'] = pd.to_datetime(df["Order Date"])

start_date = df['Order Date'].min()
end_date = df['Order Date'].max()

with col1:
    date1 = pd.to_datetime(st.date_input("Start Date", start_date))

with col2:
    date2 = pd.to_datetime(st.date_input("End Date", end_date))

df = df[(df['Order Date'] >= date1) & (df['Order Date'] <= end_date)].copy()

st.sidebar.header("Choose your filter:")

region = st.sidebar.multiselect("Pick your region: ", df['Region'].unique())
filtered_df = df[df['Region'].isin(region)] if region else df

state = st.sidebar.multiselect("Pick your state: ", filtered_df['State'].unique())
filtered_df = filtered_df[filtered_df['State'].isin(state)] if state else filtered_df

city = st.sidebar.multiselect("Pick your city: ", filtered_df['City'].unique())
filtered_df = filtered_df[filtered_df['City'].isin(city)] if city else filtered_df

category_df = filtered_df.groupby(by = ['Category'], as_index=False)['Sales'].sum()

with col1:
    st.subheader("Category wise sales")
    fig = px.bar(category_df, x='Category', y='Sales',text=['${:,.2f}'.format(x) for x in category_df["Sales"]], template='plotly_dark')
    st.plotly_chart(fig, use_container_width=True, height=200)

with col2:
    st.subheader("Region wise sales")
    fig = px.pie(filtered_df, values="Sales", names="Region", hole=0.5)
    fig.update_traces(text=filtered_df["Region"], textposition='outside')
    st.plotly_chart(fig, use_container_width=True)

cl1, cl2 = st.columns(2)

with cl1:
    with st.expander("Category_ViewData"):
        st.write(category_df)
        csv = category_df.to_csv(index=False)
        st.download_button("Download Data", data=csv, file_name="category.csv", mime="text/csv", help="Click here to download the data as csv file")

with cl2:
    with st.expander("Region_ViewData"):
        region_df = filtered_df.groupby(by=["Region"], as_index=False)["Sales"].sum()
        st.write(region_df)
        csv = region_df.to_csv(index=False)
        st.download_button("Download Data", data=csv, file_name="region.csv", mime="text/csv", help="Click here to download the data as csv file")

filtered_df["month_year"] = filtered_df["Order Date"].dt.to_period("M")
st.subheader("Time Series Analysis")

linechart = filtered_df.groupby(filtered_df['month_year'].dt.strftime('%Y : %b'))['Sales'].sum().reset_index()


fig = px.line(linechart, x='month_year', y='Sales', labels={"Sales": "Amount"}, height=500, width=1000, template='gridon')
st.plotly_chart(fig, use_container_width=True)

with st.expander("View data of Time Series"):
    st.write(linechart.T)
    csv = linechart.to_csv(index=False)
    st.download_button("Download Data", data=csv, file_name="time_series.csv", mime="text/csv", help="Click here to download time series data")

st.subheader("Heirarchial view of sales using tree map")
fig2 = px.treemap(filtered_df, path=["Region", "Category", "Sub-Category"], values="Sales", hover_data=["Sales"], color="Sub-Category")
st.plotly_chart(fig2, use_container_width=True)

st.subheader(":point_right: Month wise Sub-Category Sales Summary")
with st.expander("Month and sub-category wise sales"):
    st.write("Month and sub-category wise sales")
    filtered_df["month"] = filtered_df["Order Date"].dt.month_name()
    sub_category_year = pd.pivot_table(data=filtered_df, values='Sales', index='Sub-Category', columns='month')
    st.dataframe(sub_category_year.style.background_gradient(cmap="Blues"))

data1 = px.scatter(filtered_df,title="Relationship between sales and profits", x="Sales", y="Profit", size="Quantity")
st.plotly_chart(data1, use_container_width=True)