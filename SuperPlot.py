import streamlit as st
import pandas as pd
import altair as alt

# Bar Chart Specs
domain1 = ['RFS SUPER OUT', 'EW SUPER OUT', 'CASH OUT', 'PENSION', 'RFS WAGES', 'EW WAGES','EXCESS CASH']
range1 =  ['green',           'red',        'blue',     'yellow',  'magenta',   'pink',   'yellow']
# Line Chart Specs
domain2 = ['RFS SUPER OUT', 'EW SUPER OUT', 'CASH OUT', 'PENSION', 'RFS WAGES', 'EW WAGES', 'TOTAL INCOME']
range2 =  ['green',           'red',        'blue',     'yellow',  'magenta',   'pink',      'cyan']
domain3 = ['RFS BALANCE',   'EW BALANCE',   'CASH BALANCE','OTHER ASSETS']
range3 =   ['green',           'red',        'blue',       'yellow']

# domain1 = ['RFS SUPER OUT', 'EW SUPER OUT', 'CASH OUT', 'PENSION', 'RFS WAGES', 'EW WAGES','EXCESS CASH']
# range1 =  ['red',           'green',        'blue',     'yellow',  'magenta',   'pink',   'yellow']
#   plot_barchart_plus(df1,           domain1, range1,'RFS AGE', dftick,       'TickVal')
def plot_barchart_plus(maindataframe, domain, range,  column,    tickdataframe, tickfield) :
#----------------------------------------------------------------
    data_melted = pd.melt(maindataframe, id_vars=[column], value_vars=domain, var_name='Contributor', value_name='$ Per Year')
    data_melted_tick = pd.melt(tickdataframe, id_vars=[column], value_vars=tickfield, var_name='Contributor', value_name='last plot')
    match column :
        case 'RFS AGE' :
            xcolor = '#00ff00' #green'
            xcolor2 = "#c3fac3" #green'
        case 'EW AGE' :
            xcolor = "#fa3737" #red'
            xcolor2 = "#fdb4b4" #red'
        case 'INDEX' :
            xcolor = xcolor2 ='#ffffff' #white'
            
    chart = (
        alt.Chart(data_melted).mark_bar()
        .encode(
            alt.X(f"{column}"+":N", sort='x', axis=alt.Axis(labelColor=xcolor2, labelFontSize= 18, titleColor=xcolor, titleFontSize=24)),
            alt.Y('$ Per Year:Q' ),
            color = alt.Color('Contributor:N',  sort=domain, legend=alt.Legend(orient='bottom'), \
                    scale=alt.Scale(domain=domain, range=range)),
            order = "order:Q"  # weird - order is undefined ??, but needed - works
        ).properties (
            height = 400
        ) .interactive()
        
    )
    tick = (
        alt.Chart(data_melted_tick).mark_line(   # mark_tick
            point = alt.OverlayMarkDef( filled = False, fill = 'white'),
            color="#FF19EC",
            thickness=1,
            size=2,  # controls width of tick.
        )
        .encode(
            alt.X(f"{column}"+":N", sort='x'),
            alt.Y('last plot:Q' ),
            # color = alt.Color('variablet:N',  sort=domain, legend=alt.Legend(orient='bottom'), \
            #         scale=alt.Scale(domain=domain, range=range)),
            # order = "order:Q"  # weird - order is undefined ??, but needed - works    st.altair_chart(chart + tick)    
        ).properties (
            height = 400
        ).interactive()

    )

    st.altair_chart(chart + tick)    

#----------------------------------------------------------------
def plot_barchart(dataframe, domain, range, column) :
#----------------------------------------------------------------
    data_melted = pd.melt(dataframe, id_vars=[column], value_vars=domain, var_name='Contributor', value_name='$ Per Year')
    match column :
        case 'RFS AGE' :
            xcolor = '#00ff00' #green'
            xcolor2 = "#c3fac3" #green'
        case 'EW AGE' :
            xcolor = "#fa3737" #red'
            xcolor2 = "#fdb4b4" #red'
        case 'INDEX' :
            xcolor = xcolor2 ='#ffffff' #white'
    
    chart = (
        alt.Chart(data_melted).mark_bar()
        .encode(
            alt.X(f"{column}"+":N", sort='x',axis=alt.Axis(labelColor=xcolor2, labelFontSize= 18, titleColor=xcolor, titleFontSize=24)  ),
            alt.Y('$ Per Year:Q' ),
            color = alt.Color('Contributor:N',  sort=domain, legend=alt.Legend(orient='bottom'), \
                    scale=alt.Scale(domain=domain, range=range)),
            order = "order:Q"  # weird - order is undefined ??, but needed - works
        ).properties (
            height = 400
        ).interactive()

    )
    st.altair_chart(chart)    



#----------------------------------------------------------------
def plot_linechart(dataframe, domain, range, column) :
#----------------------------------------------------------------
    #single_select = alt.selection_point(fields=['RFS AGE', 'PENSION'],name = 'RSEL') # You can specify fields to identify the point
  
    data_melted = pd.melt(dataframe, id_vars=[column], value_vars=domain, var_name='computed figure', value_name='$ value')
    match column :
        case 'RFS AGE' :
            xcolor = '#00ff00' #green'
            xcolor2 = "#c3fac3" #green'
        case 'EW AGE' :
            xcolor = "#fa3737" #red'
            xcolor2 = "#fdb4b4" #red'
        case 'INDEX' :
            xcolor = xcolor2 ='#ffffff' #white'
    chart = (
        alt.Chart(data_melted).mark_line(point = alt.OverlayMarkDef( filled = False, fill = 'white'))
        .encode(
            alt.X(f"{column}"+":N", sort='x',axis=alt.Axis(labelColor=xcolor2, labelFontSize= 18, titleColor=xcolor, titleFontSize=24)),
            alt.Y('$ value:Q' ),
            color = alt.Color('computed figure:N',  sort=domain, legend=alt.Legend(orient='bottom'), \
                    scale=alt.Scale(domain=domain, range=range)),
            order = "order:Q"  # weird - order is undefined ??, but needed - works
        ).properties (
            height = 500
        )
        #.add_params(single_select)
        .interactive()

    )
    st.altair_chart(chart)   
    #print(event_data)
    #return event_data

#----------------------------------------------------------------
def display_linechart(df1, whichdomain) :
#----------------------------------------------------------------

    plot_axis = st.session_state['plot_axis']
    match whichdomain :
        # case 1 :
        #     plot_linechart(df1, domain1, range1, plot_axis)
        case 2 :
            plot_linechart(df1, domain2, range2, plot_axis)
        case 3 :
            plot_linechart(df1, domain3, range3, plot_axis)



#----------------------------------------------------------------
def display_barchart_plus(st, numOfRows, Age1, Age2, df1) :
#----------------------------------------------------------------
    #-- Handle the Marking of previous and display of first graph
    gap, col1, col2, col3, col4 = st.columns([1, 1, 1, 2, 6])
    MarkButton = col1.button('Mark This', type = 'secondary' )
    ClearButton = col2.button('Clear Mark', type = 'secondary')
    Auto_tick_checked = col3.checkbox("AutoMark previous", False)
    
    radio_vals = [":rainbow[RFS]", ":red[***EW***]", "Years"]
    selx = col4.radio(
        "Plot X Axis as ",
        radio_vals,
        captions=[
            ":rainbow[Plot by Richard's Age]",
            ":red[Plot by Elly's Age]",
            "Plot by Years from now",
        ],
        horizontal = True
    )

    # trying to stop axis change from modifying the stored tick - but the damage happens in the step before I think
    # if 'old_plot_axis'  not in st.session_state :
    #     st.session_state.old_plot_axis = 'RFS AGE'
    # skip_update = False
    if selx == radio_vals[0] : 
        plot_axis = 'RFS AGE'
    elif selx == radio_vals[1] :
        plot_axis = 'EW AGE'
    else :
        plot_axis = 'INDEX'

    # if st.session_state.old_plot_axis != plot_axis :
    #     # axis changed
    #     skip_update = True
    # st.session_state.old_plot_axis = plot_axis    

    if 'plot_axis' not in st.session_state :
        st.session_state['plot_axis'] = plot_axis
    st.session_state['plot_axis'] = plot_axis

    st.write('---')

    if 'stored_ticks' not in st.session_state :
        st.session_state['stored_ticks'] = df1['TOTAL INCOME']
    if 'frame_state' not in st.session_state :
        st.session_state['frame_state'] = False

    dftick = pd.DataFrame(index=range(numOfRows))
    dftick.loc[:,'TickVal'] = st.session_state['stored_ticks'] 
    dftick.loc[:,'RFS AGE'] = range(Age1, numOfRows+Age1)
    dftick.loc[:,'EW AGE']  = range(Age2, numOfRows+Age2)
    dftick.loc[:,'INDEX']   = range(numOfRows)

    FrameVisible = st.session_state['frame_state']

    if MarkButton :
        st.session_state['stored_ticks'] = df1['TOTAL INCOME']
        dftick.loc[:,'TickVal'] = st.session_state['stored_ticks'] 
        FrameVisible = True

    if ClearButton :
        FrameVisible = False
        
    if FrameVisible == True :
        plot_barchart_plus(df1,domain1, range1, plot_axis, dftick, 'TickVal')
    else :
        plot_barchart(df1,domain1, range1, plot_axis)

    # Must do this after chart update to make it 'old' data that is stored
    if Auto_tick_checked == True :
        # if skip_update == True :
        #     skip_update = False
        # else :            
        st.session_state['stored_ticks'] = df1['TOTAL INCOME']
        dftick.loc[:,'TickVal'] = st.session_state['stored_ticks'] 
        FrameVisible = True

    st.session_state['frame_state'] = FrameVisible


    #-- End mark previous
