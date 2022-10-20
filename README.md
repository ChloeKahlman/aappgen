This script generates the necessary files for AAPP.

It requires the import of the xlrd python library. Install it with:
```
pip install xlrd
```

Provide the files 'testpwd.txt', 'realpwd.txt', and 'contest_floor.xlsx' in the in folder.

Format specification of the input files:  **TODO**

**testpwd.txt & realpwd.txt**

**contest_floor.xlsx**



The script will ask if you want to use cached team data. If you choose yes, ids and passwords will not be redistributed amongst the generated user accounts. Choose no for a fresh generation of all accounts.

The resulting files will be put in the out folder.

Format specification of the output files: **TODO**
**TODO link to contest information page**

**generatedhosts**
# generatedhosts
## Format:
# storage = {'all':{'children':{'backup':{'hosts':{}}, 'teams':{'hosts':{}}}}}
# if team has pc : storage['all']['children']['teams']['hosts'][spts[0]] = {'ansible_host': f"{spts[0]}.clients.vu.nl", 'room': room, 'teamname': spts[1]}
# if no team has pc : storage['all']['children']['backup']['hosts'][item] = {'ansible_host': f"{item}.clients.vu.nl", 'room': room}                

# organisations.json
## Format:
    # id: the external affiliation ID. Must be unique
    # icpc_id (optional): an external ID, e.g. from the ICPC CMS, may be empty
    # name: the affiliation short name as used in the jury interface and certain exports
    # formal_name: the affiliation name as used on the scoreboard
    # country: the country code in form of ISO 3166-1 alpha-3

# groups.json
## Format: 
    # id: the category ID to use. Must be unique
    # icpc_id (optional): an external ID, e.g. from the ICPC CMS, may be empty
    # name: the name of the team category as shown on the scoreboard
    # hidden (defaults to false): if true, teams in this category will not be shown on the scoreboard
    # sortorder (defaults to 0): the sort order of the team category to use on the scoreboard. Categories with the same sortorder will be grouped together.

# teams.json
## Format:
    # id: the team ID. Must be unique
    # icpc_id (optional): an external ID, e.g. from the ICPC CMS, may be empty
    # group_ids: an array with one element: the category ID this team belongs to
    # name: the team name as used in the web interface
    # members (optional): Members of the team as one long string
    # display_name (optional): the team display name. If provided, will display this instead of the team name in certain places, like the scoreboard
    # organization_id: the external ID of the team affiliation this team belongs to

# test/accounts.yaml
## Format:
    # id: the account ID. Must be unique
    # username: the account username. Must be unique
    # password: the password to use for the account
    # type: the user type, one of team, judge, admin or balloon, jury will be interpret as judge
    # team_id: (NOT OPTIONAL) the external ID of the team this account belongs to
    # name: (optional) the full name of the account
    # ip (optional): IP address to link to this account

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
    
# testpassslips.txt
## Format: 
    # teamname
    # password
    # room number (so the password can be delivered)
    
# realpassslips.txt
## Format:
    # teamname
    # password
    # room number (so the password can be delivered)
    
# roomtoteams.txt
## Format:
    # Room
    # team1
    # team2 etc


# teamstoroom.txt
## Format:
    # teamname: room number
    # etc

# roomtopcs.txt
## Format:
    # Room number
    #pc1
    #pc2 etc.
