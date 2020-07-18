import asm3.db
import asm3.dbupdate
import os

# The path to the folder containing the ASM3 modules
PATH = os.path.dirname(os.path.abspath(__file__)) + os.sep

dbo = asm3.db.get_database()
dbo.locale = 'en'
dbo.installpath = PATH
asm3.dbupdate.install(dbo)
