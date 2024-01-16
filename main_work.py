# This is a sample Python script.

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.
import streamlit as st
#import inspect
from neo4j import GraphDatabase
import pandas as pd
import dotenv
import os
import plotly.express as px
import numpy as np
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import plotly.io as pio


def neo4j_query(query, parameters=None):
    # with GraphDatabase.driver(URI, auth=AUTH) as driver:
    #     driver.verify_connectivity()
    # URI examples: "neo4j://localhost", "neo4j+s://xxx.databases.neo4j.io"
    dotenv.load_dotenv()
    URI = os.getenv("uri")
    user = os.getenv("user")
    passw = os.getenv("passw")
    AUTH = (user, passw)

    with GraphDatabase.driver(URI, auth=AUTH) as driver:
        with driver.session() as session:
            result = session.run(query, parameters)
            data = [record.data() for record in result]
            return pd.DataFrame(data)

def activity_query_plot():
    query_semester = """MATCH (n:LearningActivity)
                     RETURN n.semester AS Semester, count(n) as activities
                     ORDER BY n.semester"""
    df_semester = neo4j_query(query_semester)
    st.subheader("Number of activities per semester")
    st.markdown("The following plot shows the number of activities per semester.")
    df_semester["Semester"] = df_semester["Semester"].astype("category")

    fig = px.bar(df_semester, x="Semester", y="activities", color="Semester")
    fig.update_traces(hovertemplate=(
            "<b>Activities: </b>%{y}<br>" +
            "<b>Semester: </b>%{x}<br>" +
            "<extra></extra>"
    ))
    fig.update_layout(
        xaxis_title="Semester",
        yaxis_title="Number of activities",
        showlegend=False,
        # color_discrete_sequence=px.colors.qualitative.G10
    )
    return fig, df_semester

def staff_query_plot():
    query_teaching_staff = ("""MATCH (n:Teacher)
                     RETURN n.academicTitle AS title, count(n) AS Count 
                     ORDER BY title""")
    df_teaching_staff = neo4j_query(query_teaching_staff)
    st.subheader("Number of teaching staff per title")
    st.markdown("The following plot shows the number of teaching staff per title.")

    fig = px.bar(df_teaching_staff, x="title", y="Count", color="title")
    fig.update_traces(hovertemplate=(
            "<b>Count: </b>%{y}<br>" +
            "<b>Title: </b>%{x}<br>" +
            "<extra></extra>"
    ))
    fig.update_layout(
        xaxis_title="",
        yaxis_title="Count",
        showlegend=False
    )
    return fig, df_teaching_staff
def full_query_plot():
    full_query = ("""MATCH (n) RETURN n""")
    df_locations = neo4j_query(full_query)
    st.subheader("Map of activities")
    st.markdown("The following map shows the location of the activities.")
    df_locations = pd.json_normalize(df_locations['n'])

    fig = px.scatter_mapbox(df_locations,
                        lat="latitude",
                        lon="longitude",
                        hover_name="name",
                        hover_data=["workHours"],
                        color_discrete_sequence=["fuchsia"],
                        zoom=2,
                        height=300)
    fig.update_layout(mapbox_style="open-street-map")
    return fig, df_locations

def scientific_practices_query_plot():
    query_scientific_practices = ("""MATCH (n:LearningActivity)-[r]-(s:`Scientific Practice`)
                                     RETURN s.name as `Scientific Practice`, count(s) as `Count`, n.semester AS Semester
                                     ORDER BY Semester""")
    df_scientific_practices = neo4j_query(query_scientific_practices)
    st.subheader("Number of scientific practices per semester")
    st.markdown("The following plot shows the number of scientific practices per semester.")
    df_scientific_practices = df_scientific_practices.pivot(index='Semester', columns='Scientific Practice',
                                                            values='Count').fillna(0)

    # Create a stacked bar plot
    fig = go.Figure()

    for col in df_scientific_practices.columns:
        fig.add_trace(go.Bar(
            x=df_scientific_practices.index,
            y=df_scientific_practices[col],
            name=col,
            hovertemplate='Semester: %{x}<br>' + col + ': %{y}<extra></extra>',
        ))

    fig.update_layout(
        barmode='stack',
        title='Development of Scientific Practices in the Curriculum',
        xaxis_title='',
        yaxis_title='',
        legend_title='Scientific Practice',
        legend=dict(
            font=dict(
                size=10,
            ),
        ),
        autosize=False,
        width=900,  # Adjust these values to make the plot larger
        height=400,
    )


    return fig, df_scientific_practices

def activityName_query_plot():
    query_activity = """MATCH (l:LearningActivity) 
                        RETURN l.name AS `Name` , l.semester AS `Semester`, l.workHours AS `Work hours`
                        ORDER BY l.semester"""
    df_activity = neo4j_query(query_activity)
    st.subheader("Work hours per activity")
    st.markdown("The following plot shows the work hours per activity.")
    fig_bubble = px.scatter(df_activity,
                            x="Semester",
                            y="Work hours",
                            size="Work hours",
                            color="Name",
                            hover_name="Name", #title="Bubble Chart of Work Hours by Learning Activity",
                            labels={"Work hours": "Work Hours", "Semester": "Semester"})

    fig_bubble.update_layout(xaxis_title="Semester", yaxis_title="Work Hours")
    return fig_bubble, df_activity

def pie_staff_query_plot():
    query_teaching_staff_pie = ("""MATCH (n:Teacher)
                            RETURN n.academicTitle AS title, count(n) AS Count 
                            ORDER BY title""")
    df_teaching_staff_pie = neo4j_query(query_teaching_staff_pie)
    st.subheader("Number of teaching staff per title")
    st.markdown("The following plot shows the number of teaching staff per title.")
    fig = px.pie(df_teaching_staff_pie,
                 names="title",
                 values="Count")
                 #title="Pie Chart of Teaching Staff by Title")
    return fig, df_teaching_staff_pie

def main():
    st.sidebar.title("Shape of the Future")
    st.sidebar.markdown("This is a dashboard to explore the data of the Shape of the Future project.")
    st.sidebar.title("Explore")
    #st.sidebar.markdown("Select the plot you would like to see.")

    pio.templates.default = "presentation+ggplot2"


    # Add a selectbox to the sidebar
    option = st.sidebar.selectbox(
        'Select the plot you would like to see.',
        ('LearningActivity', 'Academics', 'Map of Activities', 'Scientific Practices', 'Activity Name',
         'Teaching Staff '
                                                                                                    'Pie'))


    if option == 'LearningActivity':
        fig_activity, df_semester = activity_query_plot()
        st.plotly_chart(fig_activity, theme=None)
        #sourcelines, _ = inspect.getsourcelines(activity_query_plot)
        with st.expander("Show raw data"):
            st.dataframe(df_semester)
    elif option == 'Academics':
        fig_staff, df_teaching_staff = staff_query_plot()
        st.plotly_chart(fig_staff, theme=None)
        #sourcelines, _ = inspect.getsourcelines(staff_query_plot)
        with st.expander("Show raw data"):
            st.dataframe(df_teaching_staff)
    elif option == 'Map of Activities':
        fig_full, df_locations = full_query_plot()
        st.plotly_chart(fig_full, theme=None)
        #sourcelines, _ = inspect.getsourcelines(full_query_plot)
        with st.expander("Show raw data"):
            st.dataframe(df_locations)
    elif option == 'Scientific Practices':
        fig_scientific_practices, df_scientific_practices = scientific_practices_query_plot()
        st.plotly_chart(fig_scientific_practices, theme=None)
        #sourcelines, _ = inspect.getsourcelines(scientific_practices_query_plot)
        with st.expander("Show raw data"):
            st.dataframe(df_scientific_practices)
    elif option == 'Activity Name':
        fig_activity_name, df_activity_name = activityName_query_plot()
        st.plotly_chart(fig_activity_name, theme=None)
        #sourcelines, _ = inspect.getsourcelines(activityName_query_plot)
        with st.expander("Show raw data"):
            st.dataframe(df_activity_name)
    elif option == 'Teaching Staff Pie':
        fig_pie_staff,df_teaching_staff_pie = pie_staff_query_plot()
        st.plotly_chart(fig_pie_staff, theme=None)
        #sourcelines, _ = inspect.getsourcelines(pie_staff_query_plot)
        with st.expander("Show raw data"):
            st.dataframe(df_teaching_staff_pie)

    #Get the source code
    # sourcelines, _ = inspect.getsourcelines(main)
    # with st.expander("Source Code"):
    #     st.code("".join(sourcelines))

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    main()

# See PyCharm help at https://www.jetbrains.com/help/pycharm/
