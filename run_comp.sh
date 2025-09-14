for i in *.bnet; do
    echo "$i"
    # run cabean with 1 minute timeout
    time timeout 3m cabean -compositional 2 "$i"
    # always run python step after (regardless of timeout)
    time python detect_attractors_test.py -f "$i" --type bnet
done
