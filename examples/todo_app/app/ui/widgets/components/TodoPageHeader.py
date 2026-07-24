import htpy
import hypie as hp


class TodoPageHeader(hp.ServerComponent):
    def template(self):
        return htpy.h1(class_="text-4xl")["Todos"]
