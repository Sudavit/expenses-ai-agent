# create unset commands for all variables set in .env
# run it with

#       source <(unenv)

# to unset them

sed '/^#/d; s/export /unset /; s/=.*//' .env
