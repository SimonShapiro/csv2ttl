import csv
from rdflib import Graph, XSD, Literal, URIRef, RDF
import codecs
from urllib import parse
import json
import sys
import getopt
import pprint

def csv2rdfGraph(input_file, config_dict):
    def form_id_triple(item, id_dict, forced_id=None):
        if id_dict.get("col"):
            _id = URIRef("{}{}".format(config_dict["prefixes"][id_dict["prefix"]], parse.quote_plus(item[id_dict["col"]])))
        else:
            _id = URIRef("{}{}".format(config_dict["prefixes"][id_dict["prefix"]], parse.quote_plus(forced_id)))
        value = URIRef("{}{}".format(config_dict["prefixes"][id_dict["type_prefix"]], parse.quote_plus(id_dict["type"])))
        return (_id, RDF.type, value)

    def form_literal_triple(_id, item, literal_dict):
        XSDliterals = {
            "XSD.string": XSD.string,
            "XSD.integer": XSD.integer,
            "XSD.date": XSD.date
        }
        predicate_term = literal_dict.get("alias") if literal_dict.get("alias") else literal_dict["col"]
        predicate = URIRef("{}{}".format(config_dict["prefixes"][literal_dict["prefix"]], parse.quote_plus(predicate_term)))
        # todo work out how to process nulls and defaults
        value = Literal(item[literal_dict["col"]], datatype=XSDliterals[literal_dict["type"]])
        return (_id, predicate, value)
    
    def form_link_triple(_id, link, link_dict):
        predicate_term = link_dict.get("alias") if link_dict.get("alias") else link_dict["col"]
        predicate = URIRef("{}{}".format(config_dict["prefixes"][link_dict["prefix"]], predicate_term))
        link_value = URIRef("{}{}".format(config_dict["prefixes"][link_dict["link_prefix"]], parse.quote_plus(item[link_dict["col"]])))
        return (_id, predicate, link_value)


    g = Graph()
    with codecs.open(input_file, mode='r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for item in reader:
            print(item)
            id_triple = form_id_triple(item, config_dict["id"], forced_id=item["Name"]+item["Age"])
            _id = id_triple[0]
            g.add(id_triple)
            for literal in config_dict["literals"]:
                literal_triple = form_literal_triple(_id, item, literal)
                g.add(literal_triple)
            for link in config_dict["links"]:
                link_triple = form_link_triple(_id, item, link)
                g.add(link_triple)
    return g


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hi:o:c:", ["help", "input=", "output=", "config="])
    except getopt.GetoptError as e:
        print(e.msg, e.opt)
        print('utils.py -i <inputfile> -o <outputfile> -c <configfile>')
        sys.exit(2)
    print(opts,args)
    input_file = "input.ttl"
    output_file = "output.ttl"
    config_file = "config.cfg"
    for opt, arg in opts:
        if opt == '-h':
            print('utils.py -i <inputfile> -o <outputfile> -c <configfile>')
            sys.exit()
        elif opt in ("-i", "--input"):
            input_file = arg
        elif opt in ("-o", "--output"):
            output_file = arg
        elif opt in ("-c", "--config"):
            config_file = arg

    with open(config_file) as f:
        try:
        #
            config = json.loads(f.read())
        except:
            print("Problem parsing config file, ensure that it is well-formed json")
            sys.exit(3)

    pprint.pprint(config)
    g1 = csv2rdfGraph(input_file, config)
    for row in g1.triples((None, None, None)):
        print(row)
    print(len(g1))
    g1.serialize(output_file, format="turtle")


if __name__ == "__main__":
   main(sys.argv[1:])
