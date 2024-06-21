from selenium import webdriver

class Auto_Login:

    def __init__(self, url: str, credentials: dict) -> None:
        if not self.url_is_valid():
            raise Exception("InvalidURL")
        self.url: str = url
        self.credentials: dict = credentials

    def __str__(self):
        return f"Automatic login for {self.url}"

    def url_is_valid(self) -> bool:
        # logic here
        return True

    def auto_login(self)-> None:
        # define common names or ids for input and submit fields
        # keywords_inputs = []
        # keywords_submit_button = []

        # driver = webdriver.Firefox() # only works if Firefox is installed
        # driver.get(url)
        # driver.implicitly_wait(2) # need to add a better waiting strategy
        # driver.find_element("id", "loginFormLogin")
        pass

if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser(prog="Auto Login",
                            description="Login to any website automatically. Currently only works with Firefox.",
                            epilog="The programm isn't perfect")

    parser.add_argument("URL", type=str, help="The website to log into.")
    parser.add_argument("credentials", help="The name/email and password.")

    # args = parser.parse_args()

    l = Auto_Login("https://login.bwinf.de", {"password": "helloworld", "name": "testuser69"})
    print(l)
