for i in *.bnet; do
    echo "$i"
    # run cabean with 1 minute timeouthttps://allegro.pl/oferta/glosniki-komputerowe-2-0-usb-28w-pc-laptop-14281268771
    (time timeout 30m cabean -compositional 2 "$i") >> out.log2 2>&1
    # always run python step after (regardless of timeout)
    (time python detect_attractors_test.py -f "$i" --type bnet) >> out.log2 2>&1
done
