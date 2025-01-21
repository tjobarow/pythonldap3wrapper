# Quick use guide
## Building package from source
1. To build pythonldap3wrapper from source, first clone the repo

```git clone git@github.com:tjobarow/pythonldap3wrapper.git```

2. Create a new python virtual environment (if you have that module installed in python)

```python -m venv .my-venv```

3. Activate the environment (depends on OS)

- __Linux/MacOS:__

```source ./.my-venv/bin/activate```

- __Windows (PowerShell|CMD prompt)__

```./.my-venv/Scripts/[Activate.ps1|Activate.bat]```

4. Install buildtools & wheel

```pip install build wheel```

5. Build package from within cloned repo

```python -m build --wheels```

6. Install pythonldap3wrapper using pip from within root directory of pythonldap3wrapper
```pip install .``` 

## Using package
### Import package
```from ldap3_wrapper import Ldap3Wrapper```

### Create instance of package
Create an instance of pythonldap3wrapper, providing the following parameters. Can be pulled from environment variables, or however you see fit.
```
ldap = Ldap3Wrapper(
    ldap_server_host=os.getenv("bind_hostname"),
    bind_cn=os.getenv("bind_cn"),
    bind_username=os.getenv("bind_username"),
    bind_password=os.getenv("bind_password"),
    use_ldaps=True,
)
```

### Search for user object by mail (wildcard appended to end of string)
This seaches by a full or partial email. This appends a wildcard to the end of the provided string, and matches on ```mail``` LDAP attribute.
```user=ldap.search_user_by_email(user_email="tjobarow")```

### Search for user object by sAMAccountName (wildcard appended to end of string)
This seaches by a full or partial sAMAccountName. This appends a wildcard to the end of the provided string, and matches on ```sAMAccountName``` LDAP attribute.
```user=ldap.search_user_by_userid(user_id="tjSamName")```