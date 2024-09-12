from db import db


class AccessmentModel(db.Model):
    __tablename__ = "accessments"

    id = db.Column(db.Integer, primary_key=True)
    rpt_date = db.Column(db.DateTime)
    code_id = db.Column(db.String)
    broker = db.Column(db.String)
    origin_rpt = db.Column(db.String)
    upOrdown = db.Column(db.String)
    new_rpt = db.Column(db.String)
    old_price = db.Column(db.Float(precision=2))
    new_price = db.Column(db.Float(precision=2))
    now_price = db.Column(db.Float(precision=2))
