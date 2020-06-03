import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import os
from datetime import datetime

class CovidTracker(object):
    repos = 'C:/Users/jj/git/data/covid-19-data'
    uscountyfile = os.path.join(repos, 'us-counties.csv')
    mostrecentdate = None

    def load_counties(self):
        self.df = pd.read_csv(self.uscountyfile)
        self.df = self.df.drop('fips', axis=1)

    def getmostrecentdate(self):
        if self.mostrecentdate is None:
            self.mostrecentdate = self.df['date'].max()
        return self.mostrecentdate

    def getdateframe(self, date, indexed=False):
        temp = self.df.loc[self.df['date']==date]
        if indexed:
            temp = temp.set_index(['state', 'county'])
        return temp

    def getstateframe(self, state, group_counties=False):
        temp = self.df.loc[self.df['state']==state]
        groups = ['date']
        if (group_counties):
            groups.append('county')
        temp = temp.groupby(groups).sum()
        return temp

    def getcountyframe(self, state, county):
        temp = self.df.loc[self.df['state']==state].loc[self.df['county']==county]
        temp = temp.groupby(['date']).sum()
        return temp

    def getcounties(self, state):
        sf = self.getstateframe(state)
        return set(sf['county'])

    def _set_index(self, frame):
        return frame.set_index(['state', 'county'])

    def getperiodchange(self, enddate, days=1, stat='cases', pct_change=False):
        endframe = self.getdateframe(enddate, indexed=False)
        ts = pd.Timestamp(enddate)
        offset = '1 day' if days==1 else '{0} days'.format(days)
        startdate = str((ts - pd.Timedelta(offset)).date())
        startframe = self.getdateframe(startdate, indexed=False)

        endframe = self._set_index(endframe)
        startframe = self._set_index(startframe)

        diff = endframe[stat]-startframe[stat]
        if pct_change:
            diff = diff/startframe[stat]
        return diff

    def getdiffseries_date(self, stat='cases'):
        by_date = self.df.groupby(['date']).sum()[stat]
        return by_date.diff()

    def getdiffseries_state(self, state, stat='cases'):
        sf = self.getstateframe(state)[stat]
        return sf.diff()

    def diffseries_county(self, state, county, stat='cases'):
        cf = self.getcountyframe(state, county)[stat]
        return cf.diff()

    def getdeathspercase(self, date):
        return self._getdeathspercase_helper(self.getdateframe(date))

    def getdeathspercase_state(self, state):
        return self._getdeathspercase_helper(self.getstateframe(state))
    
    def getdeathspercase_county(self, state, county):
        return self._getdeathspercase_helper(self.getcountyframe(state, county))

    def _getdeathspercase_helper(self, df):
        rate = (df['deaths']/df['cases']).rename('deaths per case')
        return pd.concat([df, rate], axis=1, join='inner')

    def _getstateframe_helper(self, states, stat='cases'):
        if (isinstance(states, str)):
            states = [states]
        result = None
        for state in states:
            state_frame = self.getstateframe(state)[stat].rename(state)
            if (result is None):
                result = state_frame
            else:
                result = pd.concat([result, state_frame], axis=1, join='inner')
        return result

    def plot_state(self, states, stat='cases'):
        frame = self._getstateframe_helper(states, stat)
        frame.plot()
        plt.show()

    def _getcountyframe_helper(self, counties, stat='cases'):
        result = None
        for t in counties:
            state = t[0]
            county = t[1]
            name = '{0}, {1}'.format(county, state)
            county_frame = self.getcountyframe(state, county)
            if (county_frame.empty):
                continue
            county_frame = county_frame[stat].rename(name)
            if (result is None):
                result = county_frame
            else:
                result = pd.concat([result, county_frame], axis=1, join='inner')
        return result

    def plot_county(self, counties, stat='cases'):
        frame = self._getcountyframe_helper(counties, stat)
        frame.plot()
        plt.show()

