# psid
The psid-work repository is designed to facilitate use of the Panel Survey of Income Dynamics. It can be used to pull, rename, and reshape publically-available PSID data.

## Downloading and formatting the raw data
This repo is currently designed to handle PSID data from 1999 onwards. All necessary data files come from the <a href = "https://simba.isr.umich.edu/Zips/ZipMain.aspx" >"packaged data"</a> section of the PSID download center. 
1. Start by expanding the "Family Files" section and download the zipped files for years 1999-2015. From 1999-2007, the supplemental wealth data are only available in separate files; simply expand the 1999, 2001, etc. year tabs to download them. 
2. Download the individual-level data. This comes as a single extract titled "Cross-year Individual: 1968-2017."
3. Download the PSID consumption data, titled "Consumption Expenditure Data: 1999-2013."

Once the data are all download, extract the zipped files into their respective folders within the repo:
<ul>
  <li> "FamilyData" should thus contain several folders labelled "fam1999er," "fam2003er," etc. </li>
  <li> "WealthData" will contain "wlth2003," "wlth2007," etc. </li>
  <li> "IndividualData" will contain "ind2017er" </li>
  <li> "ChildHistoryData" will contain "CAH85_17" </li>
</ul>
The next step is to run the "import_data.py" script in the "psid" folder. 

1. import_data takes all the raw data files from the PSID including the individual data and family data and converts them into a usable format to begin running analysis on.
