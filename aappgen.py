try:
   import xlrd
except ImportError:
    print ('Error! This script requires the xlrd package to open the room layout Excel file. Use \"pip install xlrd\" to install this package.')
    exit(1)
import yaml
import json 

######################################### CONSTANTS #####################################################################
#NUMBERS
firstid = 1
ipcpuserbase = 420000
icpcgroupsbase = 133700
teamsmax = 100

#INPUT
indir = "in/" # input file directory
# 2 files containing a list of passwords, each password on a new line. 
# each file should contain at least adminmax + judgemax + teamsmax fresh passwords.
testsessionpwdfile = indir + "testpasswd.txt"
realsessionpwdfile = indir + "realpasswd.txt"
# an excel sheet containing the floor layout
roomsfile = indir + "contest_floor.xls" # TODO current xlrd library does not support .xlsx because of security concern
pcdelimiter = '='

# ## a list of room names, matching an equal length list of csv files containing PCs and groups in those rooms.
# ## csv format: PC-444444;PC-444445 = Team Really Cool Name; etc.
# rooms = ["6B37", "6B57"]
# roomfiles = [indir + "6b37.csv", indir + "6b57.csv"]
# tabledelimiter = ';' #TODO names include this symbol often . Fix: read directly from the excel file. seems pretty easy to do

adminmax = 50
admins = ["Michael", "Josh", "Tudor", "Koen"] 

judgemax = 50
judges = ["Thomas", "Jeroen", "Peter"]

# A json object containing the organizations taking part in the contest.
# See file creation below for the format specification.
organizations = [{
  "id": "INST-42",
  "icpc_id": "42",
  "name": "VU",
  "formal_name": "Vrije Universiteit Amsterdam",
  "country": "NLD"
}]

# A json object containing the desired user groups for domjudge accounts.
# See file creation below for the format specification.
groups = [{
  "id": "100",
  "icpc_id": str(icpcgroupsbase),
  "name": "Participants"
}, {
  "id": "101",
  "icpc_id": str(icpcgroupsbase+1),
  "name": "Bacon",
  "hidden": True
},{
  "id": "102",
  "icpc_id": str(icpcgroupsbase+2),
  "name": "Spectators"
}]

#CACHE
cachefile = "cache.json"

#OUTPUT
outdir = "out/"
generatedhosts = outdir + "generatedhosts"
organisationsjson = outdir + "organizations.json"
groupsjson = outdir + "groups.json"
teamsjson = outdir + "teams.json"
testaccountsyaml = outdir + "test/accounts.yaml"
realaccountsyaml = outdir + "real/accounts.yaml"
testpassslips = outdir + "testpasswords.txt"
realpassslips = outdir + "realpasswords.txt"
roomtoteams = outdir + "roomtoteams.txt"
teamstoroom = outdir + "teamstoroom.txt"
roomtopcs = outdir + "roomtopcs.txt"
# pcs to room is already contained in generatedhosts

############################################ PROCESSING #############################################################

# Creating backup pc list
# a pc has
    # KEY a pc number
    # a room number
    # a row number
    # a column number (how many'th pc on that row)
pcs = []

# Creating a room name list 
rooms = []

# Creating teams list
# a user has:
    # KEY an id ranging from firstid to firstid + adminmax + judgemax + teamsmax
    # an icpc id, equal to id + icpcuserbase 
    # a name
    # a type, being either team, judge or admin     TODO spectator type accounts?
    # a group ids -> a number, matching an id from groups
    # a organisation id -> a number, matching an id from organisation
    # a pc number (if type == team)
    # a room number
    # a row number
    # a column number (how many'th pc on that row)
    # a password for the test session: the n'th password in testsessionpwdfile, where n is 1 + id - firstid
    # a password for the real session: the n'th password in realsessionpwdfile, where n is 1 + id - firstid
    # login, a name to log in on the domjudge servers

# Ask user to read teams from cache or not
while (True):
    answer = input("Use cached user data? (y/n):")
    if (answer == "y"):
        with open(cachefile) as infile:
            teams = json.load(infile)   # TODO catch cache not existing yet 
        break
    elif (answer == "n"):
        teams = []
        break

# For each admin, judge or team:
    # If their name occurs in the teams object, do not recompute all data
        # DO NOT RECOMPUTE: id, icpcid, name, type, group, organization, testpwd, realpwd, login
        # RECOMPUTE: pcnumber, roomnumber, rownumber, columnnumber
    # If their name does not occur in the teams object, check if id = i is taken already, else i=i+1 and try again
        # COMPUTE: everything

def login(i, teamtype):
    if i < 10:
        loginname = teamtype + "00" + str(i)
    elif i < 100:
        loginname = teamtype + "0" + str(i)
    else: 
        loginname = teamtype + str(i)
    return loginname

with open(testsessionpwdfile) as test, open(realsessionpwdfile) as real:
    testpasswords = [line.rstrip() for line in test]
    realpasswords = [line.rstrip() for line in real]

i = firstid
for admin in admins:
    if (len(list(filter(lambda team: team['name'] == admin, teams))) == 0):
        while (len(list(filter(lambda team: team['id'] == str(i), teams))) == 1):
            i = i + 1 
        team = {'id': str(i),
                'icpcid': str(i+ipcpuserbase), 
                'name': admin, 
                'type':'admin', 
                'group': '101', 
                'organization':'42', 
                'pcnumber':'', 
                'roomnumber':'',
                'rownumber':'',
                'columnnumber':'', 
                'testpwd': testpasswords[1 + i - firstid], 
                'realpwd': realpasswords[1 + i - firstid], 
                'login': login(i, 'admin') 
        }
        i = i + 1
        teams.append(team)    

i = firstid + adminmax    
for judge in judges:
    if (len(list(filter(lambda team: team['name'] == judge, teams))) == 0):
        while (len(list(filter(lambda team: team['id'] == str(i), teams))) == 1):
            i = i + 1 
        team = {'id': str(i),
                'icpcid': str(i+ipcpuserbase), 
                'name': judge, 
                'type':'judge', 
                'group': '101', 
                'organization':'42', 
                'pcnumber':'', 
                'roomnumber':'',
                'rownumber':'',
                'columnnumber':'',  
                'testpwd': testpasswords[1 + i - firstid], 
                'realpwd': realpasswords[1 + i - firstid], 
                'login': login(i, 'judge') 
        }
        i = i + 1
        teams.append(team)  

# TODO read PCs and teams from the excel file

with xlrd.open_workbook(roomsfile) as spreadsheet:
    i = firstid + adminmax + judgemax  # TODO this is potentially unsafe if actual number of judges is low but cached number of judges is over the limit
    for tab in spreadsheet.sheets():
        roomname = tab.name
        rooms.append(roomname)
        rowcounter = 0
        for cur_row in range(0, tab.nrows):
            columncounter = 0
            foundpc = False
            for cur_col in range(0, tab.ncols):
                cell = tab.cell(cur_row, cur_col)
                item = cell.value
                # print(cell.value, cell.ctype)
                if (not item.startswith("PC-")):
                    continue
                else:
                    columncounter = columncounter + 1
                    if (not foundpc):
                        rowcounter = rowcounter + 1
                        foundpc = True
                    spts = item.split(pcdelimiter,1)
                    if (len(spts) == 1): #found a backup pc
                        pc = {
                            'pcnumber': str(spts[0]), 
                            'roomnumber': roomname,
                            'rownumber': str(rowcounter),
                            'columnnumber': str(columncounter)
                        }   
                        pcs.append(pc)
                    else: #found a team
                        search = list(filter(lambda team: team['name'] == spts[1], teams))
                        if (len(search) == 1): #existing team
                            index = teams.index(search[0])
                            # update that team's pcnumber, roomnumber, row and column
                            teams[index]['pcnumber'] = spts[0]
                            teams[index]['roomnumber'] = roomname
                            teams[index]['rownumber'] = str(rowcounter)
                            teams[index]['columnnumber'] = str(columncounter)
                        else: #new team
                            while (len(list(filter(lambda team: team['id'] == i, teams))) == 1):
                                i = i + 1 
                            team = {
                                'id': str(i),
                                'icpcid': str(i+ipcpuserbase), 
                                'name': spts[1], 
                                'type': 'team', 
                                'group': '102', 
                                'organization':'42', 
                                'pcnumber': spts[0], 
                                'roomnumber': roomname,
                                'rownumber': str(rowcounter),
                                'columnnumber': str(columncounter),  
                                'testpwd': testpasswords[1 + i - firstid], 
                                'realpwd': realpasswords[1 + i - firstid], 
                                'login': login(i, 'team') 
                            }
                            teams.append(team)

############################################ FILE CREATION ##########################################################

#ansiblehosts file
storage = {'all':{'children':{'backup':{'hosts':{}}, 'teams':{'hosts':{}}}}}
for team in teams:
    if team["type"] == "admin" or team["type"] == "judge":
        continue
    storage['all']['children']['teams']['hosts'][team["pcnumber"]] = {'ansible_host': team["pcnumber"]+".clients.vu.nl", 'room': team["roomnumber"], 'teamname': team["name"]}
for pc in pcs:
    storage['all']['children']['backup']['hosts'][pc["pcnumber"]] = {'ansible_host': pc["pcnumber"]+".clients.vu.nl", 'room': pc["roomnumber"]}
with open(generatedhosts, "w") as outfile:
    yaml.dump(storage, outfile)

#organizations.json
with open(organisationsjson, "w") as outfile:
    outfile.write(json.dumps(organizations, indent=2))

#groups.json
with open(groupsjson, "w") as outfile:
    outfile.write(json.dumps(groups, indent=2))

#teams.json
teamsoutput = []
for team in teams: 
    teamoutput = {
        "id":team["id"], 
        "icpc_id":team["icpcid"], 
        "group_ids":[team["group"]], 
        "name":team["name"], 
        "organization_id":team["organization"]
    }
    teamsoutput.append(teamoutput)
with open(teamsjson, "w") as outfile:
    outfile.write(json.dumps(teamsoutput, indent=2))

#testsession accounts.yaml
accounts = []
for team in teams:
    account = {
        "id": team["login"], 
        "username": team["login"],
        "password": team["testpwd"],
        "type": team["type"],
        "team_id": team["id"]
    }
    accounts.append(account)
with open(testaccountsyaml, 'w') as outfile:
    yamllines = yaml.dump(accounts)
    for line in yamllines:
        outfile.writelines(line)

#realsession accounts.yaml
accounts = []
for team in teams:
    account = {
        "id": team["login"], 
        "username": team["login"],
        "password": team["realpwd"],
        "type": team["type"],
        "team_id": team["id"]
    }
    accounts.append(account)
with open(realaccountsyaml, 'w') as outfile:
    yamllines = yaml.dump(accounts)
    for line in yamllines:
        outfile.writelines(line)

# paper slips for handing out test session passwords
with open(testpassslips, 'w') as outfile:
    for team in teams:
        outfile.writelines("Team:  "+team["name"]+"\nUsername:  "+team["login"]+"\nTest Session Password:  "+team["testpwd"]+"\nRoom:  "+team["roomnumber"]+"   Row:"+team['rownumber']+"  Computer:"+team['columnnumber']+"\n\n")

# paper slips for handing out real session passwords
with open(realpassslips, 'w') as outfile:
    for team in teams:
        outfile.writelines("Team:  "+team["name"]+"\nUsername:  "+team["login"]+"\nCompetition Password:  "+team["realpwd"]+"\nRoom:  "+team["roomnumber"]+"   Row:"+team['rownumber']+"  Computer:"+team['columnnumber']+"\n\n")

with open(roomtoteams, 'w') as outfile:
    for room in rooms:
        outfile.writelines("ROOM "+room+"\n")
        for team in teams:
            if(room == team["roomnumber"]):
                outfile.writelines("Team: "+team["name"]+"   Row:"+team['rownumber']+"  Computer:"+team['columnnumber']+"\n")
        outfile.writelines("\n\n")

with open(teamstoroom, 'w') as outfile:
    for team in teams:
        outfile.writelines(team["name"]+"  :  "+team["roomnumber"]+"   Row:"+team['rownumber']+"  Computer:"+team['columnnumber']+"\n")

with open(roomtopcs, 'w') as outfile:
    for room in rooms:
        outfile.writelines(room+"\n")
        for team in teams:
            if(room == team["roomnumber"]):
                outfile.writelines(team["pcnumber"]+"   Row:"+team['rownumber']+"  Computer:"+team['columnnumber']+"\n")
        for pc in pcs:
            if(room == pc["roomnumber"]):
                outfile.writelines(pc["pcnumber"]+"   Row:"+pc['rownumber']+"  Computer:"+pc['columnnumber']+"\n")
        outfile.writelines("\n\n")

#TODO pcs en teamnamen op alfabetische volgorde

# Cache the teams object
with open(cachefile, 'w') as outfile:
    json.dump(teams, outfile)