import os
os.chdir("../")

# Set Year of which the data runs to here! Only use the ast two digits (i.e. 2012 = 12)
# This should be all you have to change in this file unless naming conventions change or a data series is not nenewed etc.
yr = "17"
yrn = 17

# Format Individual Data
# NEED TO SET TO SUBFOLDERS
path = "IndividualData/ind20" + yr + "er/"
folderpath = os.getcwd() +"\IndividualData\ind20" + yr + "er"
readpath = path + "IND20" + yr + "ER.do"
writepath = path + "IND20" + yr + "ERnew.do"
with open(readpath, "r") as file:
    fix = file.read()
    fix = fix.replace('[path]\\', '')
with open(writepath, "w") as file:
    file.write("cd " + folderpath)
    file.write(fix)
    file.write("\nsave ..\individual, replace;")

# Format Child History Data
path = "ChildHistoryData/cah85_" + yr + "/"
folderpath = os.getcwd() +"\ChildHistoryData\cah85_" + yr
readpath = path + "CAH85_" + yr + ".do"
writepath = path + "CAH85_" + yr + "new.do"
with open(readpath, "r") as file:
    fix = file.read()
    fix = fix.replace('[path]\\', '')
with open(writepath, "w") as file:
    file.write("cd " + folderpath)
    file.write(fix)
    file.write("\nsave ..\childhistory, replace;")


# Format Family Data
for y in range(1999, 2002+yrn, 2):
    yr = str(y)
    path = "FamilyData/fam{}er".format(yr)
    readpath = path + "/FAM{}ER.do".format(yr)
    writepath = path + "/FAM{}ERnew.do".format(yr)
    with open(readpath ,"r") as file:
        fix = file.read()
        fix = fix.replace('[path]\\', '')
    with open(writepath ,"w") as file:
        file.write(fix)

master = open("FamilyData/formatfam1.do", "w")
famfolder = os.getcwd() +"\FamilyData"
master.write("cd " + "\"" + famfolder + "\"\n")
master.write("set maxvar 10000 \n")
master.write("#delimit ; \n")
master.write("forval i = 1999(2)20" + yr + "{; \n")
master.write("cd " +  "\"" + famfolder + "\FAM`i'er\"; \n" )
master.write("do \"FAM`i'ERnew.do\"; \n")
master.write("save \"../fam`i'.dta\", replace; \n\n")
master.write("};")
master.close()

# Format Wealth Data (This only runs up to 2007)
for y in range(1999, 2009, 2):
    yrr = str(y)
    path = "WealthData/wlth{}".format(yrr)
    readpath = path + "/wlth{}.do".format(yrr)
    writepath = path + "/wlth{}new.do".format(yrr)
    with open(readpath ,"r") as file:
        fix = file.read()
        fix = fix.replace('[path]\\', '')
    with open(writepath ,"w") as file:
        file.write(fix)

master = open("WealthData/formatwealth1.do", "w")
wealthfolder = os.getcwd() +"\WealthData"
master.write("cd " + "\"" + wealthfolder + "\"\n")
master.write("set maxvar 10000 \n")
master.write("#delimit ; \n")
master.write("forval i = 1999(2)2007{; \n")
master.write("cd " +  "\"" + wealthfolder + "\wlth`i'\"; \n" )
master.write("do \"wlth`i'new.do\"; \n")
master.write("save \"../wlth`i'.dta\", replace; \n\n")
master.write("};")
master.close()

# master do file
with open("format_data.do", "w") as file:
    # family data
    file.write("clear \n")
    file.write("cd " + os.getcwd() + "\n")
    file.write("do FamilyData\\formatfam1.do" + "\n")
    # wealth data
    file.write("clear \n")
    file.write("cd " + os.getcwd() + "\n")
    file.write("do WealthData\\formatwealth1.do \n")
    # individual data
    file.write("cd " + os.getcwd() + "\n")
    file.write("do IndividualData\ind20" + yr + "er\IND20" + yr + "ERnew.do" + "\n")
    # child history data
    file.write("cd " + os.getcwd() + "\n")
    file.write("do ChildHistoryData\cah85_" + yr + "\CAH85_" + yr + "new.do" + "\n")
