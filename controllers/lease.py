import datetime
from datetime import date


# coding: utf8
# try something like
@auth.requires_login()
def index():
    response.title = "Daftar Lease / Perjanjian Sewa"
    response.subtitle= "mencakup semua kontrak perjanjian dengan tenant."
    #response.view="main.html"
    
    dbref=db 
    qry=(db.lease.id>0)
    headers=['Nama Tenant','Unit','Sewa Awal','Sewa Akhir','frequency','Harga Sewa']

    #rows=SQLTABLE(dbref(qry).select(*sel))
    rows=db((db.lease.id>0) & (db.tenant.id==db.lease.tenant) & (db.unit.id==db.lease.unit) & (db.lease.frequency==db.frequency.id)).select()

    return dict(headers=headers,rows=rows)
    
@auth.requires_login()
def add():
    response.title="Tambahkan Lease / Perjanjian Sewa"
    response.subtitle="Bagaimanapun juga anda harus mencatat perjanjian sewa."
 
    form=SQLFORM(db.lease,submit_button="Tambahkan Lease")

    form.vars.tenant = request.vars.tenant
    form.vars.unit = request.vars.unit

    #update field sewa akhir di tabel unit
    #query = (db.unit.id == request.vars.unit)
    #set = db(query)
    #thisdate = form.vars.sewa_akhir.value
    #thisdate = str(thisdate)
    #set.update(sewa_akhir=thisdate)
            
    if form.accepts(request,session):
        response.flash = 'form accepted'
        
        
        
        redirect(URL('unit','index'))
        
    elif form.errors:
        response.flash = 'form has errors'
    else:
        response.flash = 'please fill the form'

    return dict(form=form)
    

@auth.requires_login()
def edit():
    response.title="Edit Lease"
    response.subtitle="Merubah data sewa menyewa"
    
    ids = request.args[0]
    lease= db(db.lease.id==ids)
    if not lease: raise HTTP(404)
    
    return dict(form=crud.update(db.lease,ids))
    
    
@auth.requires_login()
def view():
    response.title="Detail Lease"
    response.subtitle="Melihat detail perjanjian sewa / Lease"
    
    ids = request.args[0]
    lease= db((db.lease.id==ids) & (db.tenant.id==db.lease.tenant) & (db.unit.id==db.lease.unit) & (db.frequency.id == db.lease.frequency)).select()
    if not lease: raise HTTP(404)
    
    
    return dict(lease=lease)


def update_unit():
    now = datetime.datetime.now()
    lease = db((db.lease.sewa_awal < now) & (db.lease.sewa_akhir > now)).select()
    db(db.unit).update(tenant=1,available=True,sewa_akhir=None)
    for l in lease:
        db(db.unit.id==l.unit).update(tenant=l.tenant,available=False,sewa_akhir=l.sewa_akhir)

    redirect(URL('unit','index'))
    return dict(lease=lease)
    
def checkin():
    response.title="Check-In Tenant"
    response.subtitle="Isi Data Tenant, lalu klik 'Tambahkan Tenant', Setelah itu isi data Lease dan klik 'Tambahkan Lease'"
    form=SQLFORM(db.tenant,submit_button="Tambahkan Tenant")

    vars = request.args[0]
    
    if form.process().accepted:
        response.flash = 'Data Tenant sudah dimasukkan'
        redirect(URL('checkin2',args=[vars, form.vars.id]))
        
    return dict(form=form,vars=vars)
    
def checkin2():
    response.title="Check-in Step 2"
    response.subtitle="Isi data Lease"

    form=SQLFORM(db.lease,submit_button="Tambahkan Lease")  
    form.vars.unit=request.args[0]
    form.vars.tenant=request.args[1]

    if form.process().accepted:
        response.flash = 'Data Sewa sudah dimasukkan'
        redirect(URL('update_unit'))
    
    return dict(form=form,vars=vars)
    
def checkout():
    response.title="Checkout this Tenant?"
    response.subtitle="Mengeluarkan pelanggan dari unit kamar sewa"
    response.layout="tenant/view.html"
    
    ids = request.args[0]
    tenant = db((db.tenant.id==ids) & (db.status.id == db.tenant.status)).select()
    if not tenant: raise HTTP(404)
    
    
    lease = db((db.lease.tenant==ids) & (db.frequency.id == db.lease.frequency)).select()
    form=FORM(INPUT(_type='submit'))
    
    if form.validate():
        #merubah menjadi status 4 = Lampau
        form.vars.id = db(db.tenant.id==ids).update(status="4")

        #rubah sewa akhir menjadi hari kemarin?
        today = date.today()
        settodate = date(today.year,today.month,today.day - 1)
        resp = db(db.lease.tenant==ids).update(sewa_akhir=settodate)
        response.flash = "Data sudah disimpan"

        redirect(URL('update_unit'))
        
    return dict(tenant=tenant,lease=lease,form=form,vars=vars)
