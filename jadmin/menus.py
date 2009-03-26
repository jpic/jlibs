class Menu(list):
    def render(self, ul=True):
        html = ''
        if ul:
            html += '<ul>'
        for menuitem in self:
            html += menuitem.render()
        if ul:
            html+= '</ul>'
        return html

    def add( self, title, url=None ):
        item = MenuItem( title, url )
        self.append( item )
        return item

class MenuItem(Menu):
    def __init__(self, title, url = None):
        super(MenuItem, self).__init__()
        
        self.title = title
        if not url:
            self.url = ''
        else:
            self.url = url

    def render_inside(self):
        html = '<a href="' + self.url + '" title="' + self.title + '">' + self.title + '</a>'
        return html

    def render(self):
        inside = self.render_inside()
        if len(self) == 0:
            html = '<li>' + inside + '</li>'
        else:
            html = '<li>' + inside + '<ul>'
            for menuitem in self:
                html += menuitem.render()
            html+= '</ul></li>'
        return html

    def append_to_menus( self, menus ):
        for menu in menus:
            menu.append( self )
        return self

class MenuFactories(object):
    def __init__(self, source, menu=None):
        self.source = source
        if not menu:
            menu = Menu()
        self.menu = menu

        if isinstance(source, dict):
            self.parse_dict(self.source, self.menu)

    def parse_dict(self, source, menu):
        for k, v in source.items():
            if isinstance(v, dict):
                self.parse_dict( v, menu.add(k ) )
            else:
                menu.add( k, v )

        return menu
