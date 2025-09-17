'''
This is code to run in Streamlit to analyse our Super options
Updated to github 12:00 17/09/2025
'''


import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import altair as alt

st.set_page_config(layout="wide")  # needs to be first command executed

table_start_age1 = 65
table_end_age1   = 105

SBal1       = 500000
SBal2       = 510000
CashBal     = 700000
OtherAssets = 25000

WithdrawTarget = 80005
#define these but not used as targets - used to spread withdrawals equally
Withdraw1Target    = 40000
Withdraw2Target    = 39000
WithdrawCashTarget = 21000

Age1 = 68
Age2 = 64
Start_Age1 = 68
Start_Age2 = 64

Wages2 = 50000

Cash_growth_percent = 2.9
Super_growth_percent = 3.0
Cost_of_living_adjust = 3.1
Pension_time_adjust = 2.0
Global_pension_scale_factor = 1.000

columnIdent = ['Age1','Age2','SBal1','SBal2','CashBal','OtherAssets','SDraw1','SDraw2', 'CashDraw', 'PensionY', 'TotalDraw', 'PensionSum', 'CashInterest', 'PForce1', 'PForce2', 'P2Wages']
politeLabels = ['RFS AGE','EW_AGE','RFS BALANCE','EW BALANCE','CASH BALANCE','OTHER ASSETS', '1RFS SUPER OUT', '2EW SUPER OUT', 'CASH OUT', 'PENSION', 'TOTAL INCOME', 'PENSION TOTAL', 'CASH INTEREST', 'FORCED RFS SUPER', 'FORCED EW SUPER', 'EW_WAGES']

def getPension(sum) :
    # returns pension amount based on total assets
    # PensionValidAge returns the age for person1 that data is valid for
    # (used for when to start indexing for inflation)
    max_limit = 1059000
    min_limit = 481500
    max_amount = 1732*26
    pensionValidAge = 68
    if sum > max_limit :
        return_val = 0
    elif sum < min_limit :
        return_val = max_amount
    else :
        return_val = max_amount * ((max_limit - sum) / (max_limit - min_limit))
    if Pension_inflate_enabled == True :
        return return_val * Global_pension_scale_factor
    else :
        return return_val

def getPensionValidAge() :
    return 68

def getSGCRate() :
    return 0.12

def getMinimumSuperRate(age) :
    # spell it out to avoid confusion
    if age >= 60 and age < 65 :
        return_val = 0.04
    elif age >= 65 and age < 75 :
        return_val = 0.05
    elif age >= 75 and age < 80 :
        return_val = 0.06
    elif age >= 80 and age < 85 :
        return_val = 0.07
    elif age >= 85 and age < 90 :
        return_val = 0.09
    elif age >= 90 and age < 95 :
        return_val = 0.11
    elif age >= 95 :
        return_val = 0.14
#    if Pension_inflate_enabled == True :
#        return return_val * Global_pension_scale_factor
#    else :
    return return_val
        
        
def addToDF(indexx, key, value)  :
    # use this in loop as might be modified in more than one place and need to add effects
    # specifically for SBal1, SBal2, CashBal, PForce1, PForce2, PensionSum
    # others can use replaceDF()
    df1.at[indexx,key] += int(value)

def replaceDF(indexx, key, value)  :
    # use this to initialise or fix values
    df1.at[indexx,key] = int(value)

def scaleDF(indexx, key, scale)  :
    # use this to percentahge increase current year values
    df1.at[indexx,key] =  int(df1.at[indexx,key] * float(scale))

def scaleNextDF(indexx, key, scale) :
    # use this to percentahge increase NEXT year values
    df1.at[indexx+1,key] =  int(df1.at[indexx,key] * float(scale))

        
#---- Place entities in sidebar
st.sidebar.header("RFS Pension Code simple",divider = 'grey')

#---- Work in 3 columns
#ccol1, ccol2, ccol3 = st.sidebar.columns(3)
#inv_mask = ccol3.checkbox("INVERT (Chroma Flip)", False)
#add_mask = ccol1.checkbox("ADD IN MASK", False)
#overlay_color = ccol2.color_picker("QR Code Color","#000000")
#----

#---- define a 2 column bit of side bar and populate
scol1, scol2 = st.sidebar.columns(2)
Age1 = scol1.slider("Person 1 Age",60,80,68)
Age2 = scol2.slider("Person 2 Age",60,80,64)
Start_Age1 = scol1.slider("Person 1 Start Super",Age1,80)
Start_Age2 = scol2.slider("Person 2 Start Super",Age2,80)
Wages2 = 1000*st.sidebar.slider("Person 2 Wages", 0, 100, int(Wages2/1000), 1, format="$%dk",help='Super calculated on this, but plotted as takehome 😠')

st.sidebar.divider()

#---- Full width of side bar and populate
WithdrawTarget = 1000*st.sidebar.slider("Desired Income pa", 20,150, int(WithdrawTarget/1000), 1, format="$%dk")
SBal1   = 1000*st.sidebar.slider("Super Balance Person 1", 10, 700, int(SBal1/1000), 10, format="$%dk")
SBal2   = 1000*st.sidebar.slider("Super Balance Person 2", 10, 700, int(SBal2/1000), 10, format="$%dk",help='Person 1 Super Balance at Start Age')
CashBal = 1000*st.sidebar.slider("Combined Cash Balance", 10, 1000, int(CashBal/1000), 10, format="$%dk", help = 'Person2 Super balance at PERSON1 start age')

#---- define a 2 column bit of side bar and populate
scol1, scol2 = st.sidebar.columns(2)
Cash_growth_percent  = scol1.slider("Cash Interest Rate",0.0,10.0,Cash_growth_percent, 0.1, format="%.1f%%")
Super_growth_percent = scol2.slider("Super Growth Rate",0.0,10.0,Super_growth_percent, 0.1, format="%.1f%%")

st.sidebar.divider()

table_start_age1 = scol1.slider("Table Start Age",55,Start_Age1, table_start_age1, 1, format="%dY")
table_end_age1   = scol2.slider("Table End Age",  90,115,        table_end_age1,   1, format="%dY")

numOfRows = table_end_age1 - table_start_age1 + 1 # ** recalc because we may have updated it

col1, col2 = st.sidebar.columns([2, 5])
Cost_of_living_factor = float(col2.slider("Cost of living adjustment (Deflation)",-.05, 5.0, Cost_of_living_adjust, 0.1, format="%.1f%%",
                                          help='Reduces value in super and cash to make graph\n"In Todays Dollars"'))
Cost_of_living_enabled = col1.checkbox("Enable Asset Deflation", False)

Pension_inflate_factor = float(col2.slider("Pension adjustment (Inflation)",-.05, 5.0, Pension_time_adjust, 0.1, format="%.1f%%",
                                help='Increases pension payment with time'))
Pension_inflate_enabled = col1.checkbox("Enable Pension Increases", False)

st.sidebar.write("Check 'Asset Deflation' for future in 'Todays dollars'  \n\
                 Check 'Pension Increases' to show Actual Dollars into future  \n\
                 **Only 1 at a time makes sense**")
st.sidebar.divider()

col1, col2 = st.sidebar.columns([2, 5])

Takehome_vary_factor = float(col2.slider("Takehome varies with time",-5.0, 5.0, float(0), 0.1, format="%.1f%%",
                                help='Alters Takehome amount with time'))
Takehome_vary_enabled = col1.checkbox("Enable Takehome $$ Change with Time", False)

st.sidebar.divider()

push_profit_back = st.sidebar.checkbox("Push Excess withdrawals back into Cash", False)

st.sidebar.divider()

col1, col2 = st.sidebar.columns([2, 5])

Oneoff_enabled = col1.checkbox("Enable One off payment", False)
Oneoff_Age = col2.slider("Withdrawal Age",Age1,80, Age1+3)
Oneoff_Amount = int(1000 * st.sidebar.slider("One off withdrawal amount",100, 250, int(0), 5, format="$%dk", help='Single withdrawal at given age'))

Age2Difference = Age2-Age1 # Age 2 compared to age 1, neg for younger

#------- Create dataframe
df1 = pd.DataFrame(index=np.arange(0, numOfRows), columns=columnIdent)
for i in range(0,numOfRows) :
    df1.loc[i] = 0

#------ Populate initial data
index = 0
for an_age in range(table_start_age1,table_end_age1+1) :
    df1.at[index,'Age1'] = an_age
    df1.at[index,'Age2'] = an_age +  Age2Difference 
    df1.at[index, 'PForce1'] = 0
    df1.at[index, 'PForce2'] = 0
    df1.at[index, 'OtherAssets'] = OtherAssets
    index += 1
# this places the initial Super balance in the starting age location
#if the plot doesn't start till later - then the initial balance is lost 
df1.at[Start_Age1 - table_start_age1, 'SBal1']   = SBal1
df1.at[Start_Age1 - table_start_age1, 'SBal2']   = SBal2
df1.at[Start_Age1 - table_start_age1, 'CashBal'] = CashBal

#--- Compose this before any values change - used at end in plot
# if Pension_inflate_enabled == True :
#     PensionString = f'Pension Inflated {Pension_inflate_factor:.1f}%'
# else :
#     PensionString = ''

PensionString   =  f' Pension Inflated  {Pension_inflate_factor:.1f}%' if Pension_inflate_enabled  == True else ''
DeflationString =  f' Deflation Enabled {Cost_of_living_factor:.1f}%' if Cost_of_living_enabled  == True else ''
TakehomeString  =  f' Takehome Varies   {Takehome_vary_factor:.1f}%' if Takehome_vary_enabled  == True else ''

ident_text = f'Desired= {WithdrawTarget:,.0f} Super1= {SBal1:,.0f}, Super2= {SBal2:,.0f} \
 Savings= {CashBal:,.0f} Other= {OtherAssets:,.0f} CashRate= {Cash_growth_percent:.1f}%  \
 SuperRate= {Super_growth_percent:,.1f}%' + PensionString + DeflationString + TakehomeString

#----- Run process loop
index = 0
for this_age1 in range(table_start_age1, table_end_age1) :

    #debugging trap
    if this_age1 == 90 :
        pass    

    #--- Here is where you do any changes for the year
    # Bump pension up
    validAge = getPensionValidAge()
    if Pension_inflate_enabled == True and this_age1 > validAge :
        Global_pension_scale_factor *= (1.00 + (Pension_inflate_factor/100.0))


    #Devalue assets
    if Cost_of_living_enabled == True and this_age1 > validAge :  # hmmm approx right
        scaleDF(index,'SBal1',   (1.00 - (Cost_of_living_factor/100.0)))
        scaleDF(index,'SBal2',   (1.00 - (Cost_of_living_factor/100.0)))
        scaleDF(index,'CashBal', (1.00 - (Cost_of_living_factor/100.0)))
                
    #Ramp target
    if Takehome_vary_enabled == True and this_age1 > validAge :  # hmmm approx right
        WithdrawTarget = int(WithdrawTarget * (1.00 + (Takehome_vary_factor/100)))

    # One off contributions (or withdrawals)
    if Oneoff_enabled == True :
        if Oneoff_Age == this_age1 :
            addToDF(index, 'CashBal', Oneoff_Amount)
            addToDF(index, 'CashDraw', Oneoff_Amount)
            

    #--- Add up assets and calculate pension
    cash_assets = df1.at[index,'SBal1'] + df1.at[index,'SBal2'] + df1.at[index,'CashBal']
    total_assets = cash_assets + df1.at[index,'OtherAssets']
    pension = 0
    if this_age1 >= Start_Age1 or this_age1 >= Start_Age2 - Age2Difference :
        pension = int(getPension(total_assets))
    
    df1.at[index,'PensionY'] = int(pension)
    if index > 0 :
        addToDF(index,'PensionSum', pension)

    # Work out Person 2 Salary first
    if this_age1 >= Start_Age1 and this_age1 < table_end_age1-1 : # StartAge1 = valid data
        if this_age1 < Start_Age2 - Age2Difference :  # if in gap
            replaceDF(index+1,'SBal2', df1.at[index, 'SBal2'])
            # add in notional super payment
            addToDF(index,'P2Wages', Wages2)
            addToDF(index+1,'SBal2', Wages2*getSGCRate())

    #--- Work out how much extra we need to make up income for year
    wanted = WithdrawTarget - pension

    #--- Add in wages from Person2
    wanted = wanted - df1.at[index,'P2Wages']
    


    # Work out ratio to take out
    Target1Avail = df1.at[index,'SBal1']
    Target2Avail = df1.at[index,'SBal2']
    CashAvail    = df1.at[index,'CashBal']
    #--- Correct
    totalAvail   = Target1Avail + Target2Avail + CashAvail
    #--- Emphasise keeping cash
    #totalAvail   = Target1Avail + Target2Avail + CashAvail + 100000
    #--- process
    if totalAvail > 0 :
        Withdraw1Target =  int(wanted * (Target1Avail/totalAvail))
        Withdraw2Target =  int(wanted * (Target2Avail/totalAvail))
    else :
        #needs to be defined even in not evaluated
        Withdraw1Target =  1
        Withdraw2Target =  1

    # Cash = remainder

    # Now - Something that can happen
    # WithdrawTargets are what we're aiming for to smoothly take out Super & Cash in proportion
    # But - there is also a minimum amount we have to take out - so if its greater than the Target
    # Then we want to take out less Cash
    # Its possible that the cash component goes negative.
    # you can simulate it going back into savings, or just allow it to make payment be above requested


    #--- Apply to Person1
    SBal = df1.at[index,'SBal1']
    if SBal > 0 and this_age1 >= Start_Age1 :
        val = int(Withdraw1Target )# - pension/3)
        min_super_figure = int(SBal*getMinimumSuperRate(df1.at[index,'Age1']))
        #-- was asking for less than minimum allowed
        if val < min_super_figure :
            val = min_super_figure
            addToDF(index,'PForce1', 1)  # bitmask B0
        #-- if we have enough to cover it
        if SBal > val :
            if this_age1 < table_end_age1-1 : # if row exists in table (dont overflow on last row)
                replaceDF(index+1,'SBal1', (SBal - val)) # new value
            addToDF(index,'SDraw1', val)
            wanted -= val
        else :
            replaceDF(index+1,'SBal1',0)  # force zero
            addToDF(index,'SDraw1', SBal)
            wanted -= SBal

    #--- Apply to Person2
    SBal = df1.at[index,'SBal2']
    if SBal > 0 and this_age1 >= Start_Age2 - Age2Difference  :
        val = int(Withdraw2Target ) #- pension/3)
        min_super_figure = int(SBal*getMinimumSuperRate(df1.at[index,'Age2']))
        #-- was asking for less than minimum allowed
        if val < min_super_figure :
            val = min_super_figure
            addToDF(index,'PForce2',1)
        #-- if we have enough to cover it
        if SBal > val :
            if this_age1 < table_end_age1-1 : # if row exists in table
                replaceDF(index+1,'SBal2', (SBal - val)) # new value
            addToDF(index,'SDraw2', val)
            wanted -= val
        else :
            replaceDF(index+1,'SBal2', 0) # force zero
            addToDF(index,'SDraw2', SBal)
            wanted -= SBal
    # else :
    #     #super is just sitting there - bump to next year
    #     if this_age1 >= Start_Age1 and this_age1 < table_end_age1-1 : # StartAge1 = valid data
    #         replaceDF(index+1,'SBal2', df1.at[index, 'SBal2'])
    #         if this_age1 < Start_Age2 - Age2Difference :
    #             # add in notional super payment
    #             addToDF(index+1, 'SBal2', 6000)



    #-- Apply to cash balance
    CBal = df1.at[index,'CashBal']
    if wanted < 0  and push_profit_back == False:
        replaceDF(index+1,'CashBal', df1.at[index,'CashBal'])
        pass
    elif CBal > 0 :
        val = wanted
        if CBal >= val :
            if this_age1 < table_end_age1 : # if row exists in table
                replaceDF(index+1,'CashBal', (CBal - val)) #new val
            addToDF(index,'CashDraw', val)
            wanted -= val
        else :
            wanted -= CBal
            replaceDF(index+1,'CashBal', 0)
            addToDF(index,'CashDraw', CBal)

  
    #-- Index balances for growth
    if this_age1 >= Start_Age1 and this_age1 < table_end_age1-1 :
        scaleDF(index+1,'SBal1', (1 + Super_growth_percent/100))

    if this_age1 >= Start_Age1 and this_age1 < table_end_age1-1 :
        scaleDF(index+1,'SBal2', (1 + Super_growth_percent/100))

    if this_age1 >= Start_Age1 and this_age1 < table_end_age1-1 :
        cash_inc = int(df1.at[index+1,'CashBal'] * (Cash_growth_percent/100))
        replaceDF(index+1, 'CashInterest', cash_inc)
        addToDF(index+1, 'CashBal', cash_inc)

    index += 1  
  
#--- Calculate column
df1['TotalDraw'] = df1['SDraw1'] + df1['SDraw2'] + df1['CashDraw'] + df1['PensionY']

#--- Relabel columns for display
df1.columns = politeLabels

###################  DISPLAY  ###################
st.write('##### ' + ident_text)


#--- First Plots
st.bar_chart(df1,  x='RFS AGE', y=['1RFS SUPER OUT', '2EW SUPER OUT', 'CASH OUT', 'PENSION','EW_WAGES'],color=["#00f", "#f88", "#0af","#a0a","#f00"])
st.line_chart(df1, x='RFS AGE', y=['1RFS SUPER OUT', '2EW SUPER OUT', 'CASH OUT', 'PENSION', 'EW_WAGES','TOTAL INCOME'],color=["#00f", "#f88", "#0af","#a0a","#f00","#0f0"])
st.line_chart(df1, x='RFS AGE', y=['RFS BALANCE','EW BALANCE','CASH BALANCE','OTHER ASSETS'],use_container_width = True)

#--- The Data Frame
df_styled = df1.style.format( 
    #{   #if all fields are numeric - can do formatter()
    #'PForce1':'{%s}','PForce2':'{%s}','RFSBALANCE':"{:,.0f}" }
    formatter="{:,.0f}"
)
st.write(df_styled)

#-- Alternate way of writing it out
#st.markdown(
#    df_styled.to_html(table_uuid="table_1"), unsafe_allow_html=True
#)

#--- Matplotlib - pyplot version
# fig, axs = plt.subplots(figsize=(12, 4))        # Create an empty Matplotlib Figure and Axes
# df1[['RFS SUPER OUT', 'EW SUPER OUT', 'CASH OUT', 'PENSION']].plot(kind = 'bar', stacked=True, grid=True, ax=axs, color=['r','g','b','m','y'])
# df1.plot('RFS AGE', ['RFS SUPER OUT', 'EW SUPER OUT', 'CASH OUT', 'PENSION', 'TOTAL INCOME'], ax=axs, grid=True, color=['r','g','b','m','y'])
# axs.annotate(ident_text, xy=(.015, .975), xycoords='figure fraction',
#            horizontalalignment='left', verticalalignment='top', fontsize=12)
# st.pyplot(fig)


#----   Bottom plot
# data_melted = pd.melt(df1, id_vars=['RFS AGE'], value_vars=['RFS SUPER OUT', 'EW SUPER OUT', 'CASH OUT', 'PENSION'],
#                var_name='variable', value_name='value')
# chart = (
    # alt.Chart(data_melted)
    # .mark_bar()
    # .encode(x="RFS AGE:N", y='value:Q', color = 'variable:N')
# )
# st.altair_chart(chart)
#------

#chart = (  # Actually sorts the data - which is not what you want
#    alt.Chart(data_melted).mark_bar().encode( alt.X("RFS AGE:N", sort='y'), alt.Y('value:Q'), color = 'variable:N')
#    # size="c", color="c", tooltip=["a", "b", "c"]
#)

#----------------------

st.write(Global_pension_scale_factor)
st.write(Pension_inflate_factor)
st.write(Pension_inflate_enabled)
