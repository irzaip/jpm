# coding: utf8
# try something like

@auth.requires_login()
def index():
    response.title="Priority"
    response.subtitle="Jenis-jenis prioritas yang digunakan"
    response.view="generic.html"
    
    grid = SQLFORM.smartgrid(db.priority)
    return locals()
