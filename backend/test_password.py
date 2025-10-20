from passlib.context import CryptContext

# Create a bcrypt context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Example hashed password from your database
hashed = "$2b$12$AhkBMWQIrSlZUpGT6kpsmOQRAY93bctlFD3avw.d.HovjfaoFVl1m"

# The plain password you want to test
plain = "osa6NPBH"

# Verify
print(pwd_context.verify(plain[:72], hashed))  # should print True if it matches
