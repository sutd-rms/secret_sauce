# Secret Sauce
Secret Sauce for RMS to become the top revenue prediction service in the industry

# Requisites
1. Python3
2. pip3

# Deployment
1. Change directory into your application
2. Install virtual env package
```sudo pip3 install virtualenvwrapper```
3. Create Virutal Environment
```mkvirutalenv [your_env_name]```
4. Install all package files
``` pip3 install -r requirements.txt```
5. Run migration files
``` python3 manage.py migrate```
6. Run application
```python3 manage.py runserver```

# Troubleshooting
- Database or migration error?
    1. Try cleaning up your database
    ```python3 manage.py flush```
    2. Make sure all migrations are created
    ```python3 manage.py makemigrations```
    3. Run migrations
    ```python3 manage.py migrate```
- Force reset Branch
    1. ```git fetch --all```
    2. ```git reset --hard origin/<branch_name>```

# PR Guidelines
1. Always branch off from dev!
```git checkout -b <my_new_branch> dev```
2. Make sure your migrations are already run before running the application
``` python3 manage.py migrate```
3. When handling files, make sure you do not delete other contributors' files.
*You can install gitlens extension on VSCode to see if you are touching other people's code in other sections*
4. Git add carefully
    - Please do not run ```git add -A```
    - Manually go through every file you have made changes in and add them file by file
    - Make sure you do not upload unncecessary files i.e. files uploaded for testing
    - Make sure you do not add in your own database file
5. Ensure the feature functionality works
6. Provide clear documentation on Pull Request
