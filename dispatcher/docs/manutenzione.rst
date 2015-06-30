======================
Gestire la piattaforma
======================


Attualmente ci sono due istanze attive di Orchestrator/Cistern:

- produzione
- sviluppo

Le istanze sono disallineate in termini di evoluzione, entrambe usano virtualenv per il funzionamento quindi prima di fare qualsiasi 
cosa attivare virtualenv sull'ambiente 

.. WARNING::
   **produzione e sviluppo hanno due venv diversi**



L'istanza di produzione e' eseguita con l'utente achmed, si puo' trovare sotto:

``/home/achmed/produzione/``

i log ed il db si possono trovare qui:

``/home/achmed/produzione/log_and_db/``


L'istanza di sviluppo e' eseguita con l'utente root, si puo' trovare sotto:

``/root/middleware/``
    
i log ed il db si possono trovare qui:

``/tmp/``


per attivare il virtualenv in **produzione**:

.. code-block:: guess

        su - achmed
        cd ~/produzione
        source venv/bin/activate


per attivare il virtualenv in **sviluppo**:

.. code-block:: guess

        cd middleware
        source venv/bin/activate


per avviare il sistema in produzione:

.. code-block:: guess

            cd produzione

            # avvio orchestrator
            cd orchestrator
            gunicorn -D -w 1 -b 0.0.0.0:5070 --access-logfile /tmp/access_orche.log dispatcher:app


            # avvio cistern

            cd .. && cd cistern
            gunicorn -D -w 1 -b 0.0.0.0:5071 --access-logfile /tmp/access_log.log store:app

            # avvio demoni

            cd daemons
            python loops.py start
            python cook_recipe.py start



per avviare il sistema in sviluppo, o si segue la stessa strada del sistema in produzione ( modificando i path )
o si possono avviare i frontend API tramite il web server di Flask


.. code-block:: guess

        cd produzione

        # avvio orchestrator

        cd orchestrator
        python runserver.py


        # avvio cistern

        cd .. && cd cistern
        python runserver.py

        # avvio demoni

        cd daemons
        python loops.py start

        python cook_recipe.py start



Nel sistema in sviluppo il db e' posizionato sotto /tmp/ quindi all'avvio della macchina c'e' da ricreare l'ambiente,
sempre con virtualenv attivo:

.. code-block:: guess

    cd orchestrator

    python manage.py reset_db

    python manage.py populate_db


I componenti realmente attivi sono :

- loops.py
- cook_recipe.py

Per fermare eventuali automatismi identificare quale ambiente ha i due demoni attivi ( produzione e/o sviluppo ) e killarli con 

.. code-block:: guess

    cd daemons
    python loops.py stop
    python cook_recipe.py stop

