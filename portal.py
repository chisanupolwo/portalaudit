from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from datetime import datetime, date
from flask_migrate import Migrate
from xml.dom import minidom
import glob
import os


app = Flask(__name__)
app.config['SECRET_KEY'] = 'Hard to guess string'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:\Portal Audit web\data'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False


db = SQLAlchemy(app)
bootstrap = Bootstrap(app)
Moment = Moment(app)
migrate = Migrate(app, db)


class Shipment(db.Model):
    __tablename__ = 'shipments'
    id = db.Column(db.Integer, primary_key=True)
    shipment_code = db.Column(db.String(32), index=True)
    mode = db.Column(db.String(6), default=None)
    term = db.Column(db.String(6), default=None)
    pol = db.Column(db.String(24), default=None)
    pod = db.Column(db.String(24), default=None)
    etd = db.Column(db.DateTime, default=None)
    eta = db.Column(db.DateTime, default=None)
    atd = db.Column(db.DateTime, default=None)
    ata = db.Column(db.DateTime, default=None)
    localname = db.Column(db.String(64), default=None)
    incoterm = db.Column(db.String(6), default=None)
    package = db.Column(db.String(24), default=None)
    goods = db.Column(db.String(24), default=None)
    weight = db.Column(db.Float, default=0.0)
    volume = db.Column(db.Float, default=0.0)
    bl = db.Column(db.String(64), default=None)
    shipper = db.Column(db.String(64), default=None)
    cnee = db.Column(db.String(64), default=None)
    status = db.Column(db.String(10), default='ACTIVE')
    owner = db.Column(db.String(24), default=None)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    milestone = db.relationship('Milestone', backref='shipment', lazy='dynamic')
    document = db.relationship('Document', backref='shipment', lazy='dynamic')
    comment = db.relationship('Comments', backref='shipment', lazy='dynamic')

class Milestone(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    milestone = db.Column(db.String(12), default=None)
    job = db.Column(db.String(32), index=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'))

class Document(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    document = db.Column(db.String(12), default=None)
    job = db.Column(db.String(32), index=True)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'))

class Comments(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    comment = db.Column(db.String(128))
    owner = db.Column(db.String(24), default=None)
    job = db.Column(db.String(32), index=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)
    shipment_id = db.Column(db.Integer, db.ForeignKey('shipments.id'))


#Web process always running all the time
@app.route('/Webdatastreamingrunning', methods=['GET', 'POST'])
def server():
    files = glob.glob('Z:\XML_FTP\*.xml')
    for each_file in files:
        with open(each_file) as xml:
            doc = minidom.parse(xml)

        shipments = doc.getElementsByTagName('Shipment')
        mode = doc.getElementsByTagName('TransportMode')
        term = doc.getElementsByTagName('ContainerMode')
        actual = doc.getElementsByTagName('Vessel')
        atd = doc.getElementsByTagName('ETD')
        ata = doc.getElementsByTagName('ETA')
        milestones = doc.getElementsByTagName('Milestone')

        for shipment in shipments:
            f = Shipment.query.filter_by(shipment_code=shipment.getElementsByTagName('ShipmentIdentifier')[0].firstChild.data).first()
            if f is None:
                if shipment.getElementsByTagName('ShipmentIdentifier')[0].firstChild is not None:
                    shipment_id = Shipment(shipment_code=shipment.getElementsByTagName('ShipmentIdentifier')[0].firstChild.data)
                    db.session.add(shipment_id)
                    db.session.commit()
                g = Shipment.query.filter_by(shipment_code=shipment.getElementsByTagName('ShipmentIdentifier')[0].firstChild.data).first()
                if g is not None:
                    if mode[0].firstChild is not None:
                        g.mode = mode[0].firstChild.data
                    if term[0].firstChild is not None:
                        g.term = term[0].firstChild.data
                    if shipment.getElementsByTagName('Port')[0].firstChild is not None:
                        g.pol = shipment.getElementsByTagName('Port')[0].firstChild.data
                    if shipment.getElementsByTagName('Port')[1].firstChild is not None:
                        g.pod = shipment.getElementsByTagName('Port')[1].firstChild.data
                    if shipment.getElementsByTagName('EstimatedDateTime')[0].firstChild is not None:
                        g.etd = datetime.strptime(shipment.getElementsByTagName('EstimatedDateTime')[0].firstChild.data, '%Y-%m-%dT%H:%M:%S')
                    if shipment.getElementsByTagName('EstimatedDateTime')[1].firstChild is not None:
                        g.eta = datetime.strptime(shipment.getElementsByTagName('EstimatedDateTime')[1].firstChild.data, '%Y-%m-%dT%H:%M:%S')
                    if atd[0].firstChild is not None:
                        g.atd = datetime.strptime(atd[0].firstChild.data, '%Y-%m-%dT%H:%M:%S')
                    if ata[0].firstChild is not None:
                        g.ata = datetime.strptime(ata[0].firstChild.data, '%Y-%m-%dT%H:%M:%S')
                    if shipment.getElementsByTagName('Name')[0].firstChild is not None:
                        g.localname = shipment.getElementsByTagName('Name')[0].firstChild.data
                    if shipment.getElementsByTagName('Incoterm')[0].firstChild is not None:
                        g.incoterm = shipment.getElementsByTagName('Incoterm')[0].firstChild.data
                    if shipment.getElementsByTagName('NumberOfPacks')[0].firstChild is not None and shipment.getElementsByTagName('PackType')[0].firstChild:
                        g.package = shipment.getElementsByTagName('NumberOfPacks')[0].firstChild.data+shipment.getElementsByTagName('PackType')[0].firstChild.data
                    if shipment.getElementsByTagName('GoodsDescription')[0].firstChild is not None:
                        g.goods = shipment.getElementsByTagName('GoodsDescription')[0].firstChild.data
                    if shipment.getElementsByTagName('Weight')[1].firstChild is not None:
                        g.weight = shipment.getElementsByTagName('Weight')[1].firstChild.data
                    if shipment.getElementsByTagName('Volume')[1].firstChild is not None:
                        g.volume = shipment.getElementsByTagName('Volume')[1].firstChild.data
                    if shipment.getElementsByTagName('ShipmentIdentifier')[1].firstChild is not None:
                        g.bl = shipment.getElementsByTagName('ShipmentIdentifier')[1].firstChild.data
                    if shipment.getElementsByTagName('Name')[2].firstChild is not None:
                        g.shipper = shipment.getElementsByTagName('Name')[2].firstChild.data
                    if shipment.getElementsByTagName('Name')[1].firstChild is not None:
                        g.cnee = shipment.getElementsByTagName('Name')[1].firstChild.data
                    db.session.add(g)
                    db.session.commit()
                    for milestone in shipment.getElementsByTagName('Milestone'):
                        if milestone.getElementsByTagName('EventCode')[0].firstChild is not None:
                            code = milestone.getElementsByTagName('EventCode')[0].firstChild.data
                            codes = Milestone(milestone=code, shipment=shipment_id, job=shipment.getElementsByTagName('ShipmentIdentifier')[0].firstChild.data)
                            db.session.add(codes)
                            db.session.commit()

            else:
                if shipment.getElementsByTagName('ShipmentIdentifier')[0].firstChild is not None:
                    f.shipment_code = shipment.getElementsByTagName('ShipmentIdentifier')[0].firstChild.data
                if mode[0].firstChild is not None:
                    f.mode = mode[0].firstChild.data
                if term[0].firstChild is not None:
                    f.term = term[0].firstChild.data
                if shipment.getElementsByTagName('Port')[0].firstChild is not None:
                    f.pol = shipment.getElementsByTagName('Port')[0].firstChild.data
                if shipment.getElementsByTagName('Port')[1].firstChild is not None:
                    f.pod = shipment.getElementsByTagName('Port')[1].firstChild.data
                if shipment.getElementsByTagName('EstimatedDateTime')[0].firstChild is not None:
                    f.etd = datetime.strptime(shipment.getElementsByTagName('EstimatedDateTime')[0].firstChild.data, '%Y-%m-%dT%H:%M:%S')
                if shipment.getElementsByTagName('EstimatedDateTime')[1].firstChild is not None:
                    f.eta = datetime.strptime(shipment.getElementsByTagName('EstimatedDateTime')[1].firstChild.data, '%Y-%m-%dT%H:%M:%S')
                if atd[0].firstChild is not None:
                    f.atd = datetime.strptime(atd[0].firstChild.data, '%Y-%m-%dT%H:%M:%S')
                if ata[0].firstChild is not None:
                    f.ata = datetime.strptime(ata[0].firstChild.data, '%Y-%m-%dT%H:%M:%S')
                if shipment.getElementsByTagName('Name')[0].firstChild is not None:
                    f.localname = shipment.getElementsByTagName('Name')[0].firstChild.data
                if shipment.getElementsByTagName('Incoterm')[0].firstChild is not None:
                    f.incoterm = shipment.getElementsByTagName('Incoterm')[0].firstChild.data
                if shipment.getElementsByTagName('NumberOfPacks')[0].firstChild is not None and shipment.getElementsByTagName('PackType')[0].firstChild:
                    f.package = shipment.getElementsByTagName('NumberOfPacks')[0].firstChild.data+shipment.getElementsByTagName('PackType')[0].firstChild.data
                if shipment.getElementsByTagName('GoodsDescription')[0].firstChild is not None:
                    f.goods = shipment.getElementsByTagName('GoodsDescription')[0].firstChild.data
                if shipment.getElementsByTagName('Weight')[1].firstChild is not None:
                    f.weight = shipment.getElementsByTagName('Weight')[1].firstChild.data
                if shipment.getElementsByTagName('Volume')[1].firstChild is not None:
                    f.volume = shipment.getElementsByTagName('Volume')[1].firstChild.data
                if shipment.getElementsByTagName('ShipmentIdentifier')[1].firstChild is not None:
                    f.bl = shipment.getElementsByTagName('ShipmentIdentifier')[1].firstChild.data
                if shipment.getElementsByTagName('Name')[2].firstChild is not None:
                    f.shipper = shipment.getElementsByTagName('Name')[2].firstChild.data
                if shipment.getElementsByTagName('Name')[1].firstChild is not None:
                    f.cnee = shipment.getElementsByTagName('Name')[1].firstChild.data
                db.session.add(f)
                db.session.commit()
                #Change Milestone
                db.session.query(Milestone).filter(Milestone.job==shipment.getElementsByTagName('ShipmentIdentifier')[0].firstChild.data).delete()
                db.session.commit()
                for milestone in shipment.getElementsByTagName('Milestone'):
                    if milestone.getElementsByTagName('EventCode')[0].firstChild is not None:
                        code = milestone.getElementsByTagName('EventCode')[0].firstChild.data
                        codes = Milestone(milestone=code, shipment=f, job=shipment.getElementsByTagName('ShipmentIdentifier')[0].firstChild.data)
                        db.session.add(codes)
                        db.session.commit()
    shipments = Shipment.query.all()
    all_shipments = len(shipments)
    return render_template('server.html', all_shipments=all_shipments)


#User index
@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.order_by(Shipment.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    return render_template('index.html', shipments=shipments, pagination=pagination)


#User shipment
@app.route('/<shipment_id>', methods=['GET', 'POST'])
def shipment(shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    if request.method == 'POST':
        documents = request.form.getlist('document_name')
        upload_doc = Document.query.filter_by(job=shipment_id).first()
        if upload_doc is None:
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
        else:
            del_doc = Document.query.filter_by(job=shipment_id).delete()
            db.session.commit()
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
    documents = Document.query.filter_by(job=shipment_id).all()
    milestones = Milestone.query.filter_by(job=shipment_id).all()
    comments = Comments.query.filter_by(job=shipment_id).order_by(Comments.timestamp.asc()).all()
    return render_template('shipment.html', shipment=shipment, milestones=milestones, documents=documents, comments=comments)


#User search
@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        shipment_seek = request.form['shipment_id']
        shipments = Shipment.query.filter_by(shipment_code=shipment_seek).all()
        if shipments is not None:
            return render_template('results.html', shipments=shipments)


#User filter by type
@app.route('/filterbytype/<shipment_abbs>')
def filterbytype(shipment_abbs):
    ship_iden = shipment_abbs
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.filter(Shipment.shipment_code.startswith(shipment_abbs)).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    return render_template('filterby_type.html', shipments=shipments, pagination=pagination, ship_iden=ship_iden)


#User shipment after filter
@app.route('/filterbytype/<shipment_abbs>/<shipment_id>', methods=['GET', 'POST'])
def shipmentbytype(shipment_abbs, shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    if request.method == 'POST':
        documents = request.form.getlist('document_name')
        upload_doc = Document.query.filter_by(job=shipment_id).first()
        if upload_doc is None:
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
        else:
            del_doc = Document.query.filter_by(job=shipment_id).delete()
            db.session.commit()
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
    documents = Document.query.filter_by(job=shipment_id).all()
    milestones = Milestone.query.filter_by(job=shipment_id).all()
    return render_template('shipment.html', shipment=shipment, milestones=milestones, documents=documents)


#User filter by name
@app.route('/filterbyname/<owner_name>')
def filterbyname(owner_name):
    owner_iden = owner_name
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.filter_by(owner=owner_name).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    return render_template('filterby_name.html', shipments=shipments, pagination=pagination, owner_iden=owner_iden)


#User filter by status
@app.route('/filterbystatus/<owner>/<status>')
def filterbystatus(owner, status):
    owner_iden = owner
    status_now = status
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.filter_by(owner=owner).filter_by(status=status).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    return render_template('filterby_status.html', shipments=shipments, pagination=pagination, owner_iden=owner_iden, status_now=status_now)


#User shipment after filter
@app.route('/filterbyname/<owner_name>/<shipment_id>', methods=['GET', 'POST'])
def shipmentbyname(owner_name, shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    if request.method == 'POST':
        documents = request.form.getlist('document_name')
        upload_doc = Document.query.filter_by(job=shipment_id).first()
        if upload_doc is None:
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
        else:
            del_doc = Document.query.filter_by(job=shipment_id).delete()
            db.session.commit()
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
    documents = Document.query.filter_by(job=shipment_id).all()
    milestones = Milestone.query.filter_by(job=shipment_id).all()
    comments = Comments.query.filter_by(job=shipment_id).order_by(Comments.timestamp.asc()).all()
    return render_template('filter_shipment.html', shipment=shipment, milestones=milestones, documents=documents, comments=comments)


#User comment
@app.route('/comment/<shipment_id>', methods=['GET', 'POST'])
def comment(shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    if request.method == 'POST':
        comment = request.form['Comment']
        owner = request.form['Owner']
        if comment != '':
            create_comment = Comments(comment=comment, owner=owner, job=shipment_id, shipment=shipment)
            db.session.add(create_comment)
            db.session.commit()
    return redirect(url_for('.shipment', shipment_id=shipment_id))


#User success
@app.route('/approve/<shipment_id>', methods=['GET', 'POST'])
def success(shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    shipment.status = 'APPROVING'
    db.session.add(shipment)
    db.session.commit()
    if request.method == 'POST':
        comment = request.form['Comment']
        owner = request.form['Owner']
        if comment != '':
            create_comment = Comments(comment=comment, owner=owner, job=shipment_id, shipment=shipment)
            db.session.add(create_comment)
            db.session.commit()
    return redirect(url_for('.shipment', shipment_id=shipment_id))

#User unsuccess
@app.route('/unsuccess/<shipment_id>')
def unsuccess(shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    shipment.status = 'ACTIVE'
    db.session.add(shipment)
    db.session.commit()
    return redirect(url_for('.shipment', shipment_id=shipment_id))


#User delete comment
@app.route('/delete/<shipment_id>/comment/<int:id>')
def del_comment(shipment_id, id):
    comment = Comments.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('.shipment', shipment_id=shipment_id))


#Admin Index
@app.route('/admin')
def admin():
    no_name = Shipment.query.filter_by(owner=None).all()
    no_names = len(no_name)
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.order_by(Shipment.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    return render_template('admin.html', shipments=shipments, pagination=pagination, no_names=no_names)


#Admin shipment
@app.route('/admin/<shipment_id>', methods=['GET', 'POST'])
def admin_shipment(shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    if request.method == 'POST':
        documents = request.form.getlist('document_name')
        upload_doc = Document.query.filter_by(job=shipment_id).first()
        if upload_doc is None:
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
        else:
            del_doc = Document.query.filter_by(job=shipment_id).delete()
            db.session.commit()
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
    documents = Document.query.filter_by(job=shipment_id).all()
    milestones = Milestone.query.filter_by(job=shipment_id).all()
    comments = Comments.query.filter_by(job=shipment_id).order_by(Comments.timestamp.asc()).all()
    return render_template('admin_shipment.html', shipment=shipment, milestones=milestones, documents=documents, comments=comments)


#Admin Search
@app.route('/admin/search', methods=['GET', 'POST'])
def admin_search():
    no_name = Shipment.query.filter_by(owner=None).all()
    no_names = len(no_name)
    if request.method == 'POST':
        shipment_seek = request.form['shipment_id']
        shipments = Shipment.query.filter_by(shipment_code=shipment_seek).all()
        if shipments is not None:
            return render_template('admin_results.html', shipments=shipments, no_names=no_names)


#Admin Assigname
@app.route('/admin/assignname/<shipment_code>', methods=['GET', 'POST'])
def assignname(shipment_code):
    if request.method == 'POST':
        owner = request.form['owner']
        shipment = Shipment.query.filter_by(shipment_code=shipment_code).first()
        shipment.owner = owner
        db.session.add(shipment)
        db.session.commit()
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.order_by(Shipment.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    no_name = Shipment.query.filter_by(owner=None).all()
    no_names = len(no_name)
    return redirect(url_for('.admin_noname', shipments=shipments, pagination=pagination, no_names=no_names))


#Admin delete name
@app.route('/admin/delname/<shipment_code>', methods=['GET', 'POST'])
def delname(shipment_code):
    shipment = Shipment.query.filter_by(shipment_code=shipment_code).first()
    shipment.owner = None
    db.session.add(shipment)
    db.session.commit()
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.filter_by(shipment_code=shipment_code).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    return render_template('admin_results.html', shipments=shipments, pagination=pagination)


#Admin filter by type
@app.route('/admin/filterbytype/<shipment_abbs>')
def admin_filterbytype(shipment_abbs):
    ship_iden = shipment_abbs
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.filter(Shipment.shipment_code.startswith(shipment_abbs)).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    return render_template('admin_filterby_type.html', shipments=shipments, pagination=pagination, ship_iden=ship_iden)


#Admin shipment after filter
@app.route('/admin/filterbytype/<shipment_abbs>/<shipment_id>')
def admin_shipmentbytype(shipment_abbs, shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    if request.method == 'POST':
        documents = request.form.getlist('document_name')
        upload_doc = Document.query.filter_by(job=shipment_id).first()
        if upload_doc is None:
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
        else:
            del_doc = Document.query.filter_by(job=shipment_id).delete()
            db.session.commit()
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
    documents = Document.query.filter_by(job=shipment_id).all()
    milestones = Milestone.query.filter_by(job=shipment_id).all()
    comments = Comments.query.filter_by(job=shipment_id).order_by(Comments.timestamp.asc()).all()
    return render_template('admin_shipment.html', shipment=shipment, milestones=milestones, documents=documents, comments=comments)


#Admin filter by name
@app.route('/admin/filterbyname/<owner_name>')
def admin_filterbyname(owner_name):
    owner_iden = owner_name
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.filter_by(owner=owner_name).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    return render_template('admin_filterby_name.html', shipments=shipments, pagination=pagination, owner_iden=owner_iden)


#Admind filter by status
@app.route('/admin/filterbystatus/<owner>/<status>')
def admin_filterbystatus(owner, status):
    owner_iden = owner
    status_now = status
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.filter_by(owner=owner).filter_by(status=status).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    return render_template('admin_filterby_nameandstatus.html', shipments=shipments, pagination=pagination, owner_iden=owner_iden, status_now=status_now)


#Admin shipment after filter
@app.route('/admin/filterbyname/<owner_name>/<shipment_id>')
def admin_shipmentbyname(owner_name, shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    if request.method == 'POST':
        documents = request.form.getlist('document_name')
        upload_doc = Document.query.filter_by(job=shipment_id).first()
        if upload_doc is None:
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
        else:
            del_doc = Document.query.filter_by(job=shipment_id).delete()
            db.session.commit()
            for doc in documents:
                document = Document(document=doc, job=shipment_id, shipment=shipment)
                db.session.add(document)
                db.session.commit()
    documents = Document.query.filter_by(job=shipment_id).all()
    milestones = Milestone.query.filter_by(job=shipment_id).all()
    comments = Comments.query.filter_by(job=shipment_id).order_by(Comments.timestamp.asc()).all()
    return render_template('admin_filter_shipment.html', shipment=shipment, milestones=milestones, documents=documents, comments=comments)


#Admin success
@app.route('/admin/success/<shipment_id>')
def admin_success(shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    shipment.status = 'SUCCESS'
    db.session.add(shipment)
    db.session.commit()
    return redirect(url_for('.admin_shipment', shipment_id=shipment_id))


#Admin unsucess
@app.route('/admin/unsuccess/<shipment_id>')
def admin_unsuccess(shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    shipment.status = 'ACTIVE'
    db.session.add(shipment)
    db.session.commit()
    return redirect(url_for('.admin_shipment', shipment_id=shipment_id))


#Admin reject
@app.route('/admin/reject/<shipment_id>', methods=['GET', 'POST'])
def admin_reject(shipment_id):
    shipment = Shipment.query.filter_by(shipment_code=shipment_id).first()
    shipment.status = 'REJECT'
    db.session.add(shipment)
    db.session.commit()
    if request.method == 'POST':
        comment = request.form['Comment']
        owner = request.form['Owner']
        if comment != '':
            create_comment = Comments(comment=comment, owner=owner, job=shipment_id, shipment=shipment)
            db.session.add(create_comment)
            db.session.commit()
    return redirect(url_for('.admin_shipment', shipment_id=shipment_id))


#Admin delete comment
@app.route('/admin/delete/<shipment_id>/comment/<int:id>')
def admin_del_comment(shipment_id, id):
    comment = Comments.query.get_or_404(id)
    db.session.delete(comment)
    db.session.commit()
    return redirect(url_for('.admin_shipment', shipment_id=shipment_id))


#Admin status
@app.route('/admin/status/<status>')
def admin_status(status):
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.filter_by(status=status).order_by(Shipment.timestamp.desc()).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    status_now = status
    return render_template('admin_filterby_status.html', shipments=shipments, pagination=pagination, status_now=status_now)


#Admin No name
@app.route('/admin/noname')
def admin_noname():
    page = request.args.get('page', 1, type=int)
    pagination = Shipment.query.filter_by(owner=None).order_by(Shipment.timestamp.asc()).paginate(page, per_page=10, error_out=False)
    shipments = pagination.items
    return render_template('admin_noname.html', shipments=shipments, pagination=pagination)


#Admin Summary
@app.route('/admin/summary/all')
def admin_summary():
    shipments = Shipment.query.all()
    all_shipments = len(shipments)
    active = Shipment.query.filter_by(status='ACTIVE').all()
    actives = len(active)
    reject = Shipment.query.filter_by(status='REJECT').all()
    rejects = len(reject)
    success = Shipment.query.filter_by(status='SUCCESS').all()
    successes = len(success)
    per_success = float((successes/all_shipments)*100)
    per_actives = float((actives/all_shipments)*100)
    return render_template('admin_summary.html', all_shipments=all_shipments, actives=actives, rejects=rejects, successes=successes,
                                                per_success=per_success, per_actives=per_actives)


#Admin Summary Progress
@app.route('/admin/summary/progress')
def admin_progress():
    shipments = Shipment.query.all()
    active = Shipment.query.filter_by(status='ACTIVE').all()
    success = Shipment.query.filter_by(status='SUCCESS').all()
    per_success = float((len(success)/len(shipments))*100)
    per_actives = float((len(active)/len(shipments))*100)
    ONJIRA = Shipment.query.filter_by(owner='ONJIRA').all()
    ONJIRA_A = Shipment.query.filter_by(owner='ONJIRA').filter_by(status='ACTIVE').all()
    ONJIRA_S = Shipment.query.filter_by(owner='ONJIRA').filter_by(status='SUCCESS').all()
    ONJIRA_R = Shipment.query.filter_by(owner='ONJIRA').filter_by(status='REJECT').all()
    A_ONJIRA = float((len(ONJIRA_A+ONJIRA_R)/len(ONJIRA))*100)
    S_ONJIRA = float((len(ONJIRA_S)/len(ONJIRA))*100)
    BUSARAKAM = Shipment.query.filter_by(owner='BUSARAKAM').all()
    BUSARAKAM_A = Shipment.query.filter_by(owner='BUSARAKAM').filter_by(status='ACTIVE').all()
    BUSARAKAM_S = Shipment.query.filter_by(owner='BUSARAKAM').filter_by(status='SUCCESS').all()
    BUSARAKAM_R = Shipment.query.filter_by(owner='BUSARAKAM').filter_by(status='REJECT').all()
    CHONTICHA = Shipment.query.filter_by(owner='CHONTICHA').all()
    CHONTICHA_A = Shipment.query.filter_by(owner='CHONTICHA').filter_by(status='ACTIVE').all()
    CHONTICHA_S = Shipment.query.filter_by(owner='CHONTICHA').filter_by(status='SUCCESS').all()
    CHONTICHA_R = Shipment.query.filter_by(owner='CHONTICHA').filter_by(status='REJECT').all()
    KITINUDDA = Shipment.query.filter_by(owner='KITINUDDA').all()
    KITINUDDA_A = Shipment.query.filter_by(owner='KITINUDDA').filter_by(status='ACTIVE').all()
    KITINUDDA_S = Shipment.query.filter_by(owner='KITINUDDA').filter_by(status='SUCCESS').all()
    KITINUDDA_R = Shipment.query.filter_by(owner='KITINUDDA').filter_by(status='REJECT').all()
    TASANAPORN = Shipment.query.filter_by(owner='TASANAPORN').all()
    TASANAPORN_A = Shipment.query.filter_by(owner='TASANAPORN').filter_by(status='ACTIVE').all()
    TASANAPORN_S = Shipment.query.filter_by(owner='TASANAPORN').filter_by(status='SUCCESS').all()
    TASANAPORN_R = Shipment.query.filter_by(owner='TASANAPORN').filter_by(status='REJECT').all()
    A_BUSARAKAM = float((len(BUSARAKAM_A+BUSARAKAM_R)/len(BUSARAKAM))*100)
    S_BUSARAKAM = float((len(BUSARAKAM_S)/len(BUSARAKAM))*100)
    A_CHONTICHA = float((len(CHONTICHA_A+CHONTICHA_R)/len(CHONTICHA))*100)
    S_CHONTICHA = float((len(CHONTICHA_S)/len(CHONTICHA))*100)
    A_KITINUDDA = float((len(KITINUDDA_A+KITINUDDA_R)/len(KITINUDDA))*100)
    S_KITINUDDA = float((len(KITINUDDA_S)/len(KITINUDDA))*100)
    A_TASANAPORN = float((len(TASANAPORN_A+TASANAPORN_R)/len(TASANAPORN))*100)
    S_TASANAPORN = float((len(TASANAPORN_S)/len(TASANAPORN))*100)
    ALL_A_SEAIM = float((A_BUSARAKAM+A_CHONTICHA+A_KITINUDDA+A_TASANAPORN)/4)
    ALL_S_SEAIM = float((S_BUSARAKAM+S_CHONTICHA+S_KITINUDDA+S_TASANAPORN)/4)
    ROJJANA = Shipment.query.filter_by(owner='ROJJANA').all()
    ROJJANA_A = Shipment.query.filter_by(owner='ROJJANA').filter_by(status='ACTIVE').all()
    ROJJANA_S = Shipment.query.filter_by(owner='ROJJANA').filter_by(status='SUCCESS').all()
    ROJJANA_R = Shipment.query.filter_by(owner='ROJJANA').filter_by(status='REJECT').all()
    A_ROJJANA = float((len(ROJJANA_A+ROJJANA_R)/len(ROJJANA))*100)
    S_ROJJANA = float((len(ROJJANA_S)/len(ROJJANA))*100)
    CHIRARAT = Shipment.query.filter_by(owner='CHIRARAT').all()
    CHIRARAT_A = Shipment.query.filter_by(owner='CHIRARAT').filter_by(status='ACTIVE').all()
    CHIRARAT_S = Shipment.query.filter_by(owner='CHIRARAT').filter_by(status='SUCCESS').all()
    CHIRARAT_R = Shipment.query.filter_by(owner='CHIRARAT').filter_by(status='REJECT').all()
    SUREEWAN = Shipment.query.filter_by(owner='SUREEWAN').all()
    SUREEWAN_A = Shipment.query.filter_by(owner='SUREEWAN').filter_by(status='ACTIVE').all()
    SUREEWAN_S = Shipment.query.filter_by(owner='SUREEWAN').filter_by(status='SUCCESS').all()
    SUREEWAN_R = Shipment.query.filter_by(owner='SUREEWAN').filter_by(status='REJECT').all()
    A_CHIRARAT = float((len(CHIRARAT_A+CHIRARAT_R)/len(CHIRARAT))*100)
    S_CHIRARAT = float((len(CHIRARAT_S)/len(CHIRARAT))*100)
    A_SUREEWAN = float((len(SUREEWAN_A+SUREEWAN_R)/len(SUREEWAN))*100)
    S_SUREEWAN = float((len(SUREEWAN_S)/len(SUREEWAN))*100)
    ALL_A_SEACON = float((A_CHIRARAT+A_SUREEWAN)/2)
    ALL_S_SEACON = float((S_CHIRARAT+S_SUREEWAN)/2)
    AREEYA = Shipment.query.filter_by(owner='AREEYA').all()
    AREEYA_A = Shipment.query.filter_by(owner='AREEYA').filter_by(status='ACTIVE').all()
    AREEYA_S = Shipment.query.filter_by(owner='AREEYA').filter_by(status='SUCCESS').all()
    AREEYA_R = Shipment.query.filter_by(owner='AREEYA').filter_by(status='REJECT').all()
    ATCHARA = Shipment.query.filter_by(owner='ATCHARA').all()
    ATCHARA_A = Shipment.query.filter_by(owner='ATCHARA').filter_by(status='ACTIVE').all()
    ATCHARA_S = Shipment.query.filter_by(owner='ATCHARA').filter_by(status='SUCCESS').all()
    ATCHARA_R = Shipment.query.filter_by(owner='ATCHARA').filter_by(status='REJECT').all()
    NANTANUCH = Shipment.query.filter_by(owner='NANTANUCH').all()
    NANTANUCH_A = Shipment.query.filter_by(owner='NANTANUCH').filter_by(status='ACTIVE').all()
    NANTANUCH_S = Shipment.query.filter_by(owner='NANTANUCH').filter_by(status='SUCCESS').all()
    NANTANUCH_R = Shipment.query.filter_by(owner='NANTANUCH').filter_by(status='REJECT').all()
    DUANGPORN = Shipment.query.filter_by(owner='DUANGPORN').all()
    DUANGPORN_A = Shipment.query.filter_by(owner='DUANGPORN').filter_by(status='ACTIVE').all()
    DUANGPORN_S = Shipment.query.filter_by(owner='DUANGPORN').filter_by(status='SUCCESS').all()
    DUANGPORN_R = Shipment.query.filter_by(owner='DUANGPORN').filter_by(status='REJECT').all()
    WACHIRAPORN = Shipment.query.filter_by(owner='WACHIRAPORN').all()
    WACHIRAPORN_A = Shipment.query.filter_by(owner='WACHIRAPORN').filter_by(status='ACTIVE').all()
    WACHIRAPORN_S = Shipment.query.filter_by(owner='WACHIRAPORN').filter_by(status='SUCCESS').all()
    WACHIRAPORN_R = Shipment.query.filter_by(owner='WACHIRAPORN').filter_by(status='REJECT').all()
    A_AREEYA = float((len(AREEYA_A+AREEYA_R)/len(AREEYA))*100)
    S_AREEYA = float((len(AREEYA_S)/len(AREEYA))*100)
    A_ATCHARA = float((len(ATCHARA_A+ATCHARA_R)/len(ATCHARA))*100)
    S_ATCHARA = float((len(ATCHARA_S)/len(ATCHARA))*100)
    A_NANTANUCH = float((len(NANTANUCH_A+NANTANUCH_R)/len(NANTANUCH))*100)
    S_NANTANUCH = float((len(NANTANUCH_S)/len(NANTANUCH))*100)
    A_DUANGPORN = float((len(DUANGPORN_A+DUANGPORN_R)/len(DUANGPORN))*100)
    S_DUANGPORN = float((len(DUANGPORN_S)/len(DUANGPORN))*100)
    A_WACHIRAPORN = float((len(WACHIRAPORN_A+WACHIRAPORN_R)/len(WACHIRAPORN))*100)
    S_WACHIRAPORN = float((len(WACHIRAPORN_S)/len(WACHIRAPORN))*100)
    ALL_A_SEAKEYACC = float((A_AREEYA+A_ATCHARA+A_NANTANUCH+A_DUANGPORN+A_WACHIRAPORN)/5)
    ALL_S_SEAKEYACC = float((S_AREEYA+S_ATCHARA+S_NANTANUCH+S_DUANGPORN+A_WACHIRAPORN)/5)
    PRONPARPA = Shipment.query.filter_by(owner='PRONPARPA').all()
    PRONPARPA_A = Shipment.query.filter_by(owner='PRONPARPA').filter_by(status='ACTIVE').all()
    PRONPARPA_S = Shipment.query.filter_by(owner='PRONPARPA').filter_by(status='SUCCESS').all()
    PRONPARPA_R = Shipment.query.filter_by(owner='PRONPARPA').filter_by(status='REJECT').all()
    A_PRONPARPA = float((len(PRONPARPA_A+PRONPARPA_R)/len(PRONPARPA))*100)
    S_PRONPARPA = float((len(PRONPARPA_S)/len(PRONPARPA))*100)
    FRAME = Shipment.query.filter_by(owner='FRAME').all()
    FRAME_A = Shipment.query.filter_by(owner='FRAME').filter_by(status='ACTIVE').all()
    FRAME_S = Shipment.query.filter_by(owner='FRAME').filter_by(status='SUCCESS').all()
    FRAME_R = Shipment.query.filter_by(owner='FRAME').filter_by(status='REJECT').all()
    KEMJIRA = Shipment.query.filter_by(owner='KEMJIRA').all()
    KEMJIRA_A = Shipment.query.filter_by(owner='KEMJIRA').filter_by(status='ACTIVE').all()
    KEMJIRA_S = Shipment.query.filter_by(owner='KEMJIRA').filter_by(status='SUCCESS').all()
    KEMJIRA_R = Shipment.query.filter_by(owner='KEMJIRA').filter_by(status='REJECT').all()
    MANEERAT = Shipment.query.filter_by(owner='MANEERAT').all()
    MANEERAT_A = Shipment.query.filter_by(owner='MANEERAT').filter_by(status='ACTIVE').all()
    MANEERAT_S = Shipment.query.filter_by(owner='MANEERAT').filter_by(status='SUCCESS').all()
    MANEERAT_R = Shipment.query.filter_by(owner='MANEERAT').filter_by(status='REJECT').all()
    NOPPARAT = Shipment.query.filter_by(owner='NOPPARAT').all()
    NOPPARAT_A = Shipment.query.filter_by(owner='NOPPARAT').filter_by(status='ACTIVE').all()
    NOPPARAT_S = Shipment.query.filter_by(owner='NOPPARAT').filter_by(status='SUCCESS').all()
    NOPPARAT_R = Shipment.query.filter_by(owner='NOPPARAT').filter_by(status='REJECT').all()
    A_FRAME = float((len(FRAME_A+FRAME_R)/len(FRAME))*100)
    S_FRAME = float((len(FRAME_S)/len(FRAME))*100)
    A_KEMJIRA = float((len(KEMJIRA_A+KEMJIRA_R)/len(KEMJIRA))*100)
    S_KEMJIRA = float((len(KEMJIRA_S)/len(KEMJIRA))*100)
    A_MANEERAT = float((len(MANEERAT_A+MANEERAT_R)/len(MANEERAT))*100)
    S_MANEERAT = float((len(MANEERAT_S)/len(MANEERAT))*100)
    A_NOPPARAT = float((len(NOPPARAT_A+NOPPARAT_R)/len(NOPPARAT))*100)
    S_NOPPARAT = float((len(NOPPARAT_S)/len(NOPPARAT))*100)
    ALL_A_SEACSR1 = float((A_FRAME+A_KEMJIRA+A_MANEERAT+A_NOPPARAT)/4)
    ALL_S_SEACSR1 = float((S_FRAME+S_KEMJIRA+S_MANEERAT+S_NOPPARAT)/4)
    PONGSATHON = Shipment.query.filter_by(owner='PONGSATHON').all()
    PONGSATHON_A = Shipment.query.filter_by(owner='PONGSATHON').filter_by(status='ACTIVE').all()
    PONGSATHON_S = Shipment.query.filter_by(owner='PONGSATHON').filter_by(status='SUCCESS').all()
    PONGSATHON_R = Shipment.query.filter_by(owner='PONGSATHON').filter_by(status='REJECT').all()
    WARARAT = Shipment.query.filter_by(owner='WARARAT').all()
    WARARAT_A = Shipment.query.filter_by(owner='WARARAT').filter_by(status='ACTIVE').all()
    WARARAT_S = Shipment.query.filter_by(owner='WARARAT').filter_by(status='SUCCESS').all()
    WARARAT_R = Shipment.query.filter_by(owner='WARARAT').filter_by(status='REJECT').all()
    A_PONGSATHON = float((len(PONGSATHON_A+PONGSATHON_R)/len(PONGSATHON))*100)
    S_PONGSATHON = float((len(PONGSATHON_S)/len(PONGSATHON))*100)
    A_WARARAT = float((len(WARARAT_A+WARARAT_R)/len(WARARAT))*100)
    S_WARARAT = float((len(WARARAT_S)/len(WARARAT))*100)
    ALL_A_SEACSR4 = float((A_PONGSATHON+A_WARARAT)/2)
    ALL_S_SEACSR4 = float((S_PONGSATHON+S_WARARAT)/2)
    return render_template('admin_progress.html', per_success=per_success, per_actives=per_actives, 
                            #Air team
                            A_ONJIRA=A_ONJIRA, S_ONJIRA=S_ONJIRA,
                            #Sea import
                            ALL_A_SEAIM=ALL_A_SEAIM, ALL_S_SEAIM=ALL_S_SEAIM, A_BUSARAKAM=A_BUSARAKAM, S_BUSARAKAM=S_BUSARAKAM, A_CHONTICHA=A_CHONTICHA, 
                            S_CHONTICHA=S_CHONTICHA, A_KITINUDDA=A_KITINUDDA, S_KITINUDDA=S_KITINUDDA, A_TASANAPORN=A_TASANAPORN, S_TASANAPORN=S_TASANAPORN,
                            #Sea Export
                            A_ROJJANA=A_ROJJANA, S_ROJJANA=S_ROJJANA,
                            #Consol
                            ALL_A_SEACON=ALL_A_SEACON, ALL_S_SEACON=ALL_S_SEACON, A_CHIRARAT=A_CHIRARAT, S_CHIRARAT=S_CHIRARAT, 
                            A_SUREEWAN=A_SUREEWAN, S_SUREEWAN=S_SUREEWAN,
                            #Key Account
                            ALL_A_SEAKEYACC=ALL_A_SEAKEYACC, ALL_S_SEAKEYACC=ALL_S_SEAKEYACC, A_AREEYA=A_AREEYA, S_AREEYA=S_AREEYA,
                            A_ATCHARA=A_ATCHARA, S_ATCHARA=S_ATCHARA, A_NANTANUCH=A_NANTANUCH, S_NANTANUCH=S_NANTANUCH, A_DUANGPORN=A_DUANGPORN, S_DUANGPORN=S_DUANGPORN,
                            A_WACHIRAPORN=A_WACHIRAPORN, S_WACHIRAPORN=S_WACHIRAPORN,
                            #Key Agent
                            A_PRONPARPA=A_PRONPARPA, S_PRONPARPA=S_PRONPARPA,
                            #CSR1
                            ALL_A_SEACSR1=ALL_A_SEACSR1, ALL_S_SEACSR1=ALL_S_SEACSR1, A_FRAME=A_FRAME, S_FRAME=S_FRAME, 
                            A_KEMJIRA=A_KEMJIRA, S_KEMJIRA=S_KEMJIRA, A_MANEERAT=A_MANEERAT, S_MANEERAT=S_MANEERAT,
                            A_NOPPARAT=A_NOPPARAT, S_NOPPARAT=S_NOPPARAT,
                            #CSR4
                            ALL_A_SEACSR4=ALL_A_SEACSR4, ALL_S_SEACSR4=ALL_S_SEACSR4, A_PONGSATHON=A_PONGSATHON, S_PONGSATHON=S_PONGSATHON,
                            A_WARARAT=A_WARARAT, S_WARARAT=S_WARARAT)


#Customer Data
@app.route('/customer')
def customer():
    return render_template('customer_index.html')


#Customer Search
@app.route('/customer/search', methods=['GET', 'POST'])
def customer_search():
    if request.method == 'POST':
        customer_name = request.form['customer_name']
    data_may = Shipment.query.filter_by(localname=customer_name).filter(Shipment.timestamp >= datetime(year=2020, month=5, day=1)).filter(Shipment.timestamp <= datetime(year=2020, month=5, day=31)).all()
    data_may_s = Shipment.query.filter_by(localname=customer_name).filter(Shipment.timestamp >= datetime(year=2020, month=5, day=1)).filter(Shipment.timestamp <= datetime(year=2020, month=5, day=31)).filter_by(status='SUCCESS').all()
    data_may_a = Shipment.query.filter_by(localname=customer_name).filter(Shipment.timestamp >= datetime(year=2020, month=5, day=1)).filter(Shipment.timestamp <= datetime(year=2020, month=5, day=31)).filter_by(status='ACTIVE').all()
    if len(data_may) != 0:
        s_may = float((len(data_may_s)/len(data_may))*100)
        a_may = float((len(data_may_a)/len(data_may))*100)
    else:
        s_may = 0
        a_may = 0
    data_june = Shipment.query.filter_by(localname=customer_name).filter(Shipment.timestamp >= datetime(year=2020, month=6, day=1)).filter(Shipment.timestamp <= datetime(year=2020, month=6, day=30)).all()
    data_june_s = Shipment.query.filter_by(localname=customer_name).filter(Shipment.timestamp >= datetime(year=2020, month=6, day=1)).filter(Shipment.timestamp <= datetime(year=2020, month=6, day=30)).filter_by(status='SUCCESS').all()
    data_june_a = Shipment.query.filter_by(localname=customer_name).filter(Shipment.timestamp >= datetime(year=2020, month=6, day=1)).filter(Shipment.timestamp <= datetime(year=2020, month=6, day=30)).filter_by(status='ACTIVE').all()
    if len(data_june) != 0:
        s_june = float((len(data_june_s)/len(data_june))*100)
        a_june = float((len(data_june_a)/len(data_june))*100)
    else:
        s_june = 0
        a_june = 0
    if len(data_may) != 0 and len(data_june) != 0:
        all_data_s = float((400+s_may+s_june)/6)
        all_data_a = float((a_may+a_june)/6)
    elif len(data_may) != 0:
        all_data_s = float((400+s_may)/5)
        all_data_a = float((a_may)/5)
    else:
        all_data_s = 100.00
        all_data_a = 0.00
    return render_template('customer_data.html', customer_name=customer_name, all_data_s=all_data_s, all_data_a=all_data_a,
                                                    data_may=len(data_may), s_may=s_may, a_may=a_may,
                                                    data_june=len(data_june), s_june=s_june, a_june=a_june)

if __name__ == '__main__':
    app(run)