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

ASCII_ONI_LOGO = [
    """
        ,,                                                      ,,
       ,%@;                                                     ?@*
       *@@*                                                    ,#@@:
      ,#@@S                                                    :@@@?
      ;@SS@;                  ,,,,,,   ,,,,,,                  %@?@#,
      *@%+@#,           ,:+?%S####SSS%SSS####S%*;:,           ;@S;@@:
      ?@#+?@%        :+%#@@##SS%*?S#@@@#%??%SS##@@#?;,       :@@+?@@:
      +@@*,%@?,   ,+S@@@@S%?**???%@@@@@@#%??***%%#@@@#%;    :#@+:%@@,
      ,@@?,,?@%,,*#@SS#@@##S%???S#@@@S@@@#%??%%S##@@SS#@S; ;@@; ;S@%
       *@S;, +@@#@@##@@@@@####@@@@@@%?S@@@@@@###@@@@@@##@@S@S: :+@@:
       ,S@%:, :?@@@@@@@@@@@@@@@@@@#%%%%%#@@@@@@@@@@@@@@@@@#+, :+#@*
        ,#@%;:, ;?#@@@@@@@@@@@##SSSSS%SSSSS#@@@@@@@@@@@@#*: ::+#@?
         ,S@S;:,;+*?#@#@#@#SS%%S#?;;;;;:+%#%%SS##@##@@S**+:::*#@*
          ,%@#*+*;+*S@;#+@%%S###:,?%*+*%*,+@S#S?#S??*@%*++*+%@@+
     +S+  ,S@@@S??%S@**#*@%%SS@; SS    ,@+ ?#SS%##+#;%@%%?%#@@@*  ,?S,
    :@%#?,+@@@@@@##%*?S*##%%?%@; ?#;,,,*@; ?@??%%@S?S**S##@@@@@@,:#S#%
    ?@?:SS#@@@@@@@SSS%%#S?%S%?SS+?@@##@@@*+@%%SS?%##%SSS#@@@@@@@S#*:S@:
    S@#S;?@@@@@#S#@##@#SSSSS%%%S@S%@@@@#%##%%%SSSSSS@###@#S@@@@@#++#@@+
    S@%S#*%@@@S;?%%%*+:,,;%#SS%%@S;@@#@S;@S%SSS#*:,,;*?%%%*+@@@@?%@%#@+
    *@S%@@%S@@@*:::::;;:,  :*?%?*,S#*,%@+:?%%?+,  :;;;::::;S@@@%S@#%@@:
    ,S@S@@@S#@#@@@#@@@@@#%+,    ,*@#*;%@#;    ,:*S@@@@@@#@@#@@S#@@##@*
     ,S@S@#@@@%+S@@@+*@@@@@#S%?%#@@@###@@@S??%S@@@@@#;?@@@?*S@@@@@S@+
      ;@S@SS@@%:;@#@* ?@@@@@@@@@@@#%%?%S#@@@@@@@@@@@+,S@@# *S@@%@##S
      +@?@@#@#%; ?@#@?;+?SSSSS@@@@@S?*%#@@@@@SSSS%?;+S@#@; *%@@#@S%#,
      +@SS@@@#%;+:+%S##S%%%%S@@@@@@S; *S@@@@@@S%%%S#@#S?;;;*%@@@#S##,
      ,;#@##S@%*+*****??%%%%SS#SS@S?, :%#@SS#S%%%%%??*****+?S#S@#@?:
        ;@%:*@@S%%%%????*??%S#S#SS%+ ,,?S%##S#S??**????%%%S#@S;;@#,
        +@;:@@@@#####SS%%S#@#*?%S%%;   *%%S?*?@@#%%%S#####@@@@% %@,
        ;@%,*#@@@###@@@###S@#%%SSSS%++*%SSSS%S@#S##@@@@##@@@#S::@S,
         +@S**+S@@@@@@#SS**%##@@@@@@@@@@@@@@@#S?+?SS#@@@@@@?*+?#S:
          ,*S#@@@#%#@@@?%@SSSSSS%%S####S%%%SSSS%#@*%@@@SS@@@##%+
         :;  ,:+@#?%S#@?S@S+*S#SSSSSS#SS#SSS@%*+@@%%@SS?%@#:,  ,;,
         :@S*;,:#@%%#@@%;?@; %@####S#@S####@@+ ?@;*S@#S?S@?,:+?@%,
          ;#@@#SS@#S?+, :+@@?@@#@%??%#???S@#@#%@S;,,:*%S##SS#@@%,
           ,?##S?*+;;+?S@@#*##++#???%#???%S;?@%*@@#%*+;++*%#@S+
             ,+?S#@@@@#S%##?%#S??*********?%S#?%@S%S@@@@@#S?;,
                 ,:;+%#@%+*??*?%S#########S%?*??**#@S?+:,,
                      ,?@@##@@#S%?????????S#@@##@@#+,
                        ;#@S??*++*?****??*++*??#@%,
                         :#@#???S#%?@@S?SS%?*%#@?,
                          ,?@@@####@@@@@####@@#+
                            :+?%%%?+;:;*?%%?*;,
""",
    """
       :?,                                      +*
      ,S@+                                     ,#@;
      ;@@S                                     ;@@%
      ?@*@+        ,;+?%%%%?*??%%%?*;:,       ,#%%@,
      ?@*?@:    :*S##SS%??S@@@#%?%%S###?;,    %#+#@,
      ;@%,?@; ;%##@@S%???S@@@@@#%??%S#@@#S*,,%#:;@S
      ,S#; +#S@@#@@@@###@@@#%S@@@@##@@@@##@##%,,?@;
       :#S:,:?#@@@@@@@@@@##%%%S##@@@@@@@@@@S;,,*@*
        :#S+,:+?#@#@@#SSS%*+**+?SSS##@@#@%*;,:?@*
      :  :@@?*+*#%%?#%S#%:?+;;?;;#S%SS%*#?+**S@*  :,
     *#?,*@@@#SS%*%SS%%#;:#: ,*% S%%%#??*SS#@@@#,+SS,
    ,@?*%#@@@@@SSS#S%S%%S*#@##@%?#%S%%#SSS#@@@@@S%+@*
    :@#%*#@@S%SSS%**%S%%S@?@@@%S#%%SS?*?SSSS%@@@%?S@%
    ,@S#@%#@S+;;;;;,,;???+*#+?S;???+,,:;;;;;?@@SS@%@+
     +@#@@#@S#@@S#@@S+:::+@#?%@%:::;?#@@S#@@S#@#@##%,
      *#@S@@?;@@*;@@@@@@@@@SSS#@@@@@@@@%:#@%;#@S@#S
      *##@@#?,?##?*%SSS@@@@S+?#@@@#SS%?*S@S:;S@#@SS
      ;S#@@#?+++?%S%%%S@#@@? ;S@#@#%%%SS%*+++S@@##*
      ,@?+@#%%%???*?%SSSSS; ,?SSSSS??*??%%%S@?+@*
       ,@;*@@@####SS#@S?%%%+,:?%%??@#SS#####@@S,#*
        *S*?%@@@@@#S?%###@##SS######?%##@@@@#?*%S,
         :*%S@#S@@%%#%SSSSS###SSSSS%S@?@@#S@#%?+,
        :?;,,S#?S@S?#+;##S#S#SS###?:S%%@#%%@;,:**
         *@@%%#%?+::%#?###%?#%%%##S%@+:;*%SS%S@S:
          :?SS%%%%%#@?#S?%??%???%*#?S@S%%%%SS%+,
            ,:+*%S#%?%%?%%%%%%%%%%%%%?##%?+;,
                 ,;#@#S#%???????%S#S#@?,
                   ,%@%**?%?S%?%?**S@+
                    ,*#####@@@#####S:
                      ,;++;:,:;;+;:
""",
    """
      ,,                       ,
     :#;                      ,#+
     *#?     ,:;;;;;;;;:,     +#S
     ?%%* ,;?SS%%S@@#%%SS%+, ;S?S
     ;#:??S#@@#S#@##@#S#@@@#??:%*
      *%:;S@@@@@#S??%#@@@@@#*,?%
     : ?#**S%SSS?+;;+*SSS%S**SS :,
    +S*S@@#%%S%S???*%+S%SS%#@@@*%?
    ?#%#@%%%*+?%S%#@%S%%+*?%%@@%SS
    ;#@#@S%?%%+++?S?S+++?S?%%@#@#*
     *###+#S?@@#@@S%@@#@@%?@+S@#%
     ;#@#++%%?%#@@*;#@#%%%%*+S##*
      ?*##SS%%SS%S;,%S%S%%SS#@+S,
      ;?%#@@@SS###SS##SSS#@@@%?+
      ,++?#S#%%?#S##S#S?SS#SS;+:
      ,*SSS?*?SSS%%%?SS%%*?%SS?,
        ,;+?SS%%%%%%%%%%SS?*+:
            ,*#%???%??%#%,
              +%SSSSSS%*,
                ,,  ,,,
""",
    """
(。_。)
""",
]

HELP_MESSAGE = """
 Key cheat sheet
 ===============

 Arrow Keys -> Scroll contents

 S -> [S]earch the data
 F -> [F]ilter output data
 O -> [O]rder data by a column
 C -> [C]opy data to clipboard (selected entry)
 ENTER -> Do an operation on the selected entry

 H -> Toggle this [H]elpmessage
 Q -> [Q]uit program
"""

DEFAULT_SCHEMES = {
    "f4173947c70e4152a62582b1ca8a85db": [
        ["Application", "None"],
        ["Password", "Password"],
        ["Changedate", "Hidden"],
        ["Creationdate", "Hidden"],
    ],
    "a4c831c95bf74283b28858835c253513": [
        ["Application", "None"],
        ["Verification through", "None"],
        ["Email used", "Truncate"],
        ["Changedate", "Hidden"],
        ["Creationdate", "Hidden"],
    ],
}

INSTRUCTIONS = {"add": "What scheme do you want to add the entry to?"}

CONSTRAINTS = ["None", "Password", "Truncate", "Hidden"]

FOOTER_TEXT = ["[H]elp", "[Q]uit"]

NAME_REGEX = r"^[\S\s]+$"
