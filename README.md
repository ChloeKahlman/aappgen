This script generates the necessary files for AAPP.

It requires the import of the xlrd python library. Install it with:
```
pip install xlrd
```

Provide the files 'testpwd.txt', 'realpwd.txt', and 'contest_floor.xlsx' in the in folder.

Format specification of the input files: *TODO*

The script will ask if you want to use cached team data. If you choose yes, ids and passwords will not be redistributed amongst the generated user accounts. Choose no for a fresh generation of all accounts.

The resulting files will be put in the out folder.
