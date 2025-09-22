'''
This is code to run in Streamlit to analyse Super/Retirement options
---
Richard Smith Septemeber 2025
Computed Super using figures current at >20 Sept 2025
Some of the interface is in SuperPlot.py to strip out UI dependencies
Figures in getPensionDual(), getPensionSingle(), getSGCRate() and getMinimumSuperRate()
- may need to change to bring it up to date
Update the string at end of file to match updated data
'''


# Calculation figures are done direct into the dataframe, with abstract headings like SBal1, Age1 etc
# They are then replaced with 'translated names' by "df1.columns = politeLabels" later on in code
# These are passed to the 'SuperPlot.py routines via df1.
# SuperPlot.py also introduces some specific customisation strings.


import streamlit as st
import pandas as pd
#import numpy as np
#import matplotlib.pyplot as plt
import altair as alt
import random
from SuperPlot import display_barchart_plus
from SuperPlot import display_linechart

st.set_page_config(layout="wide")  # needs to be first command executed



#--  Initial default values for UI
table_end_age   = 105
SBal1          = 500000
SBal2          = 510000
CashBal        = 700000
OtherAssets    = 25000
WithdrawTarget = 80005
Age1       = 68
Age2       = 64
Start_Age1 = 68
Start_Age2 = 64
Wages1     = 10000
Wages2     = 50000
Cash_growth_percent   = 2.9
Super_growth_percent  = 3.0
Cost_of_living_adjust = 3.1
Pension_time_adjust   = 2.0

changetargetA_index =  5     # Index
changetargetA_amount = 10  # in k$
changetargetB_index =  25
changetargetB_amount = -15


# Global variables
Pension_scale_factor  = 1.000

# Internal names for the columns in the DataFrame - so code is general purpose
columnIdent = ['Index', 'Age1',   'Age2',  'SBal1',      'SBal2',     'CashBal',     'OtherAssets',  'SDraw1',        'SDraw2',       'CashDraw', 'PensionY', 'TotalDraw',   'PensionSum',    'Super1Interest',  'Super2Interest',  'CashInterest',  'PForce1',          'PForce2',         'P1Wages',   'P2Wages', 'debug', 'Excess']
# how to personalise output
politeLabels = ['INDEX','RFS AGE','EW AGE','RFS BALANCE','EW BALANCE','CASH BALANCE','OTHER ASSETS', 'RFS SUPER OUT', 'EW SUPER OUT', 'CASH OUT', 'PENSION', 'TOTAL INCOME', 'PENSION TOTAL', 'SUPER1 INTEREST', 'SUPER2 INTEREST', 'CASH INTEREST', 'FORCED RFS SUPER', 'FORCED EW SUPER', 'RFS WAGES', 'EW WAGES','DEBUG', 'EXCESS CASH']

Dual_pension_max_limit = 1074000
Dual_pension_min_limit = 481500
Dual_pension_max_amount = 1777*26
Single_pension_max_limit = 1074000
Single_pension_min_limit = 481500
Single_pension_max_amount = 1178*26

def getPensionDual(sum) :
    # returns pension amount based on total assets
    # figures for 20 Sept 2025++
    global Dual_pension_max_limit
    global Dual_pension_min_limit
    global Dual_pension_max_amount
    if sum > Dual_pension_max_limit :
        return_val = 0
    elif sum < Dual_pension_min_limit :
        return_val = Dual_pension_max_amount
    else :
        return_val = Dual_pension_max_amount * ((Dual_pension_max_limit - sum) / (Dual_pension_max_limit - Dual_pension_min_limit))
    if Pension_inflate_enabled == True :
        return return_val * Pension_scale_factor
    else :
        return return_val
    
def getPensionSingle(sum) :
    # returns pension amount based on total assets
    global Single_pension_max_limit
    global Single_pension_min_limit
    global Single_pension_max_amount
    if sum > Single_pension_max_limit :
        return_val = 0
    elif sum < Single_pension_min_limit :
        return_val = Single_pension_max_amount
    else :
        return_val = Single_pension_max_limit * ((Single_pension_max_limit - sum) / (Single_pension_max_limit - Single_pension_min_limit))
    if Pension_inflate_enabled == True :
        return return_val * Pension_scale_factor
    else :
        return return_val

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


#------------------------------------------------------
def process_p1p2(index) :
#------------------------------------------------------
# Processes where both people are receiving pension using joint figures
    df1.at[index,'debug'] = 'p1p2'
    if index >= numOfRows-1 :
        return

    ##-- Pension
    cash_assets = df1.at[index,'SBal1'] + df1.at[index,'SBal2'] + df1.at[index,'CashBal']
    total_assets = cash_assets + df1.at[index,'OtherAssets']
    pension = int(getPensionDual(total_assets))
    replaceDF(index,'PensionY', int(pension))
    addToDF(index,'PensionSum', pension)

    ##-- Target
    #--- Work out how much extra we need to make up income for year
    wanted = WithdrawTarget - pension  # WAGES ARE ZERO HERE - df1.at(index,'P1Wages') - df1.at(index,'P2Wages')

    # find minimum amounts have to withdraw
    min_super_figure1 = int(df1.at[index,'SBal1']*getMinimumSuperRate(df1.at[index,'Age1']))
    min_super_figure2 = int(df1.at[index,'SBal2']*getMinimumSuperRate(df1.at[index,'Age2']))
    
    # if we have a min figure returned - must have enough as factor is <1.00
    if wanted <= (min_super_figure1 + min_super_figure2) :
        # didnt want that much!, we're just going to have use minimum super
        addToDF(index,'PForce1', 1)  # bitmask B0
        addToDF(index,'PForce2', 1)  # bitmask B0
        pass

    # Work out ratio to take out
    Target1Avail = df1.at[index,'SBal1']
    Target2Avail = df1.at[index,'SBal2']
    CashAvail    = df1.at[index,'CashBal']
    CashAvail *= emphasise_cash
    totalAvail   = Target1Avail + Target2Avail + CashAvail

    # if index == 20 :
    #     pass  # debug catch

    #--- process
    if totalAvail <= 0 :
        pass
    else :
        Withdraw1Target =  int(wanted * (Target1Avail/totalAvail))
        Withdraw2Target =  int(wanted * (Target2Avail/totalAvail))
        
        # take out the minimums - as have to anyway    
        addToDF(index, 'SDraw1', min_super_figure1)
        addToDF(index, 'SDraw2', min_super_figure2)
        addToDF(index,'SBal1', -min_super_figure1)
        addToDF(index,'SBal2', -min_super_figure2)

        wanted -= min_super_figure1
        wanted -= min_super_figure2

        if wanted <= 0 :
            addToDF(index,'Excess', wanted)
            if push_profit_back == False :
                pass
            else :
                addToDF(index,'CashBal', -wanted)
                pass


        else :

            Withdraw1Target -= min_super_figure1
            Withdraw2Target -= min_super_figure2

            if Withdraw1Target < 0 :
                Withdraw1Target = 0
            if Withdraw2Target < 0 :
                Withdraw2Target = 0

            #-- if we have enough to cover it - try P1 first
            bal1 = df1.at[index,'SBal1']
            bal2 = df1.at[index,'SBal2']
            # balance out super funds
            if bal1 < Withdraw1Target :
                # bump 2 to make it up
                Withdraw2Target += Withdraw1Target - bal1
                Withdraw1Target = bal1
            if bal2 < Withdraw2Target :
                Withdraw2Target = bal2
            CashTarget = wanted - Withdraw1Target - Withdraw2Target

            # try P1 first
            if df1.at[index,'SBal1'] >= Withdraw1Target :
                addToDF(index,'SDraw1',   Withdraw1Target)
                addToDF(index+1,'SBal1', -Withdraw1Target)
            else :
                left = df1.at[index,'SBal1']
                addToDF(index,'SDraw1', left)  # use it all
                replaceDF(index+1,'SBal1',0)   # force zero
                Withdraw2Target += Withdraw1Target - left        # make P2 provide bit missing

            # try P2 second
            if df1.at[index,'SBal2'] >= Withdraw2Target :
                addToDF(index,'SDraw2',   Withdraw2Target)
                addToDF(index+1,'SBal2', -Withdraw2Target)
            else :
                left = df1.at[index,'SBal2']
                addToDF(index,'SDraw2', left)  # use it all
                replaceDF(index+1,'SBal2',0)   # force zero
                CashTarget += Withdraw2Target - left # make Cash provide bit missing

            # Do whatever you can with cash
            if df1.at[index,'CashBal'] >=   CashTarget :
                addToDF(index,'CashDraw',   CashTarget)
                addToDF(index+1,'CashBal', -CashTarget)
            else :
                left = df1.at[index,'CashBal']
                addToDF(index,'CashDraw', left)  # use it all
                replaceDF(index,'CashBal',0)   # force zero
    addToDF(index+1, 'SBal1', df1.at[index,'SBal1']) # copy to new year
    addToDF(index+1, 'SBal2', df1.at[index,'SBal2']) # copy to new year
    addToDF(index+1, 'CashBal', df1.at[index,'CashBal']) # copy to new year



#------------------------------------------------------
def process_p1(index) :
#------------------------------------------------------
# processes where only 1 person is receiving pension (p1) p2 on wages
    df1.at[index,'debug'] = 'p1'
    if index >= numOfRows-1 :
        return
    
    ##-- Pension
    cash_assets = df1.at[index,'SBal1'] + df1.at[index,'SBal2'] + df1.at[index,'CashBal']
    total_assets = cash_assets + df1.at[index,'OtherAssets']
    pension = int(getPensionSingle(total_assets))
    replaceDF(index,'PensionY', int(pension))
    addToDF(index,'PensionSum', pension)

    ##-- Target
    #--- Work out how much extra we need to make up income for year
    wanted = WithdrawTarget - pension - Wages2 

    # find minimum amounts have to withdraw
    min_super_figure = int(df1.at[index,'SBal1']*getMinimumSuperRate(df1.at[index,'Age1']))
    
    # if we have a min figure returned - must have enough to take out as factor is <1.00
    if wanted <= (min_super_figure ) :
        # didnt want that much!, we're just going to have use minimum super
        addToDF(index,'PForce1', 1)  # bitmask B0
        pass

    # Work out ratio to take out
    TargetAvail = df1.at[index,'SBal1']
    CashAvail    = df1.at[index,'CashBal']
    CashAvail *= emphasise_cash
    totalAvail   = TargetAvail + CashAvail

    #--- process
    if totalAvail <= 0 :
        pass
    else :
        WithdrawPTarget =  int(wanted * (TargetAvail/totalAvail))
        
        # take out the minimums - as have to anyway    
        addToDF(index, 'SDraw1', min_super_figure)
        addToDF(index,'SBal1', -min_super_figure)

        wanted -= min_super_figure

        if wanted <= 0 :
            addToDF(index,'Excess', wanted)
            if push_profit_back == False :
                pass
            else :
                addToDF(index,'CashBal', -wanted)
                pass
        else :
            WithdrawPTarget -= min_super_figure

            if WithdrawPTarget < 0 :
                WithdrawPTarget = 0

            CashTarget = wanted - WithdrawPTarget

            # take from super
            if df1.at[index,'SBal1'] >= WithdrawPTarget :
                addToDF(index,'SDraw1',   WithdrawPTarget)
                addToDF(index+1,'SBal1', -WithdrawPTarget)
            else :
                left = df1.at[index,'SBal1']
                addToDF(index,'SDraw1', left)  # use it all
                replaceDF(index+1,'SBal1',0)   # force zero
                CashTarget += WithdrawPTarget - left        # make P2 provide bit missing

            # Do whatever you can with cash
            if df1.at[index,'CashBal'] >=   CashTarget :
                addToDF(index,'CashDraw',   CashTarget)
                addToDF(index+1,'CashBal', -CashTarget)
            else :
                left = df1.at[index,'CashBal']
                addToDF(index,'CashDraw', left)  # use it all
                replaceDF(index,'CashBal',0)   # force zero

    #---

    addToDF(index, 'P2Wages', Wages2)
    addToDF(index+1, 'SBal1', df1.at[index,'SBal1']) # copy to new year
    addToDF(index+1, 'SBal2', df1.at[index,'SBal2']) # copy to new year
    addToDF(index+1, 'CashBal', df1.at[index,'CashBal']) # copy to new year    
    pass

#------------------------------------------------------
def process_p2(index) :
#------------------------------------------------------
# processes where only 1 person is receiving pension (p2) p1 on wages
    df1.at[index,'debug'] = 'p2'
    if index >= numOfRows-1 :
        return

    ##-- Pension
    cash_assets = df1.at[index,'SBal1'] + df1.at[index,'SBal2'] + df1.at[index,'CashBal']
    total_assets = cash_assets + df1.at[index,'OtherAssets']
    pension = int(getPensionSingle(total_assets))
    replaceDF(index,'PensionY', int(pension))
    addToDF(index,'PensionSum', pension)

    ##-- Target
    #--- Work out how much extra we need to make up income for year
    wanted = WithdrawTarget - pension - Wages1 

    # find minimum amounts have to withdraw
    min_super_figure = int(df1.at[index,'SBal2']*getMinimumSuperRate(df1.at[index,'Age2']))
    
    # if we have a min figure returned - must have enough as factor is <1.00
    if wanted <= (min_super_figure ) :
        # didnt want that much!, we're just going to have use minimum super
        addToDF(index,'PForce2', 1)  # bitmask B0
        pass

    # Work out ratio to take out
    TargetAvail = df1.at[index,'SBal2']
    CashAvail    = df1.at[index,'CashBal']
    CashAvail *= emphasise_cash
    totalAvail   = TargetAvail + CashAvail

    #--- process
    if totalAvail <= 0 :
        pass
    else :
        WithdrawPTarget =  int(wanted * (TargetAvail/totalAvail))
        
        # take out the minimums - as have to anyway    
        addToDF(index, 'SDraw2', min_super_figure)
        addToDF(index,'SBal2', -min_super_figure)

        wanted -= min_super_figure

        if wanted <= 0 :
            addToDF(index,'Excess', wanted)
            if push_profit_back == False :
                pass
            else :
                addToDF(index,'CashBal', -wanted)
                pass
        else :
            WithdrawPTarget -= min_super_figure

            if WithdrawPTarget < 0 :
                WithdrawPTarget = 0

            CashTarget = wanted - WithdrawPTarget

            # take from super
            if df1.at[index,'SBal2'] >= WithdrawPTarget :
                addToDF(index,'SDraw2',   WithdrawPTarget)
                addToDF(index+1,'SBal2', -WithdrawPTarget)
            else :
                left = df1.at[index,'SBal2']
                addToDF(index,'SDraw2', left)  # use it all
                replaceDF(index+1,'SBal2',0)   # force zero
                CashTarget += WithdrawPTarget - left        # make P2 provide bit missing

            # Do whatever you can with cash
            if df1.at[index,'CashBal'] >=   CashTarget :
                addToDF(index,'CashDraw',   CashTarget)
                addToDF(index+1,'CashBal', -CashTarget)
            else :
                left = df1.at[index,'CashBal']
                addToDF(index,'CashDraw', left)  # use it all
                replaceDF(index,'CashBal',0)   # force zero

    addToDF(index, 'P1Wages', Wages1)
    addToDF(index+1, 'SBal1', df1.at[index,'SBal1']) # copy to new year
    addToDF(index+1, 'SBal2', df1.at[index,'SBal2']) # copy to new year
    addToDF(index+1, 'CashBal', df1.at[index,'CashBal']) # copy to new year    
    pass

#------------------------------------------------------
def process_presuper(index) :
#------------------------------------------------------
# processes where neither person is receiving pension - both on wages

    df1.at[index,'debug'] = 'none'
    addToDF(index, 'P1Wages', Wages1)
    addToDF(index, 'P2Wages', Wages2)
    addToDF(index+1, 'SBal1', df1.at[index,'SBal1']) # copy to new year
    addToDF(index+1, 'SBal2', df1.at[index,'SBal2']) # copy to new year
    addToDF(index+1, 'CashBal', df1.at[index,'CashBal']) # copy to new year
    addToDF(index+1,'SBal1', Wages1*getSGCRate())   # add SGC
    addToDF(index+1,'SBal2', Wages2*getSGCRate())   # add SGC
    pass

        
##------------------------------------------------------
##-------------- BEGIN UI DESCRIPTION ------------------

#---- Place entities in sidebar
st.sidebar.header("RFS Pension Code V1.00",divider = 'rainbow')

with st.sidebar.expander("✔️✔️✔️😀 Age-Wages-Super 😀✔️✔️✔️  ▶️", True) :
    st.write('---')
    #---- define a 2 column bit of side bar and populate
    scol1, scol2 = st.columns(2)
    Age1 = scol1.slider("Person 1 Age",60,80,68)
    Age2 = scol2.slider("Person 2 Age",60,80,64)
    st.write('---')
    Start_Age1 = scol1.slider("Person 1 Start Super",Age1,80)
    Start_Age2 = scol2.slider("Person 2 Start Super",Age2,80)
    Wages1 = 1000*st.slider("Person 1 Wages", 0, 100, int(Wages1/1000), 1, format="$%dk",help='Super calculated on this, but plotted as takehome 😠')
    Wages2 = 1000*st.slider("Person 2 Wages", 0, 100, int(Wages2/1000), 1, format="$%dk",help='Super calculated on this, but plotted as takehome 😠')
    st.write('---')
    SBal1   = 1000*st.slider("Super Balance Person 1", 10, 700, int(SBal1/1000), 10,   format="$%dk", help='Person 1 Super Balance at Start of plot')
    SBal2   = 1000*st.slider("Super Balance Person 2", 10, 700, int(SBal2/1000), 10,   format="$%dk", help='Person 2 Super Balance at Start of plot')
    CashBal = 1000*st.slider("Combined Cash Balance", 10, 1000, int(CashBal/1000), 10, format="$%dk", help='Cash Balance at Start of plot')
    st.write('---')
    table_end_age   = st.slider("Table End Age",  80,115, table_end_age, 1, format="%dY")


WithdrawTarget = 1000*st.sidebar.slider("Desired Income pa", 20,150, int(WithdrawTarget/1000), 1, format="$%dk")

#---- define a 2 column bit of side bar and populate
scol1, scol2 = st.sidebar.columns(2)
Cash_growth_percent  = scol1.slider("Cash Interest Rate",0.0,10.0,Cash_growth_percent, 0.1, format="%.1f%%")
Super_growth_percent = scol2.slider("Super Growth Rate",0.0,10.0,Super_growth_percent, 0.1, format="%.1f%%")

st.sidebar.write("---")

# imbalanced side bar columns
col1, col2 = st.sidebar.columns([2, 5])
Cost_of_living_factor = float(col2.slider("Cost of living adjustment (Deflation)",-.05, 5.0, Cost_of_living_adjust, 0.1, format="%.1f%%",
                                          help='Reduces value in super and cash to make graph\n"In Todays Dollars"'))
Cost_of_living_enabled = col1.checkbox("Enable Asset Deflation", True)

st.sidebar.write("Check 'Asset Deflation' for future in 'Todays dollars'  \n\
                 Check 'Pension Increases' (& prob Takehome increase) to show Actual Dollars into future.  \
                 **Only 'Asset' or other pair at a time makes sense**")

col1, col2 = st.sidebar.columns([2, 5])

Pension_inflate_factor = float(col2.slider("Pension adjustment (Inflation)",-.05, 5.0, Pension_time_adjust, 0.1, format="%.1f%%",
                                help='Increases pension payment with time'))
Pension_inflate_enabled = col1.checkbox("Enable Pension Increases", False)

col1, col2 = st.sidebar.columns([2, 5])
Takehome_vary_factor = float(col2.slider("Takehome varies with time",-5.0, 5.0, float(0), 0.1, format="%.1f%%",
                                help='Alters Takehome amount with time zzzzz'))
Takehome_vary_enabled = col1.checkbox("Enable Takehome $$ Change with Time", False)
st.sidebar.write('---')

col1, col2, col3 = st.sidebar.columns([4, 4, 9])
youngest = min(Age1,Age2)             ## calc now - as need now
numOfRows = table_end_age - youngest  ## calc now - as need now

changetargetA_enable = col1.checkbox("Enable Change A", False)
changetargetA_index =  col2.selectbox("Index from start", range(numOfRows-1), changetargetA_index, help="By index to avoid confusion of who's age, Use 'Years' for index to see")
changetargetA_amount = 1000*col3.slider("Amount1", -100,100,changetargetA_amount,10,"$%dk")

changetargetB_enable = col1.checkbox("Enable Change B", False)
changetargetB_index =  col2.selectbox("Index from start ", range(numOfRows-1), changetargetB_index, help="By index to avoid confusion of who's age, Use 'Years' for index to see")
changetargetB_amount = 1000*col3.slider("Amount2", -100,100,changetargetB_amount,10,"$%dk")

st.sidebar.divider()

push_profit_back = st.sidebar.checkbox("Push Excess withdrawals back into Cash", False)
emphasise_cash = st.sidebar.slider("Emphasise Getting rid of cash", 0.33, 3.0, float(1.0), 0.01, format="%.1f",
                                help='Alters Ratio of cash to Super withdrawn')
st.sidebar.divider()


with st.sidebar.expander("✔️✔️✔️ 👍One Off withdrawals👍 ✔️✔️✔️ ▶️", True) :
    col1, col2 = st.columns([2, 5])

    Oneoff_enabled = col1.checkbox("Enable One off payment", False)
    Oneoff_Index = col2.slider("Index from start",0, numOfRows-1, 2, help="By index to avoid confusion of who's age, Use 'Years' for index to see")
    Oneoff_Amount = int(1000 * st.slider("One off withdrawal amount",100, 250, int(0), 5, format="$%dk", help='Single withdrawal at given age'))
    st.write("---")
    radio_vals = ["CASH", "PENSION1", "PENSION2", "PENSIONBOTH", "ALL"]
    suck_lump_from = st.radio(
        "Take Lump Sum from",
        radio_vals,
        captions=[
            ":blue[From CASH]",
            ":red[From Pension 1]",
            ":orange[From Pension 2]",
            ":green[From Both Pensions]",
            ":blue[From All]"
        ],
        horizontal = True
    )

#--- Compose these before any values change - used at end in plot
DeflationString =  f' ***Deflation Enabled {Cost_of_living_factor:.1f}%***,' if Cost_of_living_enabled  == True else ''
PensionString   =  f' Pension Inflated  {Pension_inflate_factor:.1f}%,' if Pension_inflate_enabled  == True else ''
TakehomeString  =  f' Takehome Varies   {Takehome_vary_factor:.1f}%,' if Takehome_vary_enabled  == True else ''
PushBackString  =  f' [Excess Back to Cash]'  if push_profit_back  == True else ''
ChangeAString  =   f' Takehome StepA {changetargetA_amount:,.0f} at index {changetargetA_index},' if changetargetA_enable  == True else ''
ChangeBString  =   f' Takehome StepB {changetargetB_amount:,.0f} at index {changetargetB_index},' if changetargetB_enable  == True else ''
OneOffString   =   f' OneOff Withdrawal {Oneoff_Amount:,.0f} at index {Oneoff_Index},' if Oneoff_enabled == True else ''

ident_text = f'Desired= {WithdrawTarget:,.0f}, Super1= {SBal1:,.0f}, Super2= {SBal2:,.0f}, \
  Savings= {CashBal:,.0f}, Other= {OtherAssets:,.0f}, CashRate= {Cash_growth_percent:.1f}%, \
  SuperRate= {Super_growth_percent:,.1f}%,' + DeflationString + PensionString + TakehomeString + PushBackString \
  + ChangeAString + ChangeBString + OneOffString


if 0 :
    "---"  # modulation frame start of RFS simulation of GFC
    col1, col2, space = st.sidebar.columns([2, 2, 5])
    Munge_Bal1 = col1.checkbox("Allow Changes to Super 1 Balance", False)
    Munge_Bal2 = col2.checkbox("Allow Changes to Super 2 Balance", False)

    df2 = pd.DataFrame(index=range(0, numOfRows) )#, columns=columnIdent)
    df2.loc[:,'Index'] = range(numOfRows)
    df2.loc[:,'Age1'] = range(Age1, numOfRows+Age1)
    df2.loc[:,'Age2'] = range(Age2, numOfRows+Age2)
    df2.loc[:,'Super1Factor'] = 1.0
    df2.loc[:,'Super2Factor'] = 1.0

    edited_df2 = st.data_editor(df2)
    st.write('---')

##------------------------------------------------------
##--------------- END UI DESCRIPTION -------------------

# previously done - but logically done here
# youngest = min(Age1,Age2)
# numOfRows = table_end_age - youngest

#------- Create dataframe
df1 = pd.DataFrame(index=range(numOfRows), columns=columnIdent)
for i in range(0,numOfRows) :
    df1.loc[i] = 0

#------ Populate initial data

for dfindex in range(numOfRows) : # in loop way - or -
#    df1.at[dfindex,'Age1'] = dfindex + Age1
    df1.at[dfindex,'Age2'] = dfindex + Age2
    df1.at[dfindex, 'PForce1'] = 0
    df1.at[dfindex, 'PForce2'] = 0
    df1.at[dfindex, 'OtherAssets'] = OtherAssets
#    df1.at[dfindex, 'Index'] = dfindex
# - or - native dataframe way
df1.loc[:,'Index'] = range(numOfRows)    
df1.loc[:,'Age1']  = range(Age1, numOfRows+Age1)

# this places the initial Super balance in the starting age location
df1.at[0, 'SBal1']   = SBal1
df1.at[0, 'SBal2']   = SBal2
df1.at[0, 'CashBal'] = CashBal


##----------------------------------------------
##------- Begin processing loop ----------------

for dfindex in range(numOfRows) :

    #Ramp target
    if Takehome_vary_enabled == True :
        WithdrawTarget = int(WithdrawTarget * (1.00 + (Takehome_vary_factor/100)))
    
    # One off contributions (or withdrawals)
    if Oneoff_enabled == True :
        if Oneoff_Index == dfindex:
            match suck_lump_from :
                case 'CASH' : 
                    addToDF(dfindex, 'CashBal',  -Oneoff_Amount)
                    addToDF(dfindex, 'CashDraw',  Oneoff_Amount)
                case 'PENSION1' : 
                    addToDF(dfindex, 'SBal1', -Oneoff_Amount)
                    addToDF(dfindex, 'SDraw1', Oneoff_Amount)
                case 'PENSION2' : 
                    addToDF(dfindex, 'SBal2', -Oneoff_Amount)
                    addToDF(dfindex, 'SDraw2', Oneoff_Amount)
                case 'PENSIONBOTH' : 
                    addToDF(dfindex, 'SBal1', -Oneoff_Amount/2)
                    addToDF(dfindex, 'SDraw1', Oneoff_Amount/2)
                    addToDF(dfindex, 'SBal2', -Oneoff_Amount/2)
                    addToDF(dfindex, 'SDraw2', Oneoff_Amount/2)
                case 'ALL' : 
                    addToDF(dfindex, 'SBal1',   -Oneoff_Amount/3)
                    addToDF(dfindex, 'SDraw1',   Oneoff_Amount/3)
                    addToDF(dfindex, 'SBal2',   -Oneoff_Amount/3)
                    addToDF(dfindex, 'SDraw2',   Oneoff_Amount/3)
                    addToDF(dfindex, 'CashBal', -Oneoff_Amount/3)
                    addToDF(dfindex, 'CashDraw', Oneoff_Amount/3)
     
    # Bump pension up by annual increment
    if Pension_inflate_enabled == True :
        Pension_scale_factor *= (1.00 + (Pension_inflate_factor/100.0))

    # Devalue assets (Simulate inflation)
    if Cost_of_living_enabled == True :
        scaleDF(dfindex,'SBal1',   (1.00 - (Cost_of_living_factor/100.0)))
        scaleDF(dfindex,'SBal2',   (1.00 - (Cost_of_living_factor/100.0)))
        scaleDF(dfindex,'CashBal', (1.00 - (Cost_of_living_factor/100.0)))
    
    # # crash the market - before you calc returns!
    # if Munge_Bal1 == True :
    #     # keep a copy
    #     old_bal1 = df1['SBal1']
    #     scaleDF(dfindex, 'SBal1', edited_df2.at[dfindex,'Super1Factor'])
    # if Munge_Bal2 == True :
    #     scaleDF(dfindex, 'SBal2', edited_df2.at[dfindex,'Super2Factor'])

    # change target withdrawal amount at 2 ages
    if changetargetA_enable == True :
        if changetargetA_index == dfindex :
            WithdrawTarget += changetargetA_amount
    if changetargetB_enable == True :
        if changetargetB_index == dfindex :
            WithdrawTarget += changetargetB_amount

    # Where the main processing gets called
    if df1.at[dfindex,'Age1']    >= Start_Age1 and df1.at[dfindex,'Age2'] >= Start_Age2 :
        process_p1p2(dfindex)
    elif df1.at[dfindex,'Age1']  >= Start_Age1 and df1.at[dfindex,'Age2']  < Start_Age2 :
        process_p1(dfindex)
    elif df1.at[dfindex,'Age1']  < Start_Age1 and df1.at[dfindex,'Age2']  >= Start_Age2 :
        process_p2(dfindex)
    else :
        process_presuper(dfindex)

    # # put it back - wrong - just placeholder
    # if Munge_Bal1 == True :
    #     df1['SBal1'] = old_bal1

    #-- Index balances for growth
    if dfindex < numOfRows-1 :
        super1_inc =  int(df1.at[dfindex,'SBal1'] * (Super_growth_percent/100))
        replaceDF(dfindex, 'Super1Interest', super1_inc)
        addToDF(dfindex+1, 'SBal1', super1_inc)
        super2_inc =  int(df1.at[dfindex,'SBal2'] * (Super_growth_percent/100))
        replaceDF(dfindex, 'Super2Interest', super2_inc)
        addToDF(dfindex+1, 'SBal2', super2_inc)

        # scaleDF(dfindex+1,'SBal1', (1 + Super_growth_percent/100))
        # scaleDF(dfindex+1,'SBal2', (1 + Super_growth_percent/100))
        cash_inc = int(df1.at[dfindex,'CashBal'] * (Cash_growth_percent/100))
        replaceDF(dfindex, 'CashInterest', cash_inc)
        addToDF(dfindex+1, 'CashBal', cash_inc)

##---------------------   end of loop ------------------
##------------------------------------------------------

#--- Calculate total column
df1['TotalDraw'] = df1['SDraw1'] + df1['SDraw2'] + df1['CashDraw'] + df1['PensionY'] + df1['P1Wages'] + df1['P2Wages']

##-----------------  Start of display ------------------
##------------------------------------------------------

#--- Relabel columns for display  
#--- everything from here on down is indiviualised  'RFS AGE' not 'Age1' etc
df1.columns = politeLabels  # df1 headings changed

st.write('##### ' + ident_text)

display_barchart_plus(st, numOfRows, Age1, Age2, df1) # Also does some UI output to main window
st.write('---')
display_linechart(df1,  2)  # 2 = uses domain2 etc 
st.write('---')
display_linechart(df1,  3)
st.write('---')

#--- Print the Data Frame - so can copy and pull into excel etc
df_styled = df1.style.format( 
    #if all fields are numeric - can do formatter(), else have to name them all..
    #'PForce1':'{%s}','PForce2':'{%s}','RFSBALANCE':"{:,.0f}",'debug':'{%s}' } 
    #formatter="{:,.0f}"
    thousands=','  # does enough for me
)
st.write(df_styled)

# Has EM and en Spaces in string to make look nice
st.write("Data valid as at 22 Sept 2025" + '  \n' + 
         f"Dual Max   =  {Dual_pension_max_limit:,.0f},  " + f" Dual Min =  {Dual_pension_min_limit:,.0f},  " + f" Dual MaxAmount =  {Dual_pension_max_amount:,.0f}    " + '  \n' + 
         f"Single Max =  {Single_pension_max_limit:,.0f}, " + f"Single Min =  {Single_pension_min_limit:,.0f}, " + f"Single MaxAmount =  {Single_pension_max_amount:,.0f}")
st.write("© Richard and Elly  -  TI 2025")

##------------------------------------------------------
##------------------  End of display -------------------


