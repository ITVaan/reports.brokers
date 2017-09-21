# Linux dist
FROM fedora:25

# Installation system requirements
RUN yum install -y git gcc file libevent-devel python-devel \
  sqlite-devel zeromq-devel libffi-devel openssl-devel systemd-python tmux

# MariaDB 10.2
RUN dnf install -y wget
RUN wget -O /etc/yum.repos.d/MariaDB.repo http://mariadb.if-not-true-then-false.com/fedora/$(rpm -E %fedora)/$(uname -i)/10_2
RUN yum install -y mariadb mariadb-server redhat-rpm-config

# Clone project
RUN mkdir /usr/src/reports.brokers/
RUN git clone https://github.com/ITVaan/reports.brokers.git /usr/src/reports.brokers

# Environment
RUN pip install virtualenv --upgrade
RUN virtualenv --python=/usr/bin/python2.7 /usr/src/reports.brokers/.env

# Entrypoint
COPY docker-entrypoint.sh /usr/local/bin/

RUN chmod +x /usr/local/bin/docker-entrypoint.sh
RUN ln -s usr/local/bin/docker-entrypoint.sh

COPY base.cfg /usr/src/reports.brokers/

EXPOSE 3306 9999

ENTRYPOINT ["docker-entrypoint.sh"]
