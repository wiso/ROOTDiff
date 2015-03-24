import logging
logging.basicConfig(level=logging.INFO)

import ROOT


def diff_directory(directory1, directory2, different_names=False):
    if different_names:
        # uses for the TFile
        logging.info("checking %s and %s", directory1.GetName(), directory2.GetName())
    else:
        logging.info("checking %s", directory1.GetName())
    keys1 = [k.GetName() for k in directory1.GetListOfKeys()]
    keys2 = [k.GetName() for k in directory2.GetListOfKeys()]

    d12 = set(keys1) - set(keys2)
    if d12:
        for k in sorted(d12):
            print "- {}".format(k)
    d21 = set(keys2) - set(keys1)
    if d21:
        for k in sorted(d21):
            print "+ {}".format(k)

    common_keys = set(keys1).intersection(keys2)

    all_equal = True
    for k in common_keys:
        obj1 = directory1.Get(k)
        obj2 = directory2.Get(k)

        if type(obj1) != type(obj2):
            print "different type {}".format(k)
            all_equal = False
            continue

        if issubclass(type(obj1), ROOT.TDirectory):
            if not diff_directory(obj1, obj2):
                all_equal = False
            continue

        logging.warning("type %s not supported", type(obj1))

    return all_equal


def diff(first_file, second_file):
    f1 = ROOT.TFile.Open(first_file)
    f2 = ROOT.TFile.Open(second_file)

    if not f1:
        print "{} do not exists. Exit".format(first_file)
        return 1
    if not f2:
        print "{} do not exists. Exit".format(second_file)
        return 1

    return diff_directory(f1, f2, True)


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("first_file", help="first file")
    parser.add_argument("second_file", help="second file")

    args = parser.parse_args()

    diff(args.first_file, args.second_file)
