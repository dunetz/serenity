FROM ubuntu:latest

RUN ["/bin/bash", "-c", "debconf-set-selections", "<<<", "postfix postfix/mailname string cloudwall.io"]
RUN ["/bin/bash", "-c", "debconf-set-selections", "<<<", "postfix postfix/main_mailer_type string 'Internet Site'"]
RUN apt-get update && apt-get install --assume-yes postfix rsyslog

# fix up the configuration to allow in-cluster relays
RUN postconf myhostname=serenity-postfix
RUN postconf "mydestination=serenity-postfix, localhost.localdomain, localhost"
RUN postconf "mynetworks=10.0.0.0/8 192.168.0.0/24 127.0.0.0/8 [::ffff:127.0.0.0]/104 [::1]/128"

# ensure chroot jail has necessary etc files
RUN cp /etc/services /var/spool/postfix/etc/services
RUN cp /etc/resolv.conf /var/spool/postfix/etc/resolv.conf

# start in foreground mode
CMD ["postfix", "start-fg"]
