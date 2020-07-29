import pandas as pd
import numpy as np
import copy
from functions import categories

class psiddata:
    def __init__(self, rawdata = None):
        if isinstance(rawdata, psidraw):
            self.rawdata = copy.deepcopy(rawdata)
        else:
            print('include raw data object')

    def getfamyeardata(self, df, namedf, year):
    #     Get list of that year's variable names
        varlist = list(namedf['Y' + str(year)])
    #     Remove missing vars/vars already included
        varlist = [x for x in varlist if x != 'missing']
        for var in varlist:
            df[var] = self.rawdata.rawfam[year][var]
        return df

    def getfamdata(self, datadict, namedf):
        # this function updates a dictionary with raw family data
        for year in range(1999, self.rawdata.lastyear + 2, 2):
            datadict.setdefault(year, pd.DataFrame())
            datadict[year] = self.getfamyeardata(datadict[year], namedf, year)
        return datadict

    def getinddata(self, df, namedf):
    #     Get list of that year's variable names
        varlist = []
        for year in range(1999, self.rawdata.lastyear + 1, 2):
            varlist = varlist + list(namedf['Y' + str(year)])
    #     Remove missing vars/vars already included
        varlist = [x for x in varlist if x != 'missing']
        for var in varlist:
            df[var] = self.rawdata.rawind[var]
        return df

    def merge_ind_fam(self, inddf, famdict):
        indid_arg = [
            'individual', 'survey information',
            'interview information', 'id (interview)',
            'missing'
            ]
        famid_arg = [
            'family', 'survey information',
            'interview information', 'family interview number (id)',
            'missing'
            ]
        indid_list = categories(self.rawdata.psidcw, indid_arg)
        famid_list = categories(self.rawdata.psidcw, famid_arg)
        newdict = {}
        # generate keep variable to track observations
        keep = [0] * len(inddf)
        for year in range(1999, self.rawdata.lastyear + 1, 2):
    # assign copy of family ID with family data name to individual data
            famname = famid_list['Y' + str(year)].values[0]
            indname = indid_list['Y' + str(year)].values[0]
            inddf[famname] = inddf[indname]
            inddf = inddf.merge(famdict[year], on = famname, how = 'left')
            # keep observations that have appeared in data at least once
            keep = np.where((inddf[famname] != 0) | (keep == 1), 1, 0)
            # generate person_id for merge with child data
        inddf['person_id'] = (self.rawdata.rawind['ER30001'] * 1000 +
                              self.rawdata.rawind['ER30002'])
        return inddf[keep == 1]

    # Crosswalk for pulling data and renaming
    def consdata(self, d = {}):
#         pull family raw consumption data
        for year in range(1999, self.rawdata.lastyear + 1, 2):
            varlist = self.rawdata.concw[year].dropna()
            for var in varlist:
                d[year][var] = self.rawdata.rawfam[year][var]
        return d


    def merge_child(self, inddf):
        # create markers for whether someone is a parent
        # subset for those with children?
        child = copy.deepcopy(self.rawdata.rawchild[
                              self.rawdata.rawchild['CAH9'] < 98])
        child['person_id'] = child['CAH3'] * 1000 + child['CAH4']
        # keep those with children
        child['max9'] = child.groupby('person_id')['CAH9'].transform(max)
        child = child.loc[(child['max9'] == child['CAH9']) |
                          (child['max9'].isnull())]
        child = child.drop_duplicates('person_id')
        child = child[['person_id', 'max9']]
        inddf = inddf.merge(child, on = 'person_id', how = 'left')
        # assign parent dummy variable
        inddf['isparent'] = np.where(inddf['max9'].notnull(), 1, 0)
        return inddf

    def outputdf(self, varobj, threshold= 0):
        # threshold refers to the minimum number of missing years allowed
        # per observation
        # start by initializing id variables
        varobj.update_rename(
            ['family_id'],
            ['family', 'survey information', 'interview information',
            'family interview number (id)', 'missing']
            )
        varobj.update_rename(
            ['indfam_id'],
            ['individual', 'survey information', 'interview information',
            'id (interview)', 'missing']
            )


        # family data
        famdict = {}
        famdict = self.getfamdata(famdict, varobj.fam_ndf)
        # consumption data
        famdict = self.consdata(famdict)
        # individual data
        inddf = pd.DataFrame()
        inddf = self.getinddata(inddf, varobj.ind_ndf)
        # merge individual and family data
        combineddf = self.merge_ind_fam(inddf, famdict)
        combineddf = self.merge_child(combineddf)
        # rename variables
        widedf = combineddf.rename(columns = varobj.renamedict)
        # only keep observations with enough data via threshold
        # observations with missing data in a year will have family_id = 0
        famlist = [value for value in varobj.renamedict.values()
                   if value.startswith('family_id')]
        # count number of missing years per row
        droparray = [0] * len(widedf)
        for col in famlist:
            rowarray = np.where(widedf[col] == 0, 1, 0)
            droparray += rowarray
        # keep observations that fall within threshold
        widedf = widedf[droparray <= threshold]

        # shift from wide to long
        finaldf = pd.wide_to_long(widedf, varobj.reshapelist,
                                  i = 'person_id', j = 'year')
        finaldf = finaldf.reset_index()
        finaldf['year'] = finaldf['year'].astype(int)
        return finaldf





class psidraw:
    def __init__(self):
        print('psidraw class: use .load() to import raw data')

# Function to read in psid variable name file
    def psidcw(self):
        vardata = pd.read_excel('psid.xlsx')
# split variable descriptions to allow for multiple identifying variables
        vardata['split_text'] = vardata['TEXT'].str.split('>')
        vardata['C0'] = vardata['TYPE']
        for cat in range(1, vardata['split_text'].str.len().max()):
            text = vardata['split_text'].str[cat]
            text = text.str.replace('\n\d\d', '')
            text = text.str.replace(':', '')
            vardata['C' + str(cat)] = text
        return vardata.fillna('missing')


    def initiate_dict(self):
        d = {}
# Function to read in family data
        for year in range(1999, self.lastyear + 2, 2):
            d[year] = pd.read_stata('familydata/fam' + str(year) + '.dta')
# Function to read in wealth data
        for year in range(1999, 2009, 2):
            wealth = pd.read_stata('wealthdata/wlth' + str(year) + '.dta')
            d[year] = d[year].join(wealth)
        return d

# Function to read in crosswalk to match up datasets across years
    def initiate_concw(self):
        concw = pd.read_excel("ConsExpCrosswalk.xlsx")
        concw.columns = ['name', 'oldname'] + list(
            range(1999, self.lastyear + 1, 2))
        concw = copy.deepcopy(concw.loc[2:])
        return concw


    def load(self, lastyear = 2017):
        self.lastyear = lastyear
        self.psidcw = self.psidcw()
        self.rawfam = self.initiate_dict()
        self.rawind = pd.read_stata('IndividualData/individual.dta')
        self.rawchild = pd.read_stata('ChildHistoryData/childhistory.dta')
        self.concw = self.initiate_concw()






class psidvars:
    def __init__(self, rawdata = None):
        if isinstance(rawdata, psidraw):
            self.reshapelist = []
            self.renamedict = {}
            self.fam_ndf = pd.DataFrame()
            self.ind_ndf = pd.DataFrame()
            self.lastyear = rawdata.lastyear
            self.psidcw = rawdata.psidcw
            self.concw = rawdata.concw
        else:
            print('include raw data object')

    def rename(self, namedf, namelist):
        # reshapelist is a list of names for wide to long function
        for name in [x for x in namelist if x not in self.reshapelist]:
            self.reshapelist.append(name)
        # append psid index dataframes for individual and family data
        self.fam_ndf = self.fam_ndf.append(
            namedf[namedf['TYPE'] == 'FAMILY PUBLIC'])
        self.ind_ndf = self.ind_ndf.append(
            namedf[namedf['TYPE'] == 'INDIVIDUAL'])
        assert(len(namedf) == len(namelist))
        # create dictionary with desired and raw data names + years
        rdict = {}
        for year in range(1999, self.lastyear + 1, 2):
            col_name = 'Y' + str(year)
            oglist = list(namedf[col_name])
            for i in range(0, len(oglist)):
                rdict[oglist[i]] = namelist[i] + str(year)
        return rdict

# creates a renaming dictionary for a namedf of PSID data
    def update_rename(self, namelist, clist):
        namedf = categories(self.psidcw, clist)
        newdict = self.rename(namedf, namelist)
        self.renamedict.update(newdict)

    def cons_renamedict(self):
        # adds consumption variables from psid crosswalk (available online)
        # to renamedict and reshapelist
        for index, row in self.concw.iterrows():
            for y in range(1999, self.lastyear + 1, 2):
                ogname = row[y]
                newname = row['name'].strip()
                self.renamedict[ogname] = newname + str(y)
                if newname not in self.reshapelist:
                    self.reshapelist.append(newname)
