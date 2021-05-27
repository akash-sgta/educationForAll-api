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

    try:
        service = User(api_key="fyUdIpAERQKQYM6o281Ca1R5WZLsF46GwpuDfmp36Jy3nzmDKdJlKYv5XoUaQi8b", url="http://localhost:8000")
        uauth = "HH2EqDOzE40luxtVM1Kv9FXPNYhn2OYcwowcDnL0hAnkGbWwSPI4sjmgtPGGLKPn"

        # checking if server is live
        data = service.check_server()
        if (data[0] == True) and (data[1][0] == 200):

            BASE_DIR = Path(__file__).resolve().parent

            # ------------------------UserCredential---------------------------------------

            # action POST => signup
            if False:
                file_name = os.path.join(BASE_DIR, "json", "user", "signup.json")
                with open(file_name, "r") as json_file:
                    temp = json.load(json_file)
                print(service.run(action="POST", uauth=uauth, data=temp))

            # action POST => signin
            if False:
                file_name = os.path.join(BASE_DIR, "json", "user", "signin.json")
                with open(file_name, "r") as json_file:
                    temp = json.load(json_file)
                print(service.run(action="POST", uauth=uauth, data=temp))

            # action POST => forgot_password
            if False:
                file_name = os.path.join(BASE_DIR, "json", "user", "forgot_password.json")
                with open(file_name, "r") as json_file:
                    temp = json.load(json_file)
                print(service.run(action="POST", uauth=uauth, data=temp))

            # action GET => user get self, all, pk
            if False:
                file_name = os.path.join(BASE_DIR, "json", "user", "get_data.json")
                with open(file_name, "r") as json_file:
                    temp = json.load(json_file)
                print(service.run(action="GET", uauth=uauth, data=temp))

            # action PUT => user change
            if True:
                file_name = os.path.join(BASE_DIR, "json", "user", "get_data.json")
                with open(file_name, "r") as json_file:
                    temp = json.load(json_file)
                print(service.run(action="PUT", uauth=uauth, data=temp))

            # action DELETE => sa
            if True:
                file_name = os.path.join(BASE_DIR, "json", "user", "get_data.json")
                with open(file_name, "r") as json_file:
                    temp = json.load(json_file)
                print(service.run(action="DELETE", uauth=uauth, data=temp))

    except Exception as ex:
        print(f"[EX] : {ex}")
