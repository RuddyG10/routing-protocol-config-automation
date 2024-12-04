from nornir.core.task import Result, Task
from nornir_netmiko.tasks import netmiko_send_config
from jinja2 import Template
import os

def render_template(template_path: str, context: dict) -> str:
    """Carga y renderiza una plantilla Jinja2."""
    with open(template_path, 'r') as template_file:
        template = Template(template_file.read())
    return template.render(context)

def assign_protocol(task: Task, protocol: str, config: dict):
    """
    Configura el protocolo de enrutamiento dinámico usando plantillas Jinja2.
    """
    # Ruta de la plantilla Jinja2
    template_path = f"templates-jinja/{protocol}_template.jinja2"
    if not os.path.exists(template_path):
        return Result(
            host=task.host,
            failed=True,
            result=f"No se encontró la plantilla para {protocol}: {template_path}"
        )

    # Renderizar la plantilla con los parámetros proporcionados
    try:
        rendered_config = render_template(template_path, {protocol: config})
    except Exception as e:
        return Result(
            host=task.host,
            failed=True,
            result=f"Error al renderizar la plantilla: {e}"
        )

    # Aplicar configuración al dispositivo
    try:
        response = task.run(
            task=netmiko_send_config,
            config_commands=rendered_config.splitlines(),
        )
        return Result(
            host=task.host,
            result=response[0].result
        )
    except Exception as e:
        return Result(
            host=task.host,
            failed=True,
            result=f"Error al aplicar la configuración: {e}"
        )

def remove_protocol(task: Task, protocol: str, config: dict = None):
    """
    Elimina la configuración del protocolo en el dispositivo seleccionado.
    """
    try:
        if protocol == "ospf":
            process_id = config.get("process_id")
            if not process_id:
                raise ValueError("No se proporcionó el process_id para eliminar OSPF.")
            remove_commands = [f"no router ospf {process_id}"]

        elif protocol == "eigrp":
            as_number = config.get("as_number")
            if not as_number:
                raise ValueError("No se proporcionó el as_number para eliminar EIGRP.")
            remove_commands = [f"no router eigrp {as_number}"]

        
        elif protocol == "bgp":
            as_number = config.get("as_number")
            if not as_number:
                raise ValueError("No se proporcionó el as_number para eliminar BGP.")
            remove_commands = [f"no router bgp {as_number}"]

        else:
            remove_commands = [f"no router {protocol}"]

        response = task.run(
            task=netmiko_send_config,
            config_commands=remove_commands,
        )
        return Result(
            host=task.host,
            result=response[0].result
        )
    except Exception as e:
        return Result(
            host=task.host,
            failed=True,
            result=f"Error al eliminar la configuración del protocolo {protocol}: {e}"
        )
