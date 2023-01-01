# Luca-alike

\-- Documentations 
            
            \-- Sql-scripts 
            
            \-- Static files
                   \--               # css and images
            
            \-- Templates 
                  \--                 # All HTML Files
            
            \--Test                           # tests 
                    \-- test.py
                    
                    
           -- .gitignore                        # ignore
           -- README.md                         # Documentation of program
           -- app.py                            # main python file
           -- db.py                             # dababase file
           -- imprint.txt                       # imprint 
           --project.sqlite                     # sqlite file
           -- requirements.txt                  # requirements file
           
           
# Complete installation guide 


Create virtual environment

            $ python3 -m venv se-env

Start virtual environment

            $ source se-env/bin/activate

Please make sure pip is updated. If not, use 

            $ pip3 install --upgrade pip 

Install all the dependencies

            $ pip3 install -r requirements.txt

Create database

            $ python3 db.py


Run python server

            $ python3 app.py
