Long story short
----------------

Installation
============

1. get it from where-you-want repository

2. Get VirtualEnv and VirtualEnvWrapper set up. See here for further details: http://www.doughellmann.com/docs/virtualenvwrapper/

3. Create a virtualenvironment

        mkvirtualenv venv

4. Install the required python dependancies:

        pip install -r requirements.txt

5. Edit `dispatcher/settings.py` to change settings that better fit you needs

6. Prepare the SQLAlchemy Database:

        python manage.py reset_db

7. Populate db
	
	python manage.py populate_db

8. Run a development server:

        python runserver.py 

10. Read the docs :)

This projects is funded by:

PIA - Pacchetti Integrati di Agevolazioni "Industria, Artigianato e Servizi" ( Annualita' 2010)
Programmazione Unitaria 2007/2013
P.O. FESR 2007/2013
Regione Autonoma della Sardegna

