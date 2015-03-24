import logging
logging.basicConfig(level=logging.INFO)

import ROOT


def abs_name(obj):
    try:
        directory = obj.GetDirectory()
    except AttributeError:
        directory = None
    result = ""
    if directory:
        result += directory.GetPath().split(":")[1] + "/" + obj.GetName()
    else:
        result += obj.GetName()
    result += " ({})".format(obj.GetTitle())
    return result


def diff_axis(axis1, axis2):
    logging.debug("comparing axis %s and %s", axis1.GetName(), axis2.GetName())
    if (axis1.GetNbins() != axis2.GetNbins()):
        print "< {} n bins = {}".format(abs_name(axis1), axis1.GetNbins())
        print "> {} n bins = {}".format(abs_name(axis2), axis2.GetNbins())
        return False
    for ibin in xrange(1, (axis1.GetNbins() + 1)):
        if axis1.GetBinLowEdge(ibin) != axis2.GetBinLowEdge(ibin):
            print "< {} different binning (bin {} = {})".format(abs_name(axis1), ibin,
                                                                axis1.GetBinLowEdge(ibin))
            print "> {} different binning (bin {} = {})".format(abs_name(axis2), ibin,
                                                                axis2.GetBinLowEdge(ibin))
            return False
    return True


def diff_graph(graph1, graph2):
    def get_x(graph):
        x = graph.GetX()
        x.SetSize(graph.GetN())
        return x

    def get_y(graph):
        y = graph.GetY()
        y.SetSize(graph.GetN())
        return y

    if graph1.GetN() != graph2.GetN():
        print "< {} npoints = {}".format(graph1.GetN())
        print "> {} npoints = {}".format(graph2.GetN())
        return False
    # TODO(sort the points?)
    for ipoint, (x1, y1, x2, y2) in enumerate(zip(get_x(graph1), get_y(graph1),
                                                  get_x(graph2), get_y(graph2))):
        if (x1, y1) != (x2, y2):
            print "< {} point {} = ({}, {})".format(abs_name(graph1), ipoint, x1, y1)
            print "> {} point {} = ({}, {})".format(abs_name(graph2), ipoint, x2, y2)
            return False


def diff_graph_asym_errors(graph1, graph2):
    if not diff_graph(graph1, graph2):
        return False
    for i in xrange(graph1.GetN()):
        if graph1.GetErrorXhigh(i) != graph2.GetErrorXhigh(i):
            print "< {} point {} error x-up = {}".format(abs_name(graph1), i, graph1.GetErrorXhigh(i))
            print "> {} point {} error x-up = {}".format(abs_name(graph2), i, graph2.GetErrorXhigh(i))
            return False
        if graph1.GetErrorXlow(i) != graph2.GetErrorXlow(i):
            print "< {} point {} error x-low = {}".format(abs_name(graph1), i, graph1.GetErrorXlow(i))
            print "> {} point {} error x-low = {}".format(abs_name(graph2), i, graph2.GetErrorXlow(i))
            False
        if graph1.GetErrorYhigh(i) != graph2.GetErrorYhigh(i):
            print "< {} point {} error y-up = {}".format(abs_name(graph1), i, graph1.GetErrorYhigh(i))
            print "> {} point {} error y-up = {}".format(abs_name(graph2), i, graph2.GetErrorYhigh(i))
            return False
        if graph1.GetErrorYlow(i) != graph2.GetErrorYlow(i):
            print "< {} point {} error y-low = {}".format(abs_name(graph1), i, graph1.GetErrorYlow(i))
            print "> {} point {} error y-low = {}".format(abs_name(graph2), i, graph2.GetErrorYlow(i))
            False
        return True


def diff_histos(histo1, histo2):
    logging.debug("checking %s", histo1.GetName())
    if (histo1.GetNbinsX() != histo2.GetNbinsX()):
        print "< {} nbins = {}".format(abs_name(histo1), histo1.GetNbinsX())
        print "> {} nbins = {}".format(abs_name(histo2), histo2.GetNbinsX())
    for ibin in xrange(1, (histo1.GetNbinsX() + 1)):
        if histo1.GetBinLowEdge(ibin) != histo2.GetBinLowEdge(ibin):
            print "< {} different binning (bin {} = {})".format(abs_name(histo1), ibin,
                                                                histo1.GetBinLowEdge(ibin))
            print "> {} different binning (bin {} = {})".format(abs_name(histo2), ibin,
                                                                histo2.GetBinLowEdge(ibin))
            return False
    for ibin in xrange(1, (histo1.GetNbinsX() + 1)):
        if histo1.GetBinContent(ibin) != histo2.GetBinContent(ibin):
            print "< {} different content (bin {} = {})".format(abs_name(histo1), ibin,
                                                                histo1.GetBinContent(ibin))
            print "> {} different content (bin {} = {})".format(abs_name(histo2), ibin,
                                                                histo2.GetBinContent(ibin))
            return False

    if histo1.GetEntries() != histo2.GetEntries():
        print "< {} different entries ({})".format(abs_name(histo1), histo1.GetEntries())
        print "> {} different entries ({})".format(abs_name(histo2), histo2.GetEntries())
        return False

    return True


def diff_list(list1, list2):
    result = True
    for obj1, obj2 in zip(list1, list2):
        result &= diff_obj(obj1, obj2)
    return result


def diff_obj(obj1, obj2):
    if type(obj1) != type(obj2):
        print "< {} type = {}".format(abs_name(obj1), type(obj1))
        print "> {} type = {}".format(abs_name(obj2), type(obj2))
        return False

    if issubclass(type(obj1), ROOT.TDirectory):
        return diff_directory(obj1, obj2)

    if type(obj1) is ROOT.TAxis:
        return diff_axis(obj1, obj2)

    if type(obj1) is ROOT.TGraph:
        return diff_graph(obj1, obj2)

    if type(obj1) in (ROOT.TGraphErrors, ROOT.TGraphAsymmErrors):
        return diff_graph_asym_errors(obj1, obj2)

    if issubclass(type(obj1), ROOT.TH2):
        logging.warning("cannot compare %s: type %s not supported", abs_name(obj1), type(obj1))
        return True

    if type(obj1) in (ROOT.TH1, ROOT.TH1F, ROOT.TH1D, ROOT.TH1I, ROOT.TProfile):
        return diff_histos(obj1, obj2)

    if type(obj1) is ROOT.TList:
        return diff_list(obj1, obj2)

    logging.warning("cannot compare %s: type %s not supported", abs_name(obj1), type(obj1))
    return True


def diff_directory(directory1, directory2, different_names=False):
    if different_names:
        # uses for the TFile
        logging.debug("checking %s and %s", directory1.GetName(), directory2.GetName())
    else:
        logging.debug("checking %s", directory1.GetName())
    keys1 = [k.GetName() for k in directory1.GetListOfKeys()]
    keys2 = [k.GetName() for k in directory2.GetListOfKeys()]

    d12 = set(keys1) - set(keys2)
    if d12:
        for k in sorted(d12):
            print "< {}".format(k)
    d21 = set(keys2) - set(keys1)
    if d21:
        for k in sorted(d21):
            print "> {}".format(k)

    common_keys = set(keys1).intersection(keys2)

    all_equal = True
    for k in common_keys:
        obj1 = directory1.Get(k)
        obj2 = directory2.Get(k)

        all_equal &= diff_obj(obj1, obj2)

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
