#! /usr/bin/env bash
# Usage: ./showparticles.sh <pythia log> particleno1 particleno2 particleno3
# Helper script to show only the lines for the given particle numbers.
# Useful for debugging.

FILE=$1
shift 1
PIDS=$(echo $@ | tr ' ' '|')
grep -E "^[ ]+(no|$PIDS)" $FILE
