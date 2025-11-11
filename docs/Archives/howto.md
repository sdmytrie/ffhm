Table of contents
<!-- TOC -->

- [Base données](#base-donn%C3%A9es)
    - [Infranet](#infranet)
        - [Export - Import](#export---import)
- [git](#git)
    - [Bitbucket](#bitbucket)
- [Server de production](#server-de-production)
    - [Site de production](#site-de-production)
        - [Export - Import](#export---import-1)
        - [Lancement gunicorn](#lancement-gunicorn)
- [Développement sous Windows](#d%C3%A9veloppement-sous-windows)
    - [Exécuter Django](#ex%C3%A9cuter-django)

<!-- /TOC -->

---

# Base données

## Infranet

    url: http://sd-84160.dedibox.fr/mysql/  
    database_name: prod_intranet
    user: prod_intranet
    password: z6fB3Va7Lr8NMnNP

### Export - Import

Avec `wampp` : C:\wamp64\bin\mysql\mysql5.7.19\bin\mysql.exe  

Sélectionner toutes les tables sauf `ext_log_enties`  
Import sous `ffhm_intranet`  
Arrêter `Django`  
Décommenter les lignes du fichiers `ffhm_intranet/models.py`  
Activer le pilote `mysql` pour la base `ffhm_intranet` dans `ffhm/settings.py`  
Lancer `Django`  

Lancer le script `ffhm_intranet/bin/import.py`  

    python manage.py shell
    >>> exec(open('ffhm_intranet/bin/import.py').read())


# git

## Bitbucket

    url: https://bitbucket.org/sergedmytrienko/ffhm/src/master/
    user: serge@dmytrienko.fr


# Server de production

    ip: 5.196.89.180
    user sdmytrie

## Site de production

    su - www-data
    ROOT=/opt/www/ffhm.dmytrienko.tld
    environnement python: source ffhmenv/bin/
    site: $ROOT/site

### Export - Import

Idem que la pré-production.  

### Lancement gunicorn

Gunicorn permet de faire le lien entre `Django` et `Apache`.  

    En tant que root
    kill -9 $(ps -ef | grep [g]unicorn | awk '{print $2}')
    cd /opt/www/ffhm.dmytrienko.tld/site
    ./gunicorn.sh


# Développement sous Windows

## Exécuter Django

    python .\manage.py runserver
    Dans un browser :
    http://<hostname>:8000
