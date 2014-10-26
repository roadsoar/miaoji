#/usr/bin/env python

def echo(value=None):
  while True:
    value = (yield value)

def assert_me():
  try:
    assert 1 > 2, "1 is not more than 2"
  except Exception,e:
    print e

if __name__ == "__main__":
  generator = echo(3)
  print generator.next()
  print generator.send(6)
  assert_me()
