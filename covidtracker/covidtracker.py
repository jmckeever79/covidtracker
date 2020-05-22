import pandas as pd
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

    def getdateframe(self, date):
        return self.df.loc[self.df['date']==date]

    def getstateframe(self, state):
        temp = self.df.loc[self.df['state']==state]
        temp = temp.groupby(['date']).sum()
        return temp

    def getcountyframe(self, state, county):
        return self.df.loc[self.df['state']==state].loc[self.df['county']==county]

    def getcounties(self, state):
        sf = self.getstateframe(state)
        return set(sf['county'])