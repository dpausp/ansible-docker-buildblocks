#!/bin/zsh
# Removing locale files
set -x

rm -rf /usr/share/locale/**/**.mo
 
# Removing python tests
rm -rf /usr/lib/python*/test

# removing binutils info / man pages
rm -rf /usr/share/binutils-data/*/*/info
rm -rf /usr/share/binutils-data/*/*/man

# Removing docs
rm -rf /usr/share/gtk-doc
rm -rf /usr/share/man/*
rm -rf /usr/share/doc/*

# remove logs
rm -f /var/log/emerge*log
rm -rf /var/log/portage

# remove shell history and other zsh stuff
rm -f /root/.*sh_history /root/.zcompdump /root/.zdirs

# tmp clean
find /tmp/ -not -type d -not -path '/tmp/ansible-tmp*' -not -name '.keep' -delete
find /tmp/ -type d -not -path '/tmp/ansible-tmp*' -not -name 'tmp' -exec rmdir -p --ignore-fail-on-non-empty {} +
