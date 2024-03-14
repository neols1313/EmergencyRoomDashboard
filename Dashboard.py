import streamlit as st
from streamlit_option_menu import option_menu
import os
import warnings
warnings.filterwarnings('ignore')
import pandas as pd
import plotly_express as px
import plotly.graph_objects as go
from pathlib import Path
import random as random

current_dir = Path(__file__).parent if "__file__" in locals() else Path.cwd()
css_file = current_dir / "styles" / "style.css"

st.set_page_config(page_title="EMERGENCY ROOM VISITOR REPORT", page_icon=":stethoscope:",layout="wide")

with open(css_file) as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True,)

db = pd.read_csv(r'C:\Users\justm\OneDrive\Desktop\MyDashboard\Hospital.csv')

db['patient_name'] = db['patient_first_inital'] + ' ' + db['patient_last_name']

db['date'] = pd.to_datetime(db['date'], dayfirst=True)

db['am_pm'] = 'AM'
db.loc[db['date'].dt.hour >= 12, 'am_pm' ] = 'PM'
db['date'] = pd.to_datetime(db['date'], format='%d/%m/%Y')
db['year'] = db['date'].dt.year
db['month'] = db['date'].dt.month
db['mth_name'] =db['date'].dt.strftime('%b')
db['weektype'] = 'weekday'
db.loc[(db['date'].dt.day == 7) | (db['date'].dt.day == 1), 'weektype'] = 'weekend' 
db['department_referral'] = db['department_referral'].fillna("None")

db['age_bin'] = '0-10'
db.loc[(db['patient_age'] > 10) & (db['patient_age'] <= 20), 'age_bin'] = '11-20'
db.loc[(db['patient_age'] > 20) & (db['patient_age'] <= 30), 'age_bin'] = '21-30'
db.loc[(db['patient_age'] > 30) & (db['patient_age'] <= 40), 'age_bin'] = '31-40'
db.loc[(db['patient_age'] > 40) & (db['patient_age'] <= 50), 'age_bin'] = '41-50'
db.loc[(db['patient_age'] > 50) & (db['patient_age'] <= 60), 'age_bin'] = '51-60'
db.loc[(db['patient_age'] > 60) & (db['patient_age'] <= 70), 'age_bin'] = '61-70'
db.loc[(db['patient_age'] > 70) , 'age_bin'] = '70+'

db['age_group'] = 'Adult'
db.loc[(db['patient_age'] <= 18), 'age_group'] = 'Teenager'
db.loc[(db['patient_age'] <= 12), 'age_group'] = 'Middle Childhood'
db.loc[(db['patient_age'] <= 6), 'age_group'] = 'Early Childhood'
db.loc[(db['patient_age'] <= 2), 'age_group'] = 'Infant'


st.sidebar.header("Please Filter Here:")
AMorPM = st.sidebar.multiselect(
    "Select the AM/PM:",
    options=db["am_pm"].unique(),
    default=db["am_pm"].unique(),
)


gender = st.sidebar.multiselect(
    "Select the Gender:",
    options=db["patient_gender"].unique(),
    default=db["patient_gender"].unique()
)
if not gender:
    df = db.query(
    "am_pm == @AMorPM & patient_race ==@race & patient_gender == @gender"
)

race = st.sidebar.multiselect(
    "Select the Race:",
    options=db["patient_race"].unique(),
    default=db["patient_race"].unique()
)

df = db.query(
    "am_pm == @AMorPM & patient_race ==@race & patient_gender == @gender"
)

# Check if the dataframe is empty:
if df.empty:
    st.warning("No data available based on the current filter settings!")
    st.stop() # This will halt the app from further execution.


st.title(" :stethoscope: EMERGENCY ROOM VISITORS REPORT")
st.markdown('<style>div.block-container{padding-top:1rem;}</style>',unsafe_allow_html=True)

with st.expander("Data Preview"):
    st.dataframe(
        db)


patient_num = df['patient_id'].count()
patient_admin_pct = (df['patient_admin_flag'].sum()/patient_num *100).round(2)
patient_non_admin_pct = 100 -patient_admin_pct
patient_avg_sat = df[(df['patient_sat_score'].notna()) & (df['patient_sat_score'] !=0.00)]['patient_sat_score'].mean().round(2)
patient_didnot_rate = (df[(df['patient_sat_score'].isna()) | (df['patient_sat_score'] ==0.00)]['patient_id'].count()/patient_num*100).round(2)
avg_waittime = df['patient_waittime'].mean().round(2)

### DEFINE METRICS ###
def plot_metric(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value= value,
            gauge={"axis": {"visible": False}},
            number={
                "prefix": prefix,
                "suffix": suffix,
                "font": {'size':20, 'color': 'black'},
                "valueformat" : ".2f"
            },
            title={
                "text": label,
                "font": {"size": 12, 'color': 'blue'},
            },
        )
    )

    if show_graph:
        fig.add_trace(
            go.Scatter(
                y=random.sample(range(0, 101), 30),
                hoverinfo="skip",
                fill="tozeroy",
                fillcolor=color_graph,
                line={
                    "color": color_graph,
                },
            )
        )

    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=0),
        showlegend=False,
        height=100,
    )

    st.plotly_chart(fig, use_container_width=True)

def plot_metric2(label, value, prefix="", suffix="", show_graph=False, color_graph=""):
    fig = go.Figure()

    fig.add_trace(
        go.Indicator(
            value= value,
            gauge={"axis": {"visible": False}},
            number={
                "prefix": prefix,
                "suffix": suffix,
                "font": {'size':30, 'color': 'black'},
                "valueformat" : ".2f"
            },
            title={
                "text": label,
                "font": {"size": 18, 'color': 'blue'},
            },
        )
    )

    fig.update_xaxes(visible=False, fixedrange=True)
    fig.update_yaxes(visible=False, fixedrange=True)
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)', paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(t=30, b=0),
        showlegend=False,
        height=100,
    )

    st.plotly_chart(fig, use_container_width=True)

### METRICS ###

### STREAMLIT PAGE ###
top_left_column, top_right_column = st.columns((1, 2))
row2_col1, row2_col2, row2_col3 = st.columns((3,3,3))
row3_col1, row3_col2, row3_col3 = st.columns((2,1,2))



with top_left_column:
    tlc = st.container()
    script = """<div id = 'tlc_outer'></div>"""
    st.markdown(script, unsafe_allow_html=True)

    with tlc:

        script = """<div id = 'tlc_inner'></div>"""
        st.markdown(script, unsafe_allow_html=True)
        st.subheader("Total Patients Visits:")
        st.text(f"{patient_num}")
        
        col_1, col_2 = st.columns(2)
        with col_1:
            plot_metric(
                "Admin appt:",
                patient_admin_pct,
                prefix="",
                suffix="%",
                show_graph=False,
                color_graph="rgba(0, 104, 201, 0.2)",
            )
        with col_2:
            plot_metric(
                "Non-Admin appt:",
                patient_non_admin_pct,
                prefix="",
                suffix="%",
                show_graph=False,
                color_graph="rgba(0, 104, 201, 0.2)",
            )

    tlc_style = """<style>
    div[data-testid='stVerticalBlock']:has(div#tlc_inner):not(:has(div#tlc_outer)) {
        background-color: rgb(212, 161, 240);
        border-radius: 25px;
        padding: 0px 0px 20px 0px
        };
    </style>
    """

    st.markdown(tlc_style, unsafe_allow_html=True)  

with top_right_column:
    
    col1, col2, col3 = st.columns(3)

    with col1:
        trc = st.container()
        script = """<div id = 'col1_outer'></div>"""
        st.markdown(script, unsafe_allow_html=True)

        with trc:
            script = """<div id = 'col1_inner'></div>"""
            st.markdown(script, unsafe_allow_html=True)
            st.image("https://cdn-icons-png.flaticon.com/128/7332/7332154.png", width=80)
            plot_metric2(
                "Avg Sat Score",
                patient_avg_sat,
                prefix="",
                suffix="",
                show_graph=False,
                color_graph="rgba(0, 104, 201, 0.2)",
            )

        col1_style = """<style>
        div[data-testid='stVerticalBlock']:has(div#col1_inner):not(:has(div#col1_outer)) {
            background-color: rgb(190, 247, 242);
            border-top-right-radius: 30px;
            border-bottom-left-radius: 30px;
            padding: 10% 0% 10% 0%; 
            };
        </style>
        """

        st.markdown(col1_style, unsafe_allow_html=True)  
     
    with col2:

        trc = st.container()
        script = """<div id = 'col2_outer'></div>"""
        st.markdown(script, unsafe_allow_html=True)

        with trc:
            script = """<div id = 'col2_inner'></div>"""
            st.markdown(script, unsafe_allow_html=True)
            st.image("https://cdn-icons-png.flaticon.com/128/3670/3670605.png", width=80)
            plot_metric2(
                "Svc Not Rated",
                patient_didnot_rate,
                prefix="",
                suffix="%",
                show_graph=False,
                color_graph="rgba(0, 104, 201, 0.2)",
            )

        col1_style = """<style>
        div[data-testid='stVerticalBlock']:has(div#col2_inner):not(:has(div#col2_outer)) {
            background-color: rgb(137, 193, 240);
            border-top-right-radius: 30px;
            border-bottom-left-radius: 30px;
            padding: 10% 0% 10% 0%;  
            };
        </style>
        """
        st.markdown(col1_style, unsafe_allow_html=True)
    
    with col3:
        
        trc = st.container()
        script = """<div id = 'col3_outer'></div>"""
        st.markdown(script, unsafe_allow_html=True)

        with trc:
            script = """<div id = 'col3_inner'></div>"""
            st.markdown(script, unsafe_allow_html=True)
            st.image("https://cdn-icons-png.flaticon.com/128/6371/6371914.png", width=80)
            plot_metric2(
                "Avg Wait Time",
                avg_waittime,
                prefix="",
                suffix="mins",
                show_graph=False,
                color_graph="rgba(0, 104, 201, 0.2)",
            )

        col1_style = """<style>
        div[data-testid='stVerticalBlock']:has(div#col3_inner):not(:has(div#col3_outer)) {
            background-color: rgb(250, 218, 190);
            border-top-right-radius: 30px;
            border-bottom-left-radius: 30px;
            padding: 10% 0% 10% 0%; 
            };
        </style>
        """
        st.markdown(col1_style, unsafe_allow_html=True)

with row2_col1:
    df1 = df.groupby('weektype')['patient_id'].count().reset_index(name='count')
    fig1 = px.bar(df1, x='weektype', 
                  y='count', orientation='v', 
                  color='weektype', text_auto=True, color_discrete_sequence=['#44E4EB', '#008f7c'])
    fig1.update_layout(title = dict(text='Patient by WeekType', x=0.1),
                       showlegend= False,
                       title_font_color = '#0B0BF6', 
                       title_font_size= 20, 
                       plot_bgcolor='rgba(0,0,0,0)', 
                       paper_bgcolor='rgb(255, 240, 240)', 
                       margin= dict(l=20, r=20, t=80, b=10),
                       )
    fig1.update_traces(textposition = 'auto', textfont_color ='black')
    fig1.update_yaxes(title = " ", showgrid = False)
    fig1.update_xaxes(title = " ")
    st.plotly_chart(fig1, use_container_width=True, height = 150)
        
with row2_col2:
    df2 = df.groupby(['age_group'], as_index=True)['patient_id'].count().reset_index(name='patient_count')
    fig2 = px.bar(df2, x='patient_count', y='age_group', orientation='h', text_auto=True, color_discrete_sequence=['#44E4EB'])
    fig2.update_layout(title = dict(text= 'Patient by Age Group', x=0.1), 
                       title_font_color = '#0B0BF6', 
                       title_font_size= 20, 
                       plot_bgcolor='rgba(0,0,0,0)', 
                       paper_bgcolor='rgb(255, 240, 240)',
                       margin= dict(l=20, r=20, t=80, b=10),
                       uniformtext_minsize=10, 
                       uniformtext_mode='hide'
                       )
    fig2.update_traces(textposition = 'auto', textfont_color ='black')
    fig2.update_yaxes(title = " ")
    fig2.update_xaxes(title = " ")
    st.plotly_chart(fig2,use_container_width=True, height = 150)

with row2_col3:
    df3 = df.groupby('year')['patient_id'].count().reset_index()
    line2 = px.line(df3, x='year', y='patient_id', labels={'x':'Year', 'y':'No of Patients'}, text='patient_id', color_discrete_sequence=['#44E4EB'])
    line2.update_traces(hovertemplate='Year: %{x}<br>No of patients: %{y:.0f}', texttemplate='%{text:.0f}', textposition = 'top center')
    line2.update_layout(title = dict(text= 'Patient over Years', x=0.1), 
                        title_font_color = '#0B0BF6', 
                        title_font_size= 20,
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgb(255, 240, 240)',
                        margin= dict(l=20, r=20, t=80, b=10),)
    line2.update_xaxes(title = '', type= 'category')
    line2.update_yaxes(title = '', showgrid =False, showticklabels=False)
    st.plotly_chart(line2,use_container_width=True, height = 150)

with row3_col1:
    df4 = df.groupby(['mth_name', 'month'])['patient_id'].count().reset_index().sort_values('month')
    df4_min_y = df4['patient_id'].min()
    df4_min_x = df4.loc[df4['patient_id'].idxmin(), 'mth_name']
    df4_max_y = df4['patient_id'].max()
    df4_max_x = df4.loc[df4['patient_id'].idxmax(), 'mth_name']
    line1 = px.line(df4, x='mth_name', y='patient_id', labels={'x':'Month', 'y':'No of Patients'}, color_discrete_sequence=['#44E4EB'])
    line1.update_traces(hovertemplate='Month: %{x}<br>No of patients: %{y:.0f}', texttemplate='%{text:.0f}', textposition = 'top center')
    line1.update_layout(title = dict(text="Patient Visits by month", x=0.1), 
                        title_font_color = '#0B0BF6', 
                        title_font_size= 20,
                        plot_bgcolor='rgba(0,0,0,0)', 
                        paper_bgcolor='rgb(255, 240, 240)',
                        margin= dict(l=20, r=20, t=80, b=10)
                        )
    line1.update_xaxes(title = '')
    line1.update_yaxes(title = '', showgrid =False)
    line1.add_annotation(x=df4_min_x, y=df4_min_y, xref="x",
            yref="y",
            text=str(df4_min_y),
            showarrow=True,
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="#ffffff"
                ),
            align="center",
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="#636363",
            ax=0,
            ay=-40,
            bordercolor="#c7c7c7",
            borderwidth=2,
            borderpad=4,
            bgcolor="#ff7f0e",
            opacity=0.8
            )
    line1.add_annotation(x=df4_max_x, y=df4_max_y, xref="x",
            yref="y",
            text= str(df4_max_y),
            showarrow=True,
            yanchor='bottom',
            font=dict(
                family="Courier New, monospace",
                size=16,
                color="#ffffff"
                ),
            align="center",
            arrowhead=2,
            arrowsize=1,
            arrowwidth=1,
            arrowcolor="#636363",
            ax=0,
            ay=-20,
            bordercolor="#c7c7c7",
            borderwidth=2,
            borderpad=4,
            bgcolor="#078086",
            opacity=0.8
            )
    st.plotly_chart(line1,use_container_width=True, height = 150)

male = (df[df['patient_gender'] == "M"]['patient_gender'].count()/patient_num *100).round(1)
female = (df[df['patient_gender'] == "F"]['patient_gender'].count()/patient_num *100).round(1)
not_defined = (df[df['patient_gender'] == "NC"]['patient_gender'].count()/patient_num *100).round(1)

with row3_col2:
    st.write("")
    st.write("")
    
    plh = st.container()
    script = """<div id = 'chat_outer'></div>"""
    st.markdown(script, unsafe_allow_html=True)

    with plh:
        script = """<div id = 'chat_inner'></div>"""
        st.markdown(script, unsafe_allow_html=True)
        st.write("")
        st.subheader("Gender Breakdown")
        st.write(" ")
        st.write(f'<p style="display: flex; justify content: center;"><img src="https://cdn-icons-png.flaticon.com/128/4874/4874892.png" width="30" style="margin-right: 5px"><span> MALE: {male}%</span></p>', 
                 unsafe_allow_html=True)
        st.write(" ")
        st.write(f'<p style="display: flex; justify content: center;"><img src="https://cdn-icons-png.flaticon.com/128/7029/7029970.png" width="30" style="margin-right: 5px"><span> FEMALE: {female}%</span></p>', 
                 unsafe_allow_html=True)
        st.write(" ")
        st.write(f'<p style="display: flex; justify content: center;"><img src="https://cdn-icons-png.flaticon.com/128/1320/1320924.png" width="30" style="margin-right: 5px"><span> UNKNOWN: {not_defined}%</span></p>', 
                 unsafe_allow_html=True)
        st.write(" ")
        st.write(" ")
    
    chat_plh_style = """<style>
    div[data-testid='stVerticalBlock']:has(div#chat_inner):not(:has(div#chat_outer)) {
        background-color: rgb(12, 204, 204);
        padding: 15% 0 15% 0;
        border-top-right-radius: 30px;
        border-bottom-left-radius: 30px;};
    </style>
    """

    st.markdown(chat_plh_style, unsafe_allow_html=True)  

with row3_col3:
    df6 = df.groupby(['department_referral'])['patient_id'].count().reset_index(name='count').sort_values('count')
    fig3 = px.bar(df6, x='count', y='department_referral', orientation='h', text_auto=True, color_discrete_sequence=['#44E4EB'])
    fig3.update_layout(title = dict(text='Patients by Department_referral', x=0.1),
                       title_font_color = '#0B0BF6', 
                       title_font_size= 20, 
                       plot_bgcolor='rgba(0,0,0,0)', 
                       paper_bgcolor='rgb(255, 240, 240)', 
                       margin= dict(l=20, r=20, t=80, b=10),
                       uniformtext_minsize=10, 
                       uniformtext_mode='hide')
    fig3.update_traces(textposition = 'auto', textfont_color ='black')
    fig3.update_yaxes(title = " ")
    fig3.update_xaxes(title = " ")
    st.plotly_chart(fig3,use_container_width=True, height = 150)

selected_option = st.selectbox("Select", options=["Patient Satisfaction Score", "Patient Waittime"])

st.write(selected_option)

if selected_option == "Patient Waittime":
    df7 = df.groupby(['patient_race', 'age_bin'], as_index=False)['patient_waittime'].mean().round(2)
    fig4 = px.density_heatmap(df7, x='age_bin', y='patient_race', z='patient_waittime', )
    fig4.update_coloraxes(colorscale=([0, '#016C90'], [0.25, '#7BBCD2'], [0.5, '#94D7DA'], [0.75, '#C0A2A6'], [1, '#F9A2AF']))
    fig4.update_layout(coloraxis_colorbar=dict(
        title='Mean Wait Time'
    ))
    st.plotly_chart(fig4, use_container_width=True, height = 200)

else:
    df8 = df.groupby(['patient_race', 'age_bin'], as_index=False)['patient_sat_score'].mean().round(2)
    fig5 = px.density_heatmap(df8, x='age_bin', y='patient_race', z='patient_sat_score', )
    fig5.update_coloraxes(colorscale=([0, '#016C90'], [0.25, '#7BBCD2'], [0.5, '#94D7DA'], [0.75, '#C0A2A6'], [1, '#F9A2AF']))
    fig5.update_layout(coloraxis_colorbar=dict(
        title='Mean Sat Score'
    ))
    st.plotly_chart(fig5, use_container_width=True, height = 200)