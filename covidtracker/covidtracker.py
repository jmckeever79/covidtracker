import pandas as pd
import numpy as np
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

    def getstateframe(self, state):
        temp = self.df.loc[self.df['state']==state]
        temp = temp.groupby(['date']).sum()
        return temp

    def getcountyframe(self, state, county):
        return self.df.loc[self.df['state']==state].loc[self.df['county']==county]

    def getcounties(self, state):
        sf = self.getstateframe(state)
        return set(sf['county'])

    def _set_index(self, frame):
        return frame.set_index(['state', 'county'])

    def getperioddifference(self, enddate, days=1, stat='cases', pct_change=False):
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