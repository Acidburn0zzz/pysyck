
import unittest
import parser2

EX99 = r"""
key:
value
"""

TOKENS99 = """
Should produce error.
"""

EX1 = r"""
- Mark McGwire
- Sammy Sosa
- Ken Griffey
"""

TOKENS1 = """
BLOCK_SEQ_START
ENTRY SCALAR
ENTRY SCALAR
ENTRY SCALAR
BLOCK_END
"""

NODES1 = [True, True, True]

EX2 = r"""
hr:  65    # Home runs
avg: 0.278 # Batting average
rbi: 147   # Runs Batted In
"""

TOKENS2 = """
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END
"""

NODES2 = [(True, True), (True, True), (True, True)]

EX3 = r"""
american:
  - Boston Red Sox
  - Detroit Tigers
  - New York Yankees
national:
  - New York Mets
  - Chicago Cubs
  - Atlanta Braves
"""

TOKENS3 = """
BLOCK_MAP_START
KEY SCALAR VALUE
    BLOCK_SEQ_START
    ENTRY SCALAR
    ENTRY SCALAR
    ENTRY SCALAR
    BLOCK_END
KEY SCALAR VALUE
    BLOCK_SEQ_START
    ENTRY SCALAR
    ENTRY SCALAR
    ENTRY SCALAR
    BLOCK_END
BLOCK_END
"""

NODES3 = [(True, [True, True, True]), (True, [True, True, True])]

EX4 = r"""
-
  name: Mark McGwire
  hr:   65
  avg:  0.278
-
  name: Sammy Sosa
  hr:   63
  avg:  0.288
"""

TOKENS4 = """
BLOCK_SEQ_START
ENTRY
    BLOCK_MAP_START
    KEY SCALAR VALUE SCALAR
    KEY SCALAR VALUE SCALAR
    KEY SCALAR VALUE SCALAR
    BLOCK_END
ENTRY
    BLOCK_MAP_START
    KEY SCALAR VALUE SCALAR
    KEY SCALAR VALUE SCALAR
    KEY SCALAR VALUE SCALAR
    BLOCK_END
BLOCK_END
"""

NODES4 = [[(True, True), (True, True), (True, True)], [(True, True), (True, True), (True, True)]]

EX5 = r"""
- [name        , hr, avg  ]
- [Mark McGwire, 65, 0.278]
- [Sammy Sosa  , 63, 0.288]
"""

TOKENS5 = """
BLOCK_SEQ_START
ENTRY FLOW_SEQ_START SCALAR ENTRY SCALAR ENTRY SCALAR FLOW_SEQ_END
ENTRY FLOW_SEQ_START SCALAR ENTRY SCALAR ENTRY SCALAR FLOW_SEQ_END
ENTRY FLOW_SEQ_START SCALAR ENTRY SCALAR ENTRY SCALAR FLOW_SEQ_END
BLOCK_END
"""

NODES5 = [[True, True, True], [True, True, True], [True, True, True]]

EX6 = r"""
Mark McGwire: {hr: 65, avg: 0.278}
Sammy Sosa: {
    hr: 63,
    avg: 0.288
  }
"""

TOKENS6 = """
BLOCK_MAP_START
KEY SCALAR VALUE
    FLOW_MAP_START KEY SCALAR VALUE SCALAR ENTRY KEY SCALAR VALUE SCALAR FLOW_MAP_END
KEY SCALAR VALUE
    FLOW_MAP_START KEY SCALAR VALUE SCALAR ENTRY KEY SCALAR VALUE SCALAR FLOW_MAP_END
BLOCK_END    
"""

NODES6 = [(True, [(True, True), (True, True)]), (True, [(True, True), (True, True)])]

EX7 = r"""
# Ranking of 1998 home runs
---
- Mark McGwire
- Sammy Sosa
- Ken Griffey

# Team ranking
---
- Chicago Cubs
- St Louis Cardinals
"""

TOKENS7 = """
DOCUMENT_START 
BLOCK_SEQ_START
ENTRY SCALAR
ENTRY SCALAR
ENTRY SCALAR
BLOCK_END

DOCUMENT_START 
BLOCK_SEQ_START
ENTRY SCALAR
ENTRY SCALAR
BLOCK_END
"""

NODES7 = ([True, True, True], [True, True])

EX8 = r"""
---
time: 20:03:20
player: Sammy Sosa
action: strike (miss)
...
---
time: 20:03:47
player: Sammy Sosa
action: grand slam
...
"""

TOKENS8 = """
DOCUMENT_START
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END
DOCUMENT_END

DOCUMENT_START
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END
DOCUMENT_END
"""

NODES8 = ([(True, True), (True, True), (True, True)], [(True, True), (True, True), (True, True)])

EX9 = r"""
---
hr: # 1998 hr ranking
  - Mark McGwire
  - Sammy Sosa
rbi:
  # 1998 rbi ranking
  - Sammy Sosa
  - Ken Griffey
"""

TOKENS9 = """
DOCUMENT_START
BLOCK_MAP_START
KEY SCALAR VALUE
    BLOCK_SEQ_START
    ENTRY SCALAR
    ENTRY SCALAR
    BLOCK_END
KEY SCALAR VALUE
    BLOCK_SEQ_START
    ENTRY SCALAR
    ENTRY SCALAR
    BLOCK_END
BLOCK_END
"""

NODES9 = [(True, [True, True]), (True, [True, True])]

EX10 = r"""
---
hr:
  - Mark McGwire
  # Following node labeled SS
  - &SS Sammy Sosa
rbi:
  - *SS # Subsequent occurrence
  - Ken Griffey
"""

TOKENS10 = """
DOCUMENT_START
BLOCK_MAP_START
KEY SCALAR VALUE
    BLOCK_SEQ_START
    ENTRY SCALAR
    ENTRY ANCHOR SCALAR
    BLOCK_END
KEY SCALAR VALUE
    BLOCK_SEQ_START
    ENTRY ALIAS
    ENTRY SCALAR
    BLOCK_END
BLOCK_END
"""

NODES10 = [(True, [True, True]), (True, ['*', True])]

EX11 = r"""
? - Detroit Tigers
  - Chicago cubs
:
  - 2001-07-23

? [ New York Yankees,
    Atlanta Braves ]
: [ 2001-07-02, 2001-08-12,
    2001-08-14 ]
"""

TOKENS11 = """
BLOCK_MAP_START
KEY
    BLOCK_SEQ_START
    ENTRY SCALAR
    ENTRY SCALAR
    BLOCK_END
VALUE
    BLOCK_SEQ_START
    ENTRY SCALAR
    BLOCK_END
KEY
    FLOW_SEQ_START SCALAR ENTRY SCALAR FLOW_SEQ_END
VALUE
    FLOW_SEQ_START SCALAR ENTRY SCALAR ENTRY SCALAR FLOW_SEQ_END
BLOCK_END
"""

NODES11 = [([True, True], [True]), ([True, True], [True, True, True])]

EX12 = r"""
---
# products purchased
- item    : Super Hoop
  quantity: 1
- item    : Basketball
  quantity: 4
- item    : Big Shoes
  quantity: 1
"""

TOKENS12 = """
DOCUMENT_START
BLOCK_SEQ_START
ENTRY
    BLOCK_MAP_START
    KEY SCALAR VALUE SCALAR
    KEY SCALAR VALUE SCALAR
    BLOCK_END
ENTRY
    BLOCK_MAP_START
    KEY SCALAR VALUE SCALAR
    KEY SCALAR VALUE SCALAR
    BLOCK_END
ENTRY
    BLOCK_MAP_START
    KEY SCALAR VALUE SCALAR
    KEY SCALAR VALUE SCALAR
    BLOCK_END
BLOCK_END
"""

NODES12 = [[(True, True), (True, True)], [(True, True), (True, True)], [(True, True), (True, True)]]

EX13 = r"""
# ASCII Art
--- |
  \//||\/||
  // ||  ||__
"""

TOKENS13 = """
DOCUMENT_START SCALAR
"""

NODES13 = True

EX14 = r"""
---
  Mark McGwire's
  year was crippled
  by a knee injury.
"""

TOKENS14 = """
DOCUMENT_START SCALAR
"""

NODES14 = True

EX15 = r"""
>
 Sammy Sosa completed another
 fine season with great stats.

   63 Home Runs
   0.288 Batting Average

 What a year!
"""

TOKENS15 = """
SCALAR
"""

NODES15 = True

EX16 = r"""
name: Mark McGwire
accomplishment: >
  Mark set a major league
  home run record in 1998.
stats: |
  65 Home Runs
  0.278 Batting Average
"""

TOKENS16 = """
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END
"""

NODES16 = [(True, True), (True, True), (True, True)]

EX17 = r"""
unicode: "Sosa did fine.\u263A"
control: "\b1998\t1999\t2000\n"
hexesc:  "\x13\x10 is \r\n"

single: '"Howdy!" he cried.'
quoted: ' # not a ''comment''.'
tie-fighter: '|\-*-/|'
"""

TOKENS17 = """
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END
"""

NODES17 = [(True, True), (True, True), (True, True), (True, True), (True, True), (True, True)]

EX18 = r"""
plain:
  This unquoted scalar
  spans many lines.

quoted: "So does this
  quoted scalar.\n"
"""

TOKENS18 = """
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END
"""

NODES18 = [(True, True), (True, True)]

EX19 = r"""
canonical: 12345
decimal: +12,345
sexagesimal: 3:25:45
octal: 014
hexadecimal: 0xC
"""

TOKENS19 = """
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END
"""

NODES19 = [(True, True), (True, True), (True, True), (True, True), (True, True)]

EX20 = r"""
canonical: 1.23015e+3
exponential: 12.3015e+02
sexagesimal: 20:30.15
fixed: 1,230.15
negative infinity: -.inf
not a number: .NaN
"""

TOKENS20 = """
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END
"""

NODES20 = [(True, True), (True, True), (True, True), (True, True), (True, True), (True, True)]

EX21 = r"""
null: ~
true: y
false: n
string: '12345'
"""

TOKENS21 = """
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END
"""

NODES21 = [(True, True), (True, True), (True, True), (True, True)]

EX22 = r"""
canonical: 2001-12-15T02:59:43.1Z
iso8601: 2001-12-14t21:59:43.10-05:00
spaced: 2001-12-14 21:59:43.10 -5
date: 2002-12-14
"""

TOKENS22 = """
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END
"""

NODES22 = [(True, True), (True, True), (True, True), (True, True)]

EX23 = r"""
---
not-date: !!str 2002-04-28

picture: !!binary |
 R0lGODlhDAAMAIQAAP//9/X
 17unp5WZmZgAAAOfn515eXv
 Pz7Y6OjuDg4J+fn5OTk6enp
 56enmleECcgggoBADs=

application specific tag: !something |
 The semantics of the tag
 above may be different for
 different documents.
"""

TOKENS23 = """
DOCUMENT_START
BLOCK_MAP_START
KEY SCALAR VALUE TAG SCALAR
KEY SCALAR VALUE TAG SCALAR
KEY SCALAR VALUE TAG SCALAR
BLOCK_END
"""

NODES23 = [(True, True), (True, True), (True, True)]

EX24 = r"""
%TAG ! tag:clarkevans.com,2002:
--- !shape
  # Use the ! handle for presenting
  # tag:clarkevans.com,2002:circle
- !circle
  center: &ORIGIN {x: 73, y: 129}
  radius: 7
- !line
  start: *ORIGIN
  finish: { x: 89, y: 102 }
- !label
  start: *ORIGIN
  color: 0xFFEEBB
  text: Pretty vector drawing.
"""

TOKENS24 = """
DIRECTIVE
DOCUMENT_START TAG
BLOCK_SEQ_START
ENTRY TAG
    BLOCK_MAP_START
    KEY SCALAR VALUE ANCHOR
        FLOW_MAP_START KEY SCALAR VALUE SCALAR ENTRY KEY SCALAR VALUE SCALAR FLOW_MAP_END
    KEY SCALAR VALUE SCALAR
    BLOCK_END
ENTRY TAG
    BLOCK_MAP_START
    KEY SCALAR VALUE ALIAS
    KEY SCALAR VALUE
        FLOW_MAP_START KEY SCALAR VALUE SCALAR ENTRY KEY SCALAR VALUE SCALAR FLOW_MAP_END
    BLOCK_END
ENTRY TAG
    BLOCK_MAP_START
    KEY SCALAR VALUE ALIAS
    KEY SCALAR VALUE SCALAR
    KEY SCALAR VALUE SCALAR
    BLOCK_END
BLOCK_END
"""

NODES24 = [[(True, [(True, True), (True, True)]), (True, True)],
    [(True, '*'), (True, [(True, True), (True, True)])],
    [(True, '*'), (True, True), (True, True)]]

EX25 = r"""
# sets are represented as a
# mapping where each key is
# associated with the empty string
--- !!set
? Mark McGwire
? Sammy Sosa
? Ken Griff
"""

TOKENS25 = """
DOCUMENT_START TAG
BLOCK_MAP_START
KEY SCALAR
KEY SCALAR
KEY SCALAR
BLOCK_END
"""

NODES25 = [(True, None), (True, None), (True, None)]

EX26 = r"""
# ordered maps are represented as
# a sequence of mappings, with
# each mapping having one key
--- !!omap
- Mark McGwire: 65
- Sammy Sosa: 63
- Ken Griffy: 58
"""

TOKENS26 = """
DOCUMENT_START TAG
BLOCK_SEQ_START
ENTRY
    BLOCK_MAP_START
    KEY SCALAR VALUE SCALAR
    BLOCK_END
ENTRY
    BLOCK_MAP_START
    KEY SCALAR VALUE SCALAR
    BLOCK_END
ENTRY
    BLOCK_MAP_START
    KEY SCALAR VALUE SCALAR
    BLOCK_END
BLOCK_END
"""

NODES26 = [[(True, True)], [(True, True)], [(True, True)]]

EX27 = r"""
--- !<tag:clarkevans.com,2002:invoice>
invoice: 34843
date   : 2001-01-23
bill-to: &id001
    given  : Chris
    family : Dumars
    address:
        lines: |
            458 Walkman Dr.
            Suite #292
        city    : Royal Oak
        state   : MI
        postal  : 48046
ship-to: *id001
product:
    - sku         : BL394D
      quantity    : 4
      description : Basketball
      price       : 450.00
    - sku         : BL4438H
      quantity    : 1
      description : Super Hoop
      price       : 2392.00
tax  : 251.42
total: 4443.52
comments:
    Late afternoon is best.
    Backup contact is Nancy
    Billsmer @ 338-4338.
"""

TOKENS27 = """
DOCUMENT_START TAG
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE ANCHOR
    BLOCK_MAP_START
    KEY SCALAR VALUE SCALAR
    KEY SCALAR VALUE SCALAR
    KEY SCALAR VALUE
        BLOCK_MAP_START
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        BLOCK_END
    BLOCK_END
KEY SCALAR VALUE ALIAS
KEY SCALAR VALUE
    BLOCK_SEQ_START
    ENTRY
        BLOCK_MAP_START
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        BLOCK_END
    ENTRY
        BLOCK_MAP_START
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        BLOCK_END
    BLOCK_END
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END
"""

NODES27 = [
    (True, True), (True, True), (True, [(True, True), (True, True), (True, [(True, True), (True, True), (True, True), (True, True)])]), (True, '*'),
    (True, [[(True, True), (True, True), (True, True), (True, True)], [(True, True), (True, True), (True, True), (True, True)]]), (True, True), (True, True), (True, True),
]

EX28 = r"""
---
Time: 2001-11-23 15:01:42 -5
User: ed
Warning:
  This is an error message
  for the log file
---
Time: 2001-11-23 15:02:31 -5
User: ed
Warning:
  A slightly different error
  message.
---
Date: 2001-11-23 15:03:17 -5
User: ed
Fatal:
  Unknown variable "bar"
Stack:
  - file: TopClass.py
    line: 23
    code: |
      x = MoreObject("345\n")
  - file: MoreClass.py
    line: 58
    code: |-
      foo = bar
"""

TOKENS28 = """
DOCUMENT_START
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END

DOCUMENT_START
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
BLOCK_END

DOCUMENT_START
BLOCK_MAP_START
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE SCALAR
KEY SCALAR VALUE
    BLOCK_SEQ_START
    ENTRY
        BLOCK_MAP_START
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        BLOCK_END
    ENTRY
        BLOCK_MAP_START
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        KEY SCALAR VALUE SCALAR
        BLOCK_END
    BLOCK_END
BLOCK_END
"""

NODES28 = (
    [(True, True), (True, True), (True, True)], [(True, True), (True, True), (True, True)],
    [(True, True), (True, True), (True, True), (True, [[(True, True), (True, True), (True, True)], [(True, True), (True, True), (True, True)]])],
)

MAX_TESTS = 100

class TestParser2(unittest.TestCase):

    def _testTokens(self, index, EX, TOKENS):
        try:
            tokens = None
            scanner = parser2.Scanner()
            tokens = scanner.scan('EX'+str(index), EX)
            self.failUnlessEqual(tokens, TOKENS.split())
        except:
            print "EXAMPLE #%s" % index
            print "EX:"
            print EX
            print "TOKENS:"
            print TOKENS
            print "RESULT:", tokens
            print "EXPECT:", TOKENS.split()
            raise

    def _testNodes(self, index, EX, NODES):
        try:
            nodes = None
            parser = parser2.Parser()
            nodes = parser.parse('EX'+str(index), EX)
            self.failUnlessEqual(nodes, NODES)
        except:
            print "EXAMPLE #%s" % index
            print "EX:"
            print EX
            print "RESULT:", nodes
            print "EXPECT:", NODES
            raise

    @classmethod
    def add_tests(cls, test_method_name, *tests):
        for index in range(1, MAX_TESTS):
            args = []
            for name in tests:
                if name+str(index) in globals():
                    args.append(globals()[name+str(index)])
                else:
                    break
            else:
                def test_method(self, index=index, args=args):
                    getattr(self, '_'+test_method_name)(index, *args)
                test_method.__name__ = '%s%02d' % (test_method_name, index)
                setattr(cls, test_method.__name__, test_method)

TestParser2.add_tests('testTokens', 'EX', 'TOKENS')
TestParser2.add_tests('testNodes', 'EX', 'NODES')

if __name__ == '__main__':
    unittest.main()

