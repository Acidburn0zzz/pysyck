
from parsers import *

generic_parser = GenericParser()
parse = generic_parser.load
parse_documents = generic_parser.load_documents

parser = Parser()
load = parser.load
load_documents = parser.load_documents
add_type = parser.add_type
add_domain_type = parser.add_domain_type
add_builtin_type = parser.add_builtin_type
add_python_type = parser.add_python_type
add_private_type = parser.add_private_type

