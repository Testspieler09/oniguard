PROGRAM_NAME = r"""
________           .__   ________                            .___
\_____  \    ____  |__| /  _____/  __ __ _____   _______   __| _/
 /   |   \  /    \ |  |/   \  ___ |  |  \\__  \  \_  __ \ / __ |
/    |    \|   |  \|  |\    \_\  \|  |  / / __ \_ |  | \// /_/ |
\_______  /|___|  /|__| \______  /|____/ (____  / |__|   \____ |
        \/      \/             \/             \/              \/
"""

DESCR = """
An Oni-themed password manager, primarily designed for terminal use, though a GUI could be seamlessly integrated.

The manager boasts several features:
    - password generation
    - a robust search function and
    - editable schemas.

Additionally, it incorporates color-coded elements and employs cryptography for enhanced security purposes.
"""

HELP_MESSAGE="""
 Key cheat sheet
 ===============

 Arrow Keys -> Scroll contents
 # other functionality

 H -> Toggle this [H]elpmessage
 Q -> [Q]uit program
"""

DEFAULT_SCHEMES = {
    "f4173947c70e4152a62582b1ca8a85db": ["Application", "Password", "Changedate", "Creationdate"],
    "a4c831c95bf74283b28858835c253513": ["Application", "Verification through", "Email used", "Changedate", "Creationdate"]
}

INSTRUCTIONS = {
    "add": "What scheme do you want to add the entry to?"
}

FOOTER_TEXT=["[H]elp", "[Q]uit"]
