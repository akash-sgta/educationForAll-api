import json
import os
import platform
from pathlib import Path

from client.user import User

if __name__ == "__main__":

    if platform.system().upper() == "WINDOWS":
        os.system("cls")
    else:
        os.system("clear")

    service = User(api_key="fyUdIpAERQKQYM6o281Ca1R5WZLsF46GwpuDfmp36Jy3nzmDKdJlKYv5XoUaQi8b", url="http://localhost")
    uauth = ""

    # checking if server is live
    data = service.check_server()
    if (data[0] == True) and (data[1][0] == 200):

        BASE_DIR = Path(__file__).resolve().parent

        # ------------------------UserCredential---------------------------------------

        # action POST => signup
        if True:
            file_name = os.path.join(BASE_DIR, "json", "user", "signup.json")
            with open(file_name, "r") as json_file:
                temp = json.load(json_file)
            print(service.run(action="POST", uauth=uauth, data=temp))

        # action POST => signin
        if True:
            file_name = os.path.join(BASE_DIR, "json", "user", "signin.json")
            with open(file_name, "r") as json_file:
                temp = json.load(json_file)
            print(service.run(action="POST", uauth=uauth, data=temp))

    else:
        print(data[0])
        print("-" * 20)
        print(data[1])
