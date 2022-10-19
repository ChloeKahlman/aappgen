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
testsessionpwdfile = indir + "koenpasswd.txt"
realsessionpwdfile = indir + "realpasswd.txt"
roomsfile = indir + "contest_floor.xlsx"
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
# pcs = { 'pcnumber':{}, 'roomnumber':{}, 'rownumber':{}, 'columnnumber':{} }
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
# teams = { 'id':{}, 'icpcid':{}, 'name':{}, 'type':{}, 'group_id':{}, 'organisation':{}, 'pcnumber':{}, 'roomnumber':{}, 'rownumber':{}, 'columnnumber':{}, 'testpwd':{}, 'realpwd':{}, 'login':{} }

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
        while (len(list(filter(lambda team: team['id'] == i, teams))) == 1):
            i = i + 1 
        team = {'id': str(i),
                'icpcid': str(i+ipcpuserbase), 
                'name': admin, 
                'type':'admin', 
                'group': '101', 
                'organization':'42', 
                'pcnumber':'', 
                'roomnumber':'', 
                'testpwd': testpasswords[1 + i - firstid], 
                'realpwd': realpasswords[1 + i - firstid], 
                'login': login(i, 'admin') 
        }
        i = i + 1
        teams.append(team)    

i = firstid + adminmax    
for judge in judges:
    if (len(list(filter(lambda team: team['name'] == judge, teams))) == 0):
        while (len(list(filter(lambda team: team['id'] == i, teams))) == 1):
            i = i + 1 
        team = {'id': str(i),
                'icpcid': str(i+ipcpuserbase), 
                'name': judge, 
                'type':'judge', 
                'group': '101', 
                'organization':'42', 
                'pcnumber':'', 
                'roomnumber':'', 
                'testpwd': testpasswords[1 + i - firstid], 
                'realpwd': realpasswords[1 + i - firstid], 
                'login': login(i, 'judge') 
        }
        i = i + 1
        teams.append(team)  

# TODO read PCs and teams from the excel file



# open the excel file

# for each sheet

    # room name = sheet name

    # add room name to rooms

    # rowcounter = 0
 

    # for each row
        # pccounter = 0
        # foundrow = false
        # look for cells containing a pc  
        
        # if randomword (any string that doesn't start with "PC-")
            # skip this cell

        # if found a pc,
            # increase column counter by 1
            # if !foundrow
            #   increase rowcounter by 1  (do only once per row)
            #   foundrow = true

        # if just a pc, add it to backup: add pcnumber, roomnumber, row and column
         #if pc has a team sitting there:
            # if the teamname exists in teams
                # update that team's pcnumber, roomnumber, row and column
            # else (new team!)
                # create new team and fill in all fields.
        
       






# OLD CODE
# # Reading the csv files with teams and pcs
# i = firstid + adminmax + judgemax
# for file in roomfiles:
#     roomnumber = rooms[roomfiles.index(file)]
#     with open(file) as csvfile:
#         spamreader = csv.reader(csvfile, delimiter=tabledelimiter)
#         for row in spamreader:
#             for item in list(row):
#                 if item=="":
#                     continue
#                 spts = item.split(pcdelimiter,1)
#                 if bool(len(spts)-1):
#                     team = {'id': str(i), 'icpcid': str(i+ipcpuserbase), "name": str(spts[1]), 'type':'team', "group":"102", "organization":"42", "pcnumber":str(spts[0]), "roomnumber":str(roomnumber), "testpwd": "", "realpwd": ""}
#                     teams.append(team)
#                     i = i + 1
#                 else:
#                     pc = {'pcnumber': str(spts[0]), 'roomnumber': str(roomnumber)}
#                     pcs.append(pc)
## END OLD CODE

############################################ FILE CREATION ##########################################################

# generatedhosts
## Format:
# storage = {'all':{'children':{'backup':{'hosts':{}}, 'teams':{'hosts':{}}}}}
# if team has pc : storage['all']['children']['teams']['hosts'][spts[0]] = {'ansible_host': f"{spts[0]}.clients.vu.nl", 'room': room, 'teamname': spts[1]}
# if no team has pc : storage['all']['children']['backup']['hosts'][item] = {'ansible_host': f"{item}.clients.vu.nl", 'room': room}                

storage = {'all':{'children':{'backup':{'hosts':{}}, 'teams':{'hosts':{}}}}}
for team in teams:
    if team["type"] == "admin" or team["type"] == "judge":
        continue
    storage['all']['children']['teams']['hosts'][team["pcnumber"]] = {'ansible_host': team["pcnumber"]+".clients.vu.nl", 'room': team["roomnumber"], 'teamname': team["name"]}
for pc in pcs:
    storage['all']['children']['backup']['hosts'][pc["pcnumber"]] = {'ansible_host': pc["pcnumber"]+".clients.vu.nl", 'room': pc["roomnumber"]}
with open(generatedhosts, "w") as outfile:
    yaml.dump(storage, outfile)

# organisations.json
## Format:
    # id: the external affiliation ID. Must be unique
    # icpc_id (optional): an external ID, e.g. from the ICPC CMS, may be empty
    # name: the affiliation short name as used in the jury interface and certain exports
    # formal_name: the affiliation name as used on the scoreboard
    # country: the country code in form of ISO 3166-1 alpha-3

with open(organisationsjson, "w") as outfile:
    outfile.write(json.dumps(organizations, indent=2))

# groups.json
## Format: 
    # id: the category ID to use. Must be unique
    # icpc_id (optional): an external ID, e.g. from the ICPC CMS, may be empty
    # name: the name of the team category as shown on the scoreboard
    # hidden (defaults to false): if true, teams in this category will not be shown on the scoreboard
    # sortorder (defaults to 0): the sort order of the team category to use on the scoreboard. Categories with the same sortorder will be grouped together.

with open(groupsjson, "w") as outfile:
    outfile.write(json.dumps(groups, indent=2))

# teams.json
## Format:
    # id: the team ID. Must be unique
    # icpc_id (optional): an external ID, e.g. from the ICPC CMS, may be empty
    # group_ids: an array with one element: the category ID this team belongs to
    # name: the team name as used in the web interface
    # members (optional): Members of the team as one long string
    # display_name (optional): the team display name. If provided, will display this instead of the team name in certain places, like the scoreboard
    # organization_id: the external ID of the team affiliation this team belongs to

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

# test/accounts.yaml
## Format:
    # id: the account ID. Must be unique
    # username: the account username. Must be unique
    # password: the password to use for the account
    # type: the user type, one of team, judge, admin or balloon, jury will be interpret as judge
    # team_id: (NOT OPTIONAL) the external ID of the team this account belongs to
    # name: (optional) the full name of the account
    # ip (optional): IP address to link to this account

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

#real version
# real/accounts.yaml
## Format:
    # id: the account ID. Must be unique
    # username: the account username. Must be unique
    # password: the password to use for the account
    # type: the user type, one of team, judge, admin or balloon, jury will be interpret as judge
    # team_id: (NOT OPTIONAL) the external ID of the team this account belongs to
    # name: (optional) the full name of the account
    # ip (optional): IP address to link to this account

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

# testpassslips.txt
## Format: 
    # teamname
    # password
    # room number (so the password can be delivered)

with open(testpassslips, 'w') as outfile:
    for team in teams:
        outfile.writelines("Team:  "+team["name"]+"\nUsername:  "+team["login"]+"\nTest Session Password:  "+team["testpwd"]+"\nRoom:  "+team["roomnumber"]+"\n\n")

# realpassslips.txt
## Format:
    # teamname
    # password
    # room number (so the password can be delivered)

with open(realpassslips, 'w') as outfile:
    for team in teams:
        outfile.writelines("Team:  "+team["name"]+"\nUsername:  "+team["login"]+"\nCompetition Password:  "+team["realpwd"]+"\nRoom:  "+team["roomnumber"]+"\n\n")

# roomtoteams.txt
## Format:
    # Room
    # team1
    # team2 etc

with open(roomtoteams, 'w') as outfile:
    for room in rooms:
        outfile.writelines("ROOM "+room+"\n")
        for team in teams:
            if(room == team["roomnumber"]):
                outfile.writelines(team["name"]+"\n")
        outfile.writelines("\n\n")

# teamstoroom.txt
## Format:
    # teamname: room number
    # etc

with open(teamstoroom, 'w') as outfile:
    for team in teams:
        outfile.writelines(team["name"]+"  :  "+team["roomnumber"]+"\n")

# roomtopcs.txt
## Format:
    # Room number
    #pc1
    #pc2 etc.

with open(roomtopcs, 'w') as outfile:
    for room in rooms:
        outfile.writelines(room+"\n")
        for team in teams:
            if(room == team["roomnumber"]):
                outfile.writelines(team["pcnumber"]+"\n")
        for pc in pcs:
            if(room == pc["roomnumber"]):
                outfile.writelines(pc["pcnumber"]+"\n")
        outfile.writelines("\n\n")

#TODO pcs en teamnamen op alfabetische volgorde

#TODO add coordinates to txt outputs

# Cache the teams object
with open(cachefile, 'w') as outfile:
    json.dump(teams, outfile)