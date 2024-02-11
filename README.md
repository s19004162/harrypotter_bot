# harry_potter
harry_potter bot application

## How to use

### Install
---
```
# Install Python
# support version 3.8 to 3.12.

# How to install streamlit
# https://docs.streamlit.io/get-started/installation/command-line

cd harrypotter_bot 

python -m venv .venv

# macOS and Linux
source .venv/bin/activate
.venv/Scripts/activate.bat

# Install required module
pip install -r requirements.txt

# Set-up .env file (Manually set up environmental variables)

# Run application
streamlit run harrypotter_bot.py

python -m streamlit run harrypotter_bot.py

# To finish virtual environment
deactivate
```

### How to upload data to SQL DB
---
This is not used in this time : [Install sqlcmd utility](https://learn.microsoft.com/en-us/sql/tools/sqlcmd/sqlcmd-utility?view=sql-server-ver15&preserve-view=true&tabs=go%2Cwindows&pivots=cs1-bash)

[Install Azure Data Studio](https://learn.microsoft.com/en-us/azure-data-studio/download-azure-data-studio?tabs=macOS-install%2Cwin-user-install%2Credhat-install%2Cwindows-uninstall%2Credhat-uninstall)

[Quickstart: Use Azure Data Studio to connect and query SQL Server](https://learn.microsoft.com/en-us/azure-data-studio/quickstart-sql-server)

```
# Create table in query view

-- Create a new table called 'Customers' in schema 'dbo'
-- Drop the table if it already exists
IF OBJECT_ID('dbo.Words', 'U') IS NOT NULL
 DROP TABLE dbo.Words;
GO
-- Create the table in the specified schema
CREATE TABLE dbo.Words
(
 WordId int NOT NULL PRIMARY KEY, -- primary key column
 Germanword nvarchar(50) NOT NULL,
 Germanexample nvarchar(200),
 Englishword nvarchar(50) NOT NULL,
 Englishexample nvarchar(200)
);
GO
```

[SQL Server Import extension](https://learn.microsoft.com/en-us/azure-data-studio/extensions/sql-server-import-extension)

