# Okta-Python-Scripts
Python scripts that demonstrte use of Okta's REST APIs for Unviversl Directory. Description of each script

1) get_all_active_users_with_app_assignments.py -> Gets all active users and their app assignments in a CSV.
2) get_applications_with_signon_type.py -> Gets all applications and their signon methods in a CSV.

# Requirements to Run Script:

1) Python 2.7
2) Python's requests libaray (run "pip install requests" from command line or shell). You may need to install pip i.e. Python's package
manager on Windows system


# How to Run Script

For all scripts open the script in your favorite editor (e.g. Sublime) and set following variables

orgName: including okta/oktapreview to your org e.g. "myorg.okta" or "myorg.oktapreview"
apiKey: API token from Okta org (Security -> API -> Token)

If there are any required attribute such as N, attributeName, attributeValue at the top, update 
those to yoru need as well.

In command prompt or shell navigate to folder where Python script is copied "cd ~/Documents/PythonScripts" and run the script e.g
"python get_all_active_users_with_app_assignments.py"


# Credits

Special thanks to Sohaib Ajmal from the Okta Developer Support team who provided the foundation for these scripts.
https://github.com/SohaibAjmal/Okta-UD-Scripts