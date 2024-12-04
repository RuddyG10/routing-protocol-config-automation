from flask import render_template, request, redirect, url_for, flash
from app import app, db
from app.models import Device, DeviceCredentials, Interface, RoutingProtocol
import yaml
from nornir import InitNornir
from scripts.nornir_tasks import assign_protocol
from pprint import pprint


@app.route('/')
def index():
    devices = Device.query.all()
    return render_template('device_list.html', devices=devices)

@app.route('/add_device', methods=['GET', 'POST'])
def add_device():
    if request.method == 'POST':
        name = request.form['name']
        hostname = request.form['hostname']
        model = request.form['model']
        brand = request.form['brand']
        platform = request.form.get('platform', 'generic')
        connection_port = request.form.get('connection_port', 22)
        protocol = request.form.get('protocol', 'SSH')

        new_device = Device(
            name=name,
            hostname=hostname,
            model=model,
            brand=brand,
            platform=platform,
            connection_port=connection_port,
            protocol=protocol
        )
        db.session.add(new_device)
        db.session.commit()
        flash("Device added successfully!", "success")
        return redirect(url_for('index'))
    return render_template('add_device.html')



@app.route('/edit_device/<int:device_id>', methods=['GET', 'POST'])
def edit_device(device_id):
    device = Device.query.get_or_404(device_id)
    if request.method == 'POST':
        device.name = request.form['name']
        device.hostname = request.form['hostname']
        device.model = request.form['model']
        device.brand = request.form['brand']
        device.platform = request.form['platform']
        device.connection_port = request.form.get('connection_port', 22)
        device.protocol = request.form.get('protocol', 'SSH')
        db.session.commit()
        flash("Device updated successfully!", "success")
        return redirect(url_for('index'))
    return render_template('edit_device.html', device=device)



@app.route('/delete_device/<int:device_id>', methods=['POST'])
def delete_device(device_id):
    device = Device.query.get_or_404(device_id)
    db.session.delete(device)
    db.session.commit()
    flash("Device deleted successfully!", "success")
    return redirect(url_for('index'))

@app.route('/assign_credentials/<int:device_id>', methods=['GET', 'POST'])
def assign_credentials(device_id):
    device = Device.query.get_or_404(device_id)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Verificar si ya existen credenciales para el dispositivo
        existing_credentials = DeviceCredentials.query.filter_by(device_id=device_id).first()
        if existing_credentials:
            # Actualizar credenciales existentes
            existing_credentials.username = username
            existing_credentials.password = password
        else:
            # Crear nuevas credenciales
            new_credentials = DeviceCredentials(
                device_id=device_id,
                username=username,
                password=password
            )
            db.session.add(new_credentials)

        db.session.commit()
        flash(f"Credentials assigned to {device.hostname} successfully!", "success")
        return redirect(url_for('index'))

    return render_template('assign_credentials.html', device=device)

@app.route('/generate_inventory', methods=['GET'])
def generate_inventory():
    devices = Device.query.all()
    inventory = {}
    print(devices)
    for device in devices:
        credentials = DeviceCredentials.query.filter_by(device_id=device.id).first()
        if not credentials:
            flash(f"Device '{device.name}' has no credentials assigned!", "danger")
            continue

        inventory[device.name] = {  # Usa 'name' como clave
            "hostname": device.hostname,
            "platform": device.platform,
            "username": credentials.username,
            "password": credentials.password,
            "port": device.connection_port or 22,
        }

    if not inventory:
        flash("No devices available to generate the inventory.", "warning")
        return redirect(url_for('index'))

    try:
        with open('hosts.yaml', 'w') as f:
            yaml.dump(inventory, f, default_flow_style=False)
        flash("Inventory successfully generated!", "success")
    except Exception as e:
        flash(f"Error generating inventory: {e}", "danger")

    return redirect(url_for('index'))






@app.route('/configure_protocol/<int:device_id>', methods=['GET', 'POST'])
def configure_protocol(device_id):
    device = Device.query.get_or_404(device_id)

    if request.method == 'POST':
        protocol = request.form['protocol']
        config_data = {}

        # Procesar datos según el protocolo
        if protocol == 'RIP':
            config_data['rip_networks'] = request.form.getlist('rip_networks[]')
        elif protocol == 'EIGRP':
            config_data['eigrp_as_number'] = request.form['eigrp_as_number']
            config_data['eigrp_networks'] = request.form.getlist('eigrp_networks[]')
        elif protocol == 'OSPF':
            config_data['process_id'] = request.form['process_id']
            networks = request.form.getlist('ospf_networks[]')
            wildcards = request.form.getlist('ospf_wildcards[]')
            areas = request.form.getlist('ospf_areas[]')

            # Crear lista de diccionarios con la red, wildcard y área
            config_data['ospf_networks'] = [
                {"network": net, "wildcard": wc, "area": area}
                for net, wc, area in zip(networks, wildcards, areas)
            ]
        elif protocol == 'BGP':
            config_data['bgp_as_number'] = request.form['bgp_as_number']
            config_data['bgp_networks'] = request.form.getlist('bgp_networks[]')
        else:
            flash("Invalid protocol selected!", "danger")
            return redirect(url_for('configure_protocol', device_id=device_id))

        # Guardar configuración en la base de datos
        new_protocol = RoutingProtocol(
            device_id=device_id,
            protocol=protocol,
            config_data=config_data
        )
        db.session.add(new_protocol)
        db.session.commit()

        # Aplicar la configuración usando Nornir
        nr = InitNornir(config_file="config.yaml")
        host = nr.inventory.hosts.get(device.name)

        if not host:
            flash(f"Device {device.hostname} not found in inventory. Add it first.", "danger")
            return redirect(url_for('index'))

        # Ejecutar la configuración
        result = nr.run(
            task=assign_protocol,
            protocol=protocol.lower(),
            config=config_data
        )

        # Depuración
        print("Result:")
        print(result)
        print("Host:")
        print(host)
        print("Configuration Data:")
        print(config_data)

        # Mostrar resultados
        for host, task_result in result.items():
            if task_result.failed:
                flash(f"Failed to configure {protocol} on {host}: {task_result.result}", "danger")
            else:
                flash(f"{protocol} configured successfully on {host}.", "success")

        return redirect(url_for('index'))

    return render_template('configure_protocol.html', device=device)



