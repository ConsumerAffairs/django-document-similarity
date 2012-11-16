docsim:
    user.present:
        - home: /home/docsim
        - shell: /bin/bash

{% if salt['cmd.has_exec']('git') %}

git://github.com/jgmize/django-document-similarity.git:
    git.latest:
        - runas: docsim
        - target: /home/docsim/django-document-similarity
        - require:
            - user: docsim
{% endif %}

mkvirtualenv:
    cmd.run:
        - shell: /bin/bash
        - name: 'su - docsim -c "bash -l -i -c \"mkvirtualenv dds -a /home/docsim/django-document-similarity\""'
        - unless: test -d /home/docsim/.virtualenvs/dds
        - require:
            - pkg: virtualenvwrapper
            - user: docsim
            - git.latest: git://github.com/jgmize/django-document-similarity.git

scipy_dependencies:
    pkg.installed:
        - names:
            - libatlas-dev
            - liblapack-dev
            - gfortran

dds_pip_install_numpy:
    cmd.run:
        - user: docsim
        - name: '/home/docsim/.virtualenvs/dds/bin/pip install numpy'
        - unless: test -d /home/docsim/.virtualenvs/dds/lib/python2.7/site-packages/numpy
        - require:
            - cmd: mkvirtualenv
            - pkg.installed: libatlas-dev
            - pkg.installed: liblapack-dev
            - pkg.installed: gfortran

dds_pip_install_scipy:
    cmd.run:
        - user: docsim
        - name: '/home/docsim/.virtualenvs/dds/bin/pip install scipy'
        - unless: test -d /home/docsim/.virtualenvs/dds/lib/python2.7/site-packages/scipy
        - require:
            - cmd: dds_pip_install_numpy

dds_pip_install_gensim:
    cmd.run:
        - user: docsim
        - name: '/home/docsim/.virtualenvs/dds/bin/pip install gensim'
        - unless: test -d /home/docsim/.virtualenvs/dds/lib/python2.7/site-packages/gensim
        - require:
            - cmd: dds_pip_install_scipy

dds_pip_install_simserver:
    cmd.run:
        - user: docsim
        - name: '/home/docsim/.virtualenvs/dds/bin/pip install simserver'
        - unless: test -d /home/docsim/.virtualenvs/dds/lib/python2.7/site-packages/simserver
        - require:
            - cmd: dds_pip_install_gensim

dds_pip_install_sklearn:
    cmd.run:
        - user: docsim
        - name: '/home/docsim/.virtualenvs/dds/bin/pip install scikit-learn'
        - unless: test -d /home/docsim/.virtualenvs/dds/lib/python2.7/site-packages/sklearn
        - require:
            - cmd: dds_pip_install_scipy

dds_pip_install_yaml:
    pkg.installed:
        - name: libyaml-dev
    cmd.run:
        - user: docsim
        - name: '/home/docsim/.virtualenvs/dds/bin/pip install PyYAML'
        - unless: test -d /home/docsim/.virtualenvs/dds/lib/python2.7/site-packages/yaml
        - require:
            - pkg: libyaml-dev
            - pkg: build-essential
            - pkg: python-dev
            - cmd: mkvirtualenv

dds_pip_install_requirements:
    cmd.run:
        - user: docsim
        - cwd: /home/docsim/django-document-similarity
        - name: '/home/docsim/.virtualenvs/dds/bin/pip install -r requirements.txt'
        - require:
            - cmd: dds_pip_install_sklearn
            - cmd: dds_pip_install_simserver
            - cmd: dds_pip_install_yaml
            - pkg: libmysqlclient-dev

nltk_tokenizers_punkt:
    pkg.installed:
        - name: unzip
    file.managed:
        # originally obtained by running nltk.download('punkt') from a python shell
        - name: /home/docsim/nltk_data/tokenizers/punkt.zip
        - source: salt://nltk_data/tokenizers/punkt.zip
        - user: docsim
        - makedirs: True
        - require:
            - user: docsim
    cmd.run:
        - name: 'unzip punkt.zip'
        - cwd: /home/docsim/nltk_data/nltk_data/tokenizers
        - unless: test -d /home/docsim/nltk_data/tokenizers/punkt
        - user: docsim
        - require:
            - file.managed: /home/docsim/nltk_data/tokenizers/punkt.zip
            - pkg.installed: unzip

# vim:set ft=yaml:
