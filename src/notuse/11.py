class a(object):
    aa=1
    def bb(self):
        a.aa=2


c=a()
c.bb()
print a.aa