from app import db

class Device(db.Model):
    __tablename__ = 'device'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)  # Nuevo campo
    hostname = db.Column(db.String(100), nullable=False)
    model = db.Column(db.String(50), nullable=False)
    brand = db.Column(db.String(50), nullable=False)
    platform = db.Column(db.String(50), nullable=False, default="generic")
    connection_port = db.Column(db.Integer, default=22)
    protocol = db.Column(db.String(10), default='SSH')
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    credentials = db.relationship('DeviceCredentials', backref='device', cascade="all, delete", lazy=True)
    protocols = db.relationship('RoutingProtocol', backref='device', cascade="all, delete", lazy=True)



class DeviceCredentials(db.Model):
    __tablename__ = 'device_credentials'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    username = db.Column(db.String(50), nullable=False)
    password = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

class Interface(db.Model):
    __tablename__ = 'interface'
    id = db.Column(db.Integer, primary_key=True)
    interface_name = db.Column(db.String(50), nullable=False)
    interface_code = db.Column(db.String(50), nullable=False)
    ip_address = db.Column(db.String(50), nullable=False)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)

class RoutingProtocol(db.Model):
    __tablename__ = 'routing_protocol'
    id = db.Column(db.Integer, primary_key=True)
    device_id = db.Column(db.Integer, db.ForeignKey('device.id'), nullable=False)
    protocol = db.Column(db.String(10), nullable=False)  # RIPv2, EIGRP, OSPF, BGP
    config_data = db.Column(db.JSON, nullable=False)  # Almacenar configuración como JSON
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

