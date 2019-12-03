#!/bin/bash

# test the shellscripts in the current directory

# --exclude=CODE1,CODE2..  Exclude types of warnings

function shell_check {

    # exclude Codes :
    # SC1091 not following external sources

    # check the tests
    shellcheck --shell=bash --color=always \
        --exclude=SC1091 \
        --exclude=SC1090 \
         ./*.sh

}

shell_check
