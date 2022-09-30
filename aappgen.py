import csv
import yaml
import json 

######################################### CONSTANTS #####################################################################
#NUMBERS
firstid = 1
ipcpuserbase = 420000
icpcgroupsbase = 133700
teamsmax = 100

#INPUT
indir = "" # input file directory
adminmax = 50
admins = ["Michael", "Josh", "Tudor", "Koen"]  #TODO could input these as seperate csv files, but there are not that many

judgemax = 50
judges = ["Thomas", "Jeroen", "Peter"]

## a list of room names, matching an equal length list of csv files containing PCs and groups in those rooms.
## csv format: PC-444444;PC-444445 = Team Really Cool Name; etc.
rooms = ["6B37", "6B57"]
roomfiles = [indir + "6b37.csv", indir + "6b57.csv"]
tabledelimiter = ';'
pcdelimiter = '='  #TODO names include these symbols often

## 2 files containing a list of passwords, each password on a new line. 
## each file should contain at least adminmax + judgemax + teamsmax fresh passwords.
testsessionpwdfile = indir + "koenpasswd.txt"
realsessionpwdfile = indir + "realpasswd.txt"

## A json object containing the organizations taking part in the contest.
## See file creation below for the format specification.
organizations = [{
  "id": "INST-42",
  "icpc_id": "42",
  "name": "VU",
  "formal_name": "Vrije Universiteit Amsterdam",
  "country": "NLD"
}]

## A json object containing the desired user groups for domjudge accounts.
## See file creation below for the format specification.
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
#pcs to room is already contained in generatedhosts

############################################ PROCESSING #############################################################
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
    # a password for the test session: the n'th password in testsessionpwdfile, where n is 1 + id - firstid
    # a password for the real session: the n'th password in realsessionpwdfile, where n is 1 + id - firstid
    # login, a name to log in on the domjudge servers
#teams = {'id':{}, 'icpcid':{}, 'name':{}, 'type':{}, 'group_id':{}, 'organisation':{}, 'pcnumber':{}, 'roomnumber':{}, 'testpwd':{}, 'realpwd':{}}
teams = []

# Creating backup pc list
# a pc has
    # KEY a pc number
    # a room number
#pcs = {'pcnumber':{}, 'roomnumber':{}}
pcs = []

# adding the admin and judge users
i = firstid
for admin in admins:
    team = {'id': str(i), 'icpcid': i+ipcpuserbase, "name": admin, 'type':'admin', "group": "101", "organization":"42", "pcnumber":"", "roomnumber":"", "testpwd": "", "realpwd": "", "login": ""}
    i = i + 1
    teams.append(team)

i = firstid + adminmax
for judge in judges:
    team = {'id': str(i), 'icpcid': i+ipcpuserbase, "name": judge, 'type':'judge', "group": "101", "organization":"42", "pcnumber":"", "roomnumber":"", "testpwd": "", "realpwd": "", "login": ""}
    i = i + 1
    teams.append(team)

# Reading the csv files with teams and pcs
i = firstid + adminmax + judgemax
for file in roomfiles:
    roomnumber = rooms[roomfiles.index(file)]
    with open(file) as csvfile:
        spamreader = csv.reader(csvfile, delimiter=tabledelimiter)
        for row in spamreader:
            for item in list(row):
                if item=="":
                    continue
                spts = item.split(pcdelimiter)
                if bool(len(spts)-1):
                    team = {'id': str(i), 'icpcid': str(i+ipcpuserbase), "name": str(spts[1]), 'type':'team', "group":"102", "organization":"42", "pcnumber":str(spts[0]), "roomnumber":str(roomnumber), "testpwd": "", "realpwd": ""}
                    teams.append(team)
                    i = i + 1
                else:
                    pc = {'pcnumber': str(spts[0]), 'roomnumber': str(roomnumber)}
                    pcs.append(pc)

# For each user, add their passwords
with open(testsessionpwdfile) as test, open(realsessionpwdfile) as real:
    testpasswords = [line.rstrip() for line in test]
    realpasswords = [line.rstrip() for line in real]
    for team in teams:
        team['testpwd'] = testpasswords[1 + int(team['id']) - firstid]
        team['realpwd'] = realpasswords[1 + int(team['id']) - firstid]

# For each user, generate their login name


for team in teams:
    if int(team["id"]) < 10:
        loginname = team["type"] + "00" + team["id"]
    elif int(team["id"]) < 100:
        loginname = team["type"] + "0" + team["id"]
    else: 
        loginname = team["type"] + team["id"]
    team["login"] = loginname

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