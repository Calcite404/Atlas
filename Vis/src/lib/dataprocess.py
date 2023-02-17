# package
import os
import numpy as np
import pandas as pd
import openpyxl


class Data:
    def __init__(self, filename):
        self.path = os.path.join(os.getcwd(), "data")
        self.filename = filename # the name of datafile with the suffix, eg. "data.xlsx", "data.csv"
        self.df = None

    def read_data(self, **kwargs):
        """
        Loading data
        :return: dataframe
        """
        datadir = self.path
        datafile = self.filename
        # datafilename = datafile.split(".")[0]
        datafilesuffix = datafile.split(".")[1]
        datafilepath = os.path.join(datadir, datafile)
        if datafilesuffix == "xlsx":
            self.df = pd.read_excel(datafilepath, **kwargs)
        elif datafilesuffix == "csv":
            self.df = pd.read_csv(datafilepath, **kwargs)

        return self.df

    def output_data(self, outfile, **kwargs):
        """
        Output processed dataframe that prepared for the further visualization
        :param outfile: output filename
        :param df: processed dataframe
        """
        datadir = self.path
        outputpath = os.path.join(datadir, outfile)
        self.df.to_csv(outputpath, **kwargs)


def deal_nans_int(dataframe, columns):
    """
    Replace NaNs with zero and convert the datatype for int objects in dataframe.
    :param dataframe: df
    :param columns: list of column names, specifying the columns that should be modified
    :return: df
    """
    for column in columns:
        dataframe[column] = dataframe[column].replace(np.NaN, 0)
        dataframe[column] = dataframe[column].astype(int)

    return dataframe


def data_process():
    """
    Pre-processing data - the process for cleaning and munging data
    Integrating data - the process for further organize all sub-parts
    :return: data_all_data: a dataframe that contains four sub-dataframes for covid, unemployment, personal_income,
    gdp_growth quarterly data
    """
    # covid-19
    covid = Data(filename="us_covid-19.csv")
    covid = covid.read_data()
    # GDP growth
    gdp_growth = Data(filename="GDP_growth.xlsx")
    gdp_growth = gdp_growth.read_data()
    gdp_growth = gdp_growth.rename(columns={'Unnamed: 0': 'State'})
    # personal income
    personal_income = Data(filename="personal_income_growth.xlsx")
    personal_income = personal_income.read_data()
    personal_income = personal_income.rename(columns={'Unnamed: 0': 'State'})
    # unemployment rate
    unemployment = Data(filename="unemployment_rate.xlsx")
    unemployment = unemployment.read_data(na_values=['–'])
    # mask
    mask_mandate = Data(filename="mask_mandate.csv")
    mask_mandate = mask_mandate.read_data()
    # hospital beds
    hospital_beds = Data(filename="hospital_beds.csv")
    hospital_beds = hospital_beds.read_data()
    hospital_beds = hospital_beds[hospital_beds['year'] >= 2019]

    # Data munging - The process for cleaning data, get the data statistics quarterly
    us_state_abbrev = {
        'Alabama': 'AL',
        'Alaska': 'AK',
        'American Samoa': 'AS',
        'Arizona': 'AZ',
        'Arkansas': 'AR',
        'California': 'CA',
        'Colorado': 'CO',
        'Connecticut': 'CT',
        'Delaware': 'DE',
        'District of Columbia': 'DC',
        'Florida': 'FL',
        'Georgia': 'GA',
        'Guam': 'GU',
        'Hawaii': 'HI',
        'Idaho': 'ID',
        'Illinois': 'IL',
        'Indiana': 'IN',
        'Iowa': 'IA',
        'Kansas': 'KS',
        'Kentucky': 'KY',
        'Louisiana': 'LA',
        'Maine': 'ME',
        'Maryland': 'MD',
        'Massachusetts': 'MA',
        'Michigan': 'MI',
        'Minnesota': 'MN',
        'Mississippi': 'MS',
        'Missouri': 'MO',
        'Montana': 'MT',
        'Nebraska': 'NE',
        'Nevada': 'NV',
        'New Hampshire': 'NH',
        'New Jersey': 'NJ',
        'New Mexico': 'NM',
        'New York': 'NY',
        'North Carolina': 'NC',
        'North Dakota': 'ND',
        'Northern Mariana Islands': 'MP',
        'Ohio': 'OH',
        'Oklahoma': 'OK',
        'Oregon': 'OR',
        'Pennsylvania': 'PA',
        'Puerto Rico': 'PR',
        'Rhode Island': 'RI',
        'South Carolina': 'SC',
        'South Dakota': 'SD',
        'Tennessee': 'TN',
        'Texas': 'TX',
        'Utah': 'UT',
        'Vermont': 'VT',
        'Virgin Islands': 'VI',
        'Virginia': 'VA',
        'Washington': 'WA',
        'West Virginia': 'WV',
        'Wisconsin': 'WI',
        'Wyoming': 'WY'
    }
    us_abbrev_to_state = {v: k for k, v in us_state_abbrev.items()}

    # unemployment rate
    unemployment = unemployment.dropna()
    unemployment['County Name/State Abbreviation'] = unemployment['County Name/State Abbreviation'].astype('str')
    unemployment['CountyName'] = unemployment['County Name/State Abbreviation'].map(lambda x: x.split(",")[0])
    unemployment['StateAbbreviation'] = unemployment['County Name/State Abbreviation'].map(lambda x: x[-2:])
    unemployment['StateAbbreviation'] = unemployment['StateAbbreviation'].str.upper()
    unemployment['Period'] = unemployment['Period'].map(lambda x: x.split(" ")[0])
    unemployment['Period'] = pd.to_datetime(unemployment['Period'], format='%b-%y')
    unemployment['Qtr'] = pd.PeriodIndex(pd.to_datetime(unemployment.Period), freq='Q')
    unemployment_qtr = unemployment.groupby(by=["StateAbbreviation", "Qtr"]).mean()
    unemployment_qtr = unemployment_qtr.reset_index()

    # personal income
    personal_income_qtr = personal_income.rename(
        columns={'2019:Q3': '2019Q3', '2019:Q4': '2019Q4', '2020:Q1': '2020Q1', '2020:Q2': '2020Q2',
                 '2020:Q3': '2020Q3', '2020:Q4': '2020Q4'})
    personal_income_qtr = pd.melt(personal_income_qtr, id_vars=['State'],
                                  value_vars=['2019Q3', '2019Q4', '2020Q1', '2020Q2', '2020Q3'])
    personal_income_qtr = personal_income_qtr.rename(columns={'variable': 'Qtr', 'value': 'Personal_Income_Change'})
    personal_income_qtr['StateAbbreviation'] = personal_income_qtr['State'].map(
        lambda x: us_state_abbrev[x.strip()])

    # GDP growth rate
    gdp_growth_qtr = gdp_growth.rename(
        columns={'2019:Q3': '2019Q3', '2019:Q4': '2019Q4', '2020:Q1': '2020Q1', '2020:Q2': '2020Q2',
                 '2020:Q3': '2020Q3', '2020:Q4': '2020Q4'})
    gdp_growth_qtr = pd.melt(gdp_growth_qtr, id_vars=['State'],
                             value_vars=['2019Q3', '2019Q4', '2020Q1', '2020Q2', '2020Q3'])
    gdp_growth_qtr = gdp_growth_qtr.rename(columns={'variable': 'Qtr', 'value': 'GDP_growth_rate'})
    gdp_growth_qtr['StateAbbreviation'] = gdp_growth_qtr['State'].map(lambda x: us_state_abbrev[x.strip()])

    # mask
    mask_mandate_s = mask_mandate[['State_Abrv', 'Mask_Mandate', 'Mandatory']]
    mask_mandate_s = mask_mandate_s.rename(columns={'State_Abrv': 'StateAbbreviation'})
    mask_mandate_s = mask_mandate_s.sort_values(by='StateAbbreviation')
    mask_mandate_s['Mask'] = mask_mandate_s['Mandatory'] + ", " + mask_mandate_s['Mask_Mandate'].astype(str)

    # cases/deaths
    covid['date'] = pd.to_datetime(covid['date'], format='%Y-%m-%d')
    covid = covid.sort_values(by='date')
    covid_qtr = covid.groupby(by=['date', 'state']).sum().reset_index()
    covid_qtr['Qtr'] = pd.PeriodIndex(covid_qtr.date, freq='Q')
    covid_qtr = covid_qtr[['date', 'Qtr', 'state', 'cases', 'deaths']]
    covid_qtr = covid_qtr.rename(columns={'state': 'State', 'cases': 'Cases', 'deaths': 'Deaths'})
    covid_qtr['StateAbbreviation'] = covid_qtr['State'].map(lambda x: us_state_abbrev[x.strip()])
    covid_qtr = covid_qtr.groupby(by=['Qtr', 'State']).max().reset_index()
    # covid_qtr['Deaths_Cases'] = covid_qtr['Deaths'].astype(str) + ',' + covid_qtr['Cases'].astype(str)

    # subtle refining; date: '2021-01-18'
    covid_p = covid.groupby(by=['date', 'state']).sum().reset_index()
    covid_p = covid_p[covid_p['date'] == '2021-01-18'][['date', 'state', 'cases', 'deaths']]
    covid_p = covid_p.rename(columns={'state': 'State'})
    covid_p['StateAbbreviation'] = covid_p['State'].map(lambda x: us_state_abbrev[x.strip()])
    unemployment_qtr_s = unemployment_qtr[['Qtr', 'StateAbbreviation', 'UnemploymentRate(%)']]
    unemployment_qtr_s['Qtr'] = unemployment_qtr['Qtr'].astype('str')
    personal_income_qtr_s = personal_income_qtr[['Qtr', 'StateAbbreviation', 'Personal_Income_Change']]
    gdp_growth_qtr_s = gdp_growth_qtr[['Qtr', 'StateAbbreviation', 'GDP_growth_rate']]
    covid_qtr_s = covid_qtr[['Qtr', 'StateAbbreviation', 'Deaths', 'Cases']]
    covid_qtr_s['Qtr'] = covid_qtr['Qtr'].astype('str')

    # Integrate
    df_all = [covid_qtr_s, unemployment_qtr_s, personal_income_qtr_s, gdp_growth_qtr_s]
    df_all = [df.set_index(['Qtr', 'StateAbbreviation']) for df in df_all]
    df_all = pd.concat(df_all, axis=1).reset_index().groupby(by=['Qtr', 'StateAbbreviation']).mean()
    df_all = df_all.reset_index()
    df_all['State'] = df_all['StateAbbreviation'].map(lambda x: us_abbrev_to_state[x.strip()])
    df_all = df_all.sort_values(by=['Qtr', 'StateAbbreviation'])
    # mask
    df_all['Mask'] = np.NaN
    for i in range(len(df_all)):
        df_all.loc[:, 'Mask'].iloc[i] = " ".join(
            mask_mandate_s[mask_mandate_s['StateAbbreviation'] == df_all['StateAbbreviation'].iloc[i]].loc[:,
            'Mask'].values)
    # cases/deaths
    df_all['Cases_p'] = np.NaN
    df_all['Deaths_p'] = np.NaN
    # cases
    for i in range(len(df_all)):
        df_all.loc[:, 'Cases_p'].iloc[i] = int(
            covid_p[covid_p['StateAbbreviation'] == df_all['StateAbbreviation'].iloc[i]].loc[:, 'cases'].values)
    # deaths
    for i in range(len(df_all)):
        df_all.loc[:, 'Deaths_p'].iloc[i] = int(
            covid_p[covid_p['StateAbbreviation'] == df_all['StateAbbreviation'].iloc[i]].loc[:, 'deaths'].values)

    # dealing with int-type columns
    df_all = deal_nans_int(df_all, ['Cases', 'Deaths', 'Cases_p', 'Deaths_p'])

    # compute CFR rate: case fatality ratio
    df_all['CFR'] = (df_all['Deaths'] / df_all['Cases']).round(3) * 100
    df_all['CFR_p'] = (df_all['Deaths_p'] / df_all['Cases_p']).round(3) * 100

    df_all_data = Data("covid_usa_all_data.csv")
    df_all_data.df = df_all.copy()
    df_all_data.output_data("covid_usa_all_data.csv")

    return df_all_data

