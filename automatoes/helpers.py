#!/usr/bin/env python
#
# Copyright 2019-2022 Flávio Gonçalves Garcia
# Copyright 2016-2017 Veeti Paananen under MIT License
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
import locale
import sys


def confirm(msg, default=True):
    no_encode_found = False
    print("*********************************************************")
    print("Inside the confirm function!!!!\n\n")
    print("Please post the output at:\n %s" %
          "https://github.com/candango/automatoes/issues/103")
    while True:
        choices = "Y/n" if default else "y/N"
        answer = ""
        encoding = ""
        try:
            answer, encoding = decode(input("%s [%s] " % (msg, choices)))
        except UnicodeDecodeError as ude:
            print("*********************************************************")
            print("This exception is on the python input function WTF!?:")
            print("DECODING!!!!")
            print(ude)
            print("*********************************************************")
            print("Preferred encoding: %s" % locale.getpreferredencoding())
            print("Default locale:\n lang: %s, encoding: %s"
                  % locale.getdefaultlocale())
            print("Current input encoding: %s" % sys.stdin.encoding)
            print("Current output encoding: %s" % sys.stdout.encoding)
            print("Byte order: %s" % sys.byteorder)
            print("Setting answer to: UnicodeDecodeError")
            answer = "UnicodeDecodeError"
            print("*********************************************************")
        except UnicodeEncodeError as uee:
            print("*********************************************************")
            print("This exception is on the python input function WTF!?:")
            print("ENCODING!!!!")
            print(uee)
            print("*********************************************************")
            print("Preferred encoding: %s" % locale.getpreferredencoding())
            print("Default locale:\n lang: %s, encoding: %s"
                  % locale.getdefaultlocale())
            print("Current input encoding: %s" % sys.stdin.encoding)
            print("Current output encoding: %s" % sys.stdout.encoding)
            print("Byte order: %s" % sys.byteorder)
            print("*********************************************************")

        print("*********************************************************")
        if "UnicodeDecodeError" in answer:
            print("Dude, please type this: y, yes, n, no")
            print("No more ç/ű/etc... + backspace + backspace or whatever "
                  "UnicodeDecodeError you can generate with your keyboard....")
            print("Fix here is just ignore.... and keep asking for valid "
                  "responses")
        if "no encode found" in answer:
            no_encode_found = True
            print("We need more encodes....")
            print("*********************************************************")
        print("Answer: %s" % answer)
        print("Answer encoded with: %s" % encoding)
        print("Preferred encoding: %s" % locale.getpreferredencoding())
        print("Default locale:\n lang: %s, encoding: %s"
              % locale.getdefaultlocale())
        print("Current input encoding: %s" % sys.stdin.encoding)
        print("Current output encoding: %s" % sys.stdout.encoding)
        print("Byte order: %s" % sys.byteorder)

        print("*********************************************************")

        answer = answer.strip().lower()

        print("Outside the confirm function!!!! Don't copy after the next"
              "line of starts...")
        print("*********************************************************")

        if no_encode_found:
            print("If this is the case, I need to add a parameter for y/n "
                  "options on `manuale register`")
            return False

        if answer in {"yes", "y"} or (default and not answer):
            return True
        if answer in {"no", "n"} or (not default and not answer):
            return False


def decode(answer: str, encoding="ascii") -> (str, str):
    print("Answer inside the decode: %s. Trying encoding: %s" %
          (answer, encoding))
    try:
        return answer.encode(encoding).decode(encoding), encoding
    except UnicodeDecodeError as ude:
        last_exception = "%s" % ude
        print(last_exception)
    except UnicodeEncodeError as uee:
        last_exception = "%s" % uee
        print(last_exception)
    if encoding != "utf-32":
        if encoding == "ascii":
            return decode(answer, "utf-8")
        if encoding == "utf-8":
            return decode(answer, "utf-16")
        if encoding == "utf-16":
            return decode(answer, "utf-32")
    return "no encode found exception(%s)" % last_exception, encoding
